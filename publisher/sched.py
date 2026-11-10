#!/usr/bin/env python3
"""schedule.json 관리. 렌더·내보내기(posts/NN-final) 뒤에 실행.
  python3 publisher/sched.py add 10-youtube 2026-11-11T08:00 "#10 YouTube"   # 추가·시각 변경
  python3 publisher/sched.py remove 10-youtube                               # 빼기
  python3 publisher/sched.py refresh                                         # count·first_line·music 다시 채움
시각은 한국 시간(KST)."""
import glob, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "publisher", "schedule.json")

def fill(i):
    slug = i["folder"].split("/")[1][:-6]
    f = os.path.join(ROOT, i["folder"])
    if not os.path.isdir(f):   # 아직 렌더 전인 예약 자리: count 0이면 Aside가 이미지 수 불일치로 안 올림
        i.setdefault("count", 0); i.setdefault("first_line", ""); i.setdefault("music", "")
        return i
    i["count"] = len(glob.glob(f + "/[0-9][0-9].jpg"))
    i["first_line"] = open(f + "/caption.txt", encoding="utf-8").read().strip().splitlines()[0].strip()
    ep = json.load(open(os.path.join(ROOT, "episodes", slug + ".json"), encoding="utf-8"))
    i["music"] = ep.get("music") or ""
    return i

s = json.load(open(P, encoding="utf-8"))
cmd = sys.argv[1]
if cmd == "add":
    slug, at, name = sys.argv[2], sys.argv[3], sys.argv[4]
    s = [i for i in s if i["folder"] != f"posts/{slug}-final"]
    s.append({"at": at + ":00+09:00", "folder": f"posts/{slug}-final", "episode": name})
elif cmd == "remove":
    s = [i for i in s if i["folder"] != f"posts/{sys.argv[2]}-final"]
s = sorted((fill(i) for i in s), key=lambda i: i["at"])
json.dump(s, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for i in s:
    print(i["at"][5:16], i["episode"], i["count"], "장 |", i["music"][:40])
