#!/usr/bin/env python3
"""Business Suite 예약용 Aside 프롬프트 만들기 (rules/3-upload.md 틀 + schedule.json).
  python3 publisher/make_bs_prompt.py            # 지금부터 1시간 뒤 이후 편 전부
  python3 publisher/make_bs_prompt.py --days 7   # 앞으로 7일 안의 편만
결과: 화면 출력 + out/business-suite-prompt.txt (+ /mnt/project-files/production/business-suite-prompt.md, 있으면)
규칙이 바뀌면 이 파일이 아니라 rules/3-upload.md의 PROMPT 틀만 고친다."""
import datetime as dt, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KST = dt.timezone(dt.timedelta(hours=9))


def main():
    days = None
    if "--days" in sys.argv:
        days = int(sys.argv[sys.argv.index("--days") + 1])
    rules = open(os.path.join(ROOT, "rules/3-upload.md"), encoding="utf-8").read()
    m = re.search(r"<!-- PROMPT START -->\n(.*?)<!-- PROMPT END -->", rules, re.S)
    if not m:
        sys.exit("rules/3-upload.md에 PROMPT START/END 틀이 없음")
    tpl = m.group(1).strip()
    sched = json.load(open(os.path.join(ROOT, "publisher/schedule.json"), encoding="utf-8"))
    now = dt.datetime.now(KST)
    lo = now + dt.timedelta(hours=1)
    hi = now + dt.timedelta(days=days) if days else None
    rows = []
    for it in sorted(sched, key=lambda x: x["at"]):
        at = dt.datetime.fromisoformat(it["at"])
        if at < lo or (hi and at > hi):
            continue
        folder = it["folder"]
        n = len([f for f in os.listdir(os.path.join(ROOT, folder)) if re.fullmatch(r"\d\d\.jpg", f)]) if os.path.isdir(os.path.join(ROOT, folder)) else None
        if n is not None and n != it["count"]:
            sys.exit(f"{folder}: 이미지 {n}장인데 편성표 count {it['count']} → 편성표나 내보내기부터 고칠 것")
        music = it.get("music", "").split(" / ")[0]
        rows.append(f"   - {at:%m/%d %H:%M} | 폴더 {folder} | {it['count']}장 | 첫 줄: \"{it['first_line']}\" | 음악(기록만): {music}")
    if not rows:
        sys.exit("예약할 편이 없음(편성표에 앞으로 올라갈 편 없음)")
    prompt = tpl.replace("{EPISODES}", "\n".join(rows))
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    open(os.path.join(ROOT, "out/business-suite-prompt.txt"), "w", encoding="utf-8").write(prompt + "\n")
    shared = "/mnt/project-files/production"
    if os.path.isdir(shared):
        open(os.path.join(shared, "business-suite-prompt.md"), "w", encoding="utf-8").write(
            f"# Business Suite 예약 프롬프트 ({now:%m/%d %H:%M} KST 생성, rules/3-upload.md 틀)\n\n"
            "시작 링크: https://business.facebook.com/latest/content_calendar\n"
            "아래 전체를 Aside에 붙여 넣고, 끝나면 Aside 결과 표를 제작·게시 스레드에 붙여 주세요.\n\n```\n" + prompt + "\n```\n")
    print(prompt)


if __name__ == "__main__":
    main()
