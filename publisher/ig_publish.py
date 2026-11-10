#!/usr/bin/env python3
"""Instagram 캐러셀 직접 게시 (Instagram API with Instagram Login).

publisher/schedule.json 의 각 항목 중 게시 시각이 지났고 아직 안 올라간 편을 올린다.
- 이미지: 이 저장소 커밋에 고정한 raw.githubusercontent URL (공개 저장소)
- 캡션: <folder>/caption.txt
- 상태: publisher/published.json (게시 id·주소). 워크플로가 커밋한다.
- 중복 방지: 최근 게시물 캡션 첫 줄과 같으면 건너뛴다(사용자가 수동으로 이미 올린 경우 포함).
- 늦은 편: 예정 시각보다 MAX_LATE_HOURS 넘게 지나면 올리지 않고 기록만 남긴다.

환경 변수: IG_TOKEN(필수), IG_USER_ID(선택), GITHUB_SHA, GITHUB_REPOSITORY, DRY_RUN=1, ONLY=<folder>
"""
import datetime as dt
import glob
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://graph.instagram.com/v23.0"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEDULE = os.path.join(ROOT, "publisher", "schedule.json")
STATE = os.path.join(ROOT, "publisher", "published.json")
MAX_LATE_HOURS = 3
MAX_ITEMS = 20


def call(method, path, **params):
    params["access_token"] = os.environ["IG_TOKEN"]
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}"
    if method == "GET":
        req = urllib.request.Request(url + "?" + data.decode())
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"{method} {path} -> {e.code}: {body}") from None


def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def first_line(text):
    return (text or "").strip().splitlines()[0].strip() if (text or "").strip() else ""


def wait_ready(cid, label):
    for _ in range(30):
        st = call("GET", cid, fields="status_code").get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"{label} 컨테이너 상태 {st} ({cid})")
        time.sleep(5)
    raise RuntimeError(f"{label} 컨테이너가 준비되지 않음 ({cid})")


def publish(item, user_id, sha, repo, dry):
    folder = item["folder"].rstrip("/")
    imgs = sorted(glob.glob(os.path.join(ROOT, folder, "[0-9][0-9].jpg")))
    if not 2 <= len(imgs) <= MAX_ITEMS:
        raise RuntimeError(f"{folder}: 이미지 {len(imgs)}장 (2~{MAX_ITEMS}장만 가능)")
    with open(os.path.join(ROOT, folder, "caption.txt"), encoding="utf-8") as f:
        caption = f.read().rstrip("\n")
    if len(caption) > 2200:
        raise RuntimeError(f"{folder}: 캡션 {len(caption)}자 (2200자 초과)")
    urls = [f"https://raw.githubusercontent.com/{repo}/{sha}/{folder}/{os.path.basename(p)}" for p in imgs]
    print(f"[{folder}] {len(urls)}장, 캡션 {len(caption)}자, 첫 줄: {first_line(caption)}")
    if dry:
        for u in urls:
            req = urllib.request.Request(u, method="HEAD")
            with urllib.request.urlopen(req, timeout=30) as r:
                ct = r.headers.get("content-type")
                if r.status != 200 or ct != "image/jpeg":
                    raise RuntimeError(f"이미지 주소 확인 실패 {u} ({r.status} {ct})")
        print("  DRY_RUN: 이미지 주소 모두 200 image/jpeg, 게시는 하지 않음")
        return None
    children = []
    for i, u in enumerate(urls, 1):
        cid = call("POST", f"{user_id}/media", image_url=u, is_carousel_item="true")["id"]
        children.append(cid)
        print(f"  장 {i:02d} 컨테이너 {cid}")
    for i, cid in enumerate(children, 1):
        wait_ready(cid, f"장 {i:02d}")
    car = call("POST", f"{user_id}/media", media_type="CAROUSEL", children=",".join(children), caption=caption)["id"]
    wait_ready(car, "캐러셀")
    media_id = call("POST", f"{user_id}/media_publish", creation_id=car)["id"]
    link = call("GET", media_id, fields="permalink").get("permalink")
    print(f"  게시 완료 {media_id} {link}")
    return {"media_id": media_id, "permalink": link}


def main():
    dry = os.environ.get("DRY_RUN") == "1"
    only = os.environ.get("ONLY", "").rstrip("/")
    sha = os.environ.get("GITHUB_SHA") or os.popen(f"git -C {ROOT} rev-parse HEAD").read().strip()
    repo = os.environ.get("GITHUB_REPOSITORY", "ybkaudio/company-focus-media")
    schedule = load(SCHEDULE, [])
    state = load(STATE, {})
    now = dt.datetime.now(dt.timezone.utc)

    me = call("GET", "me", fields="user_id,username")
    user_id = os.environ.get("IG_USER_ID") or me["user_id"]
    print(f"계정 @{me.get('username')} ({user_id}), 커밋 {sha[:7]}, {'점검' if dry else '게시'} 모드")
    recent = call("GET", f"{user_id}/media", fields="caption,timestamp,permalink", limit="15").get("data", [])
    recent_first = {first_line(m.get("caption")): m for m in recent if m.get("caption")}

    changed = False
    failed = False
    for item in schedule:
        folder = item["folder"].rstrip("/")
        if only and folder != only:
            continue
        if folder in state and state[folder].get("status") in ("published", "skipped"):
            continue
        at = dt.datetime.fromisoformat(item["at"])
        if not dry and not only and at > now:
            continue
        late = (now - at).total_seconds() / 3600
        try:
            with open(os.path.join(ROOT, folder, "caption.txt"), encoding="utf-8") as f:
                fl = first_line(f.read())
            if fl in recent_first:
                m = recent_first[fl]
                print(f"[{folder}] 이미 올라가 있음 ({m.get('permalink')}), 건너뜀")
                if not dry:
                    state[folder] = {"status": "published", "permalink": m.get("permalink"), "note": "이미 게시돼 있어 건너뜀", "at": item["at"]}
                    changed = True
                continue
            if not dry and not only and late > MAX_LATE_HOURS:
                print(f"[{folder}] 예정보다 {late:.1f}시간 늦어 올리지 않음")
                state[folder] = {"status": "skipped", "note": f"{late:.1f}시간 지연", "at": item["at"]}
                changed = True
                continue
            res = publish(item, user_id, sha, repo, dry)
            if res:
                state[folder] = {"status": "published", **res, "at": item["at"],
                                 "published_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
                changed = True
                with open(STATE, "w", encoding="utf-8") as f:
                    json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:  # 한 편이 실패해도 다음 편은 시도
            failed = True
            print(f"[{folder}] 실패: {e}", file=sys.stderr)
            if not dry:
                state[folder] = {**state.get(folder, {}), "status": "error", "error": str(e)[:500], "at": item["at"]}
                changed = True
    if changed:
        with open(STATE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
