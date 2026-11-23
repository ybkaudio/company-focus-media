#!/usr/bin/env python3
"""schedule.json 관리. 렌더·내보내기(posts/NN-final) 뒤에 실행.
  python3 publisher/sched.py add 10-youtube 2026-11-11T08:00 "#10 YouTube"   # 추가·시각 변경
  python3 publisher/sched.py remove 10-youtube                               # 빼기
  python3 publisher/sched.py refresh                                         # count·first_line·music 다시 채움
  python3 publisher/sched.py slot 46-xxx "인물 · 회사"                         # 비어 있는 가장 빠른 슬롯에 넣기(렌더 직후)
시각은 한국 시간(KST). 실행할 때마다 publisher/upcoming.txt(Aside 루틴이 읽는 앞으로 올라갈 편 목록)도 다시 씀."""
import glob, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "publisher", "schedule.json")

def fill(i):
    slug = i["folder"].split("/")[1][:-6]
    f = os.path.join(ROOT, i["folder"])
    if not os.path.isdir(f):   # 아직 렌더 전인 예약 자리: count 0이면 Aside가 이미지 수 불일치로 안 올림
        i.setdefault("count", 0); i.setdefault("first_line", ""); i.setdefault("music", ""); i.setdefault("comment", "")
        return i
    i["count"] = len(glob.glob(f + "/[0-9][0-9].jpg"))
    import datetime
    posted = datetime.datetime.fromisoformat(i["at"]) <= datetime.datetime.now(datetime.timezone.utc)
    if not (posted and i.get("first_line")):   # 이미 게시 시각이 지난 편은 first_line을 바꾸지 않음(중복 게시 확인용, 11/11)
        i["first_line"] = open(f + "/caption.txt", encoding="utf-8").read().strip().splitlines()[0].strip()
    ep = json.load(open(os.path.join(ROOT, "episodes", slug + ".json"), encoding="utf-8"))
    i["music"] = ep.get("music") or ""
    c = f + "/comment.txt"   # 게시 직후 우리 계정이 다는 첫 댓글 (11/11)
    i["comment"] = open(c, encoding="utf-8").read().strip() if os.path.exists(c) else ""
    pl = f + "/poll.txt"   # 첫 댓글에 붙일 투표 선택지(줄마다 하나, 없으면 칸 없음)
    if os.path.exists(pl):
        i["poll"] = [x.strip() for x in open(pl, encoding="utf-8").read().splitlines() if x.strip()]
    else:
        i.pop("poll", None)
    return i

s = json.load(open(P, encoding="utf-8"))
cmd = sys.argv[1]
if cmd == "add":
    slug, at, name = sys.argv[2], sys.argv[3], sys.argv[4]
    s = [i for i in s if i["folder"] != f"posts/{slug}-final"]
    s.append({"at": at + ":00+09:00", "folder": f"posts/{slug}-final", "episode": name})
elif cmd == "slot":
    # 슬롯 00·04·08·12·16·20시 KST(rules/3-upload.md). Aside 게시 루틴이 각 슬롯 5분 뒤 schedule.json을 읽으므로
    # 지금부터 LEAD 뒤 이후의, 아무 편도 없는 가장 빠른 슬롯.
    import datetime as dt
    KST = dt.timezone(dt.timedelta(hours=9)); SLOTS = (0, 4, 8, 12, 16, 20); LEAD = dt.timedelta(minutes=10)
    slug, name = sys.argv[2], sys.argv[3]
    s = [i for i in s if i["folder"] != f"posts/{slug}-final"]
    used = {dt.datetime.fromisoformat(i["at"]) for i in s}
    t = dt.datetime.now(KST) + LEAD
    c = t.replace(minute=0, second=0, microsecond=0)
    while c < t or c.hour not in SLOTS or c in used:
        c += dt.timedelta(hours=1)
    s.append({"at": c.strftime("%Y-%m-%dT%H:%M:%S+09:00"), "folder": f"posts/{slug}-final", "episode": name})
    print("슬롯:", c.strftime("%m/%d %H:%M KST"), name)
elif cmd == "remove":
    s = [i for i in s if i["folder"] != f"posts/{sys.argv[2]}-final"]
s = sorted((fill(i) for i in s), key=lambda i: i["at"])
json.dump(s, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for i in s:
    print(i["at"][5:16], i["episode"], i["count"], "장 |", i["music"][:40])

# Aside 루틴용 목록: 아직 게시 시각이 안 된 편(한 줄에 한 편, 시각순)
import datetime as _dt
_now = _dt.datetime.now(_dt.timezone.utc)
rows = [f"{i['at'][:10]} {i['at'][11:16]} KST | 폴더 {i['folder']} | {i['count']}장 | 첫 줄: \"{i['first_line']}\" | {i['episode']}"
        for i in s if _dt.datetime.fromisoformat(i["at"]) > _now and i.get("count")]
open(os.path.join(ROOT, "publisher", "upcoming.txt"), "w", encoding="utf-8").write(
    "# 앞으로 올라갈 기업집중탐구 편 (sched.py가 자동으로 씀, 손으로 고치지 않음)\n" + "\n".join(rows) + "\n")
