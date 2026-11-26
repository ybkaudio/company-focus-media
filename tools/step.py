#!/usr/bin/env python3
"""편마다 진행표(episodes/<stem>.steps.json): 지금 단계 · 읽을 교과서 장 · 통과 기준 체크 칸.
검사 명령을 못 넘거나 체크 칸 수를 확인하지 않으면 다음 단계로 못 감. (textbook/00-시작.md 0-1)

  step.py start <stem> "인물 · 회사" [--account kiupin|ai]   # 2장 끝 = 진행표 생성, 3단계부터
  step.py show <stem>                                        # 지금 단계 · 읽을 장 · 체크 칸
  step.py done <stem> <단계> --checked <체크 칸 수>           # 검사 실행 + 다음 단계로
  step.py posted <stem>                                      # 게시됨
  step.py list [--from N]                                    # 전체 진행표 (12장 4번: 진행 중인 편 점검)
  step.py sync                                               # schedule.json 기준으로 렌더·게시된 편 진행표 맞추기
"""
import datetime, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TB = ROOT / "textbook"
EP = ROOT / "episodes"
KST = datetime.timezone(datetime.timedelta(hours=9))

STEPS = {  # 단계: (이름, 교과서 장 파일)
    2: ("편 고르기", "02-편고르기.md"),
    3: ("리서치", "03-리서치.md"),
    4: ("구성", "04-구성.md"),
    5: ("본문", "05-본문.md"),
    6: ("제목", "06-제목.md"),
    7: ("사진", "07-사진.md"),
    8: ("문서 올리기", "08-문서.md"),
    9: ("사용자 검토 (표지 제목 = 합격)", "09-사용자검토.md"),
    10: ("렌더·최종 점검", "10-렌더.md"),
    11: ("대기열·게시", "11-게시.md"),
}
LAST = 11


def now():
    return datetime.datetime.now(KST).strftime("%Y-%m-%d %H:%M")


def path(stem):
    return EP / f"{stem}.steps.json"


def load(stem):
    p = path(stem)
    if not p.exists():
        sys.exit(f"진행표 없음: {p}\n먼저 `step.py start {stem} \"인물 · 회사\"` (교과서 2장)")
    return json.loads(p.read_text())


def save(d):
    path(d["stem"]).write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")


