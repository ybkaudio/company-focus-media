#!/usr/bin/env python3
"""schedule.json 관리. 렌더·내보내기(posts/NN-final) 뒤에 실행.
  python3 publisher/sched.py add 10-youtube 2026-11-11T08:00 "#10 YouTube"   # 추가·시각 변경
  python3 publisher/sched.py remove 10-youtube                               # 빼기
  python3 publisher/sched.py refresh                                         # count·first_line·music 다시 채움
  python3 publisher/sched.py slot 46-xxx "인물 · 회사"                         # 대기열 맨 뒤에 넣기(렌더 직후)
  python3 publisher/sched.py posted 27b-palantir-karp                         # 게시됨 표시(Notion '완료'·'이미 게시됨' 확인 후)
11/25부터 at은 게시 시각이 아니라 대기열 순서(사용자가 맥북 Aside에 프롬프트를 넣을 때마다 맨 앞 미게시 편 1편이 올라감).
실행할 때마다 publisher/upcoming.txt(아직 안 올라간 편, 순서대로)도 다시 씀."""
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
    if not (i.get("posted") and i.get("first_line")):   # 이미 올라간 편은 first_line을 바꾸지 않음(중복 게시 확인용, 11/11)
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
    # 11/25 사용자: 정시 슬롯 폐지, 순서 대기열. 맨 뒤 편 at + 4시간(순서용 값, 게시 시각 아님)
    import datetime as dt
    KST = dt.timezone(dt.timedelta(hours=9))
    slug, name = sys.argv[2], sys.argv[3]
    s = [i for i in s if i["folder"] != f"posts/{slug}-final"]
    last = max([dt.datetime.fromisoformat(i["at"]) for i in s] + [dt.datetime.now(KST).replace(minute=0, second=0, microsecond=0)])
    c = (last + dt.timedelta(hours=4)).astimezone(KST)
    s.append({"at": c.strftime("%Y-%m-%dT%H:%M:%S+09:00"), "folder": f"posts/{slug}-final", "episode": name})
    print("대기열 맨 뒤:", name)
elif cmd == "posted":
    for i in s:
        if i["folder"] == f"posts/{sys.argv[2]}-final":
            i["posted"] = True
elif cmd == "remove":
    s = [i for i in s if i["folder"] != f"posts/{sys.argv[2]}-final"]
s = sorted((fill(i) for i in s), key=lambda i: i["at"])
json.dump(s, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for i in s:
    print(i["at"][5:16], i["episode"], i["count"], "장 |", i["music"][:40])

# 사용자용 대기열: 아직 안 올라간 편(posted 없음), 순서대로
rows = [f"{n}. 폴더 {i['folder']} | {i['count']}장 | 첫 줄: \"{i['first_line']}\" | {i['episode']}"
        for n, i in enumerate((i for i in s if not i.get("posted") and i.get("count")), 1)]
open(os.path.join(ROOT, "publisher", "upcoming.txt"), "w", encoding="utf-8").write(
    "# 아직 안 올라간 기업집중탐구 편, 올라갈 순서 (sched.py가 자동으로 씀, 손으로 고치지 않음)\n"
    "# 맥북 Aside에 게시 프롬프트를 한 번 넣을 때마다 맨 위 1편이 올라감\n" + "\n".join(rows) + "\n")