def checklist(n, account):
    """그 장 '## 통과 기준'의 - [ ] 줄. 다른 계정 표시 줄은 뺌."""
    text = (TB / STEPS[n][1]).read_text()
    m = re.search(r"^## 통과 기준[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    items = re.findall(r"^- \[ \] (.+)$", m.group(1), re.M) if m else []
    skip = "[AI]" if account == "kiupin" else "[기업인]"
    return [i for i in items if skip not in i]


def gate(n, d):
    """기계 검사. 걸리면 이유 목록."""
    stem, bad = d["stem"], []
    ep = EP / f"{stem}.json"
    if n in (8, 10):
        if not ep.exists():
            bad.append(f"{ep.relative_to(ROOT)} 없음")
        else:
            r = subprocess.run([sys.executable, str(ROOT / "render.py"), "--check", str(ep)],
                               capture_output=True, text=True, cwd=ROOT)
            if r.returncode != 0:
                bad.append("render.py --check 걸림:\n" + (r.stdout + r.stderr).strip())
    if n == 3 and not (ROOT / "plans" / f"{stem}-research.md").exists():
        bad.append(f"plans/{stem}-research.md 없음 (3장 통과 기준)")
    if n == 4 and not (ROOT / "plans" / f"{stem}.md").exists():
        bad.append(f"plans/{stem}.md 없음 (4장 넘기는 것)")
    if n == 10 and not list((ROOT / "posts").glob(f"{stem}*-final")) and not list((ROOT / "posts").glob(f"{stem}-final")):
        bad.append(f"posts/{stem}-final 없음 (export.py)")
    if n == 11:
        sched = json.loads((ROOT / "publisher" / "schedule.json").read_text())
        if not any(stem in (it.get("folder") or "") for it in sched):
            bad.append("publisher/schedule.json에 없음 (sched.py slot)")
    return bad


def show(d):
    st = d["step"]
    print(f"■ {d['stem']} · {d.get('title','')} · 계정 {d['account']}")
    if st == "posted":
        print("게시됨. 더 할 단계 없음.")
        return
    name, ch = STEPS[st]
    print(f"지금 단계: {st}. {name}")
    print(f"먼저 읽을 장: textbook/{ch} (처음부터 끝까지, 기억으로 대신하지 않음)")
    items = checklist(st, d["account"])
    print(f"통과 기준 {len(items)}칸:")
    for i in items:
        print(f"  [ ] {i}")
    print(f"다 채우면: python3 tools/step.py done {d['stem']} {st} --checked {len(items)}")
    if d.get("history"):
        h = d["history"][-1]
        print(f"(지난 단계: {h['step']} {h['done_at']})")


def main(a):
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return
    cmd = a[0]
    if cmd == "start":
        stem, title = a[1], a[2] if len(a) > 2 else ""
        account = a[a.index("--account") + 1] if "--account" in a else "kiupin"
        if path(stem).exists():
            sys.exit(f"이미 있음: {path(stem)} → step.py show {stem}")
        d = {"stem": stem, "title": title, "account": account, "step": 3,
             "history": [{"step": 2, "done_at": now()}]}
        save(d)
        show(d)
    elif cmd == "show":
        show(load(a[1]))
    elif cmd == "done":
        d, n = load(a[1]), int(a[2])
        if d["step"] != n:
            sys.exit(f"지금 단계는 {d['step']}임. {n}단계를 끝낼 수 없음 → step.py show {a[1]}")
        items = checklist(n, d["account"])
        got = int(a[a.index("--checked") + 1]) if "--checked" in a else -1
        if got != len(items):
            print(f"{n}장 통과 기준 {len(items)}칸을 하나씩 확인하고 --checked {len(items)}로 다시:")
            for i in items:
                print(f"  [ ] {i}")
            sys.exit(1)
        bad = gate(n, d)
        if bad:
            sys.exit(f"{n}단계 검사에 걸림. 고치고 다시:\n- " + "\n- ".join(bad))
        d["history"].append({"step": n, "done_at": now(), "checked": len(items)})
        if n < LAST:
            d["step"] = n + 1
        else:  # 11단계 유지 = 게시 대기
            d["waiting_post"] = True
            print("대기열에 들어감. 게시되면 step.py posted")
        save(d)
        show(d)
    elif cmd == "posted":
        d = load(a[1])
        d["step"] = "posted"
        d["history"].append({"step": "posted", "done_at": now()})
        save(d)
        print(f"{a[1]} 게시됨")
    elif cmd == "list":
        frm = int(a[a.index("--from") + 1]) if "--from" in a else 0
        for p in sorted(EP.glob("*.steps.json")):
            d = json.loads(p.read_text())
            st = d["step"]
            if st == "posted" or (isinstance(st, int) and st < frm):
                continue
            label = "게시 대기" if d.get("waiting_post") else STEPS[st][0]
            print(f"{d['stem']:<32} {st:>2}. {label:<22} {d.get('title','')}")
    elif cmd == "sync":
        sched = json.loads((ROOT / "publisher" / "schedule.json").read_text())
        n = 0
        for it in sched:
            m = re.match(r"posts/(.+?)-final$", it.get("folder") or "")
            if not m:
                continue
            stem = m.group(1)
            if path(stem).exists():
                d = json.loads(path(stem).read_text())
            else:
                d = {"stem": stem, "title": re.sub(r"^#\d+\s*", "", it.get("episode", "")),
                     "account": "kiupin", "history": [{"step": "sync", "done_at": now()}]}
            if it.get("posted"):
                d["step"] = "posted"
            elif d.get("step") != "posted":
                d["step"], d["waiting_post"] = LAST, True
            save(d)
            n += 1
        print(f"{n}편 진행표 맞춤")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
