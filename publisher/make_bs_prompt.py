#!/usr/bin/env python3
"""Aside 게시 루틴 프롬프트 만들기 (rules/3-upload.md의 PROMPT 틀 그대로).
  python3 publisher/make_bs_prompt.py
결과: 화면 출력 + out/aside-post-routine.txt (+ /mnt/project-files/production/aside-post-routine.md, 있으면)
루틴은 매번 schedule.json을 새로 읽으므로 편성표가 바뀌어도 다시 만들 필요 없음. 틀이 바뀔 때만 실행.
(11/23 Business Suite는 인스타 캐러셀 10장 제한이라 instagram.com 직접 게시로 돌아감. 파일 이름은 그대로 둠.)"""
import datetime as dt, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KST = dt.timezone(dt.timedelta(hours=9))


def main():
    rules = open(os.path.join(ROOT, "rules/3-upload.md"), encoding="utf-8").read()
    m = re.search(r"<!-- PROMPT START -->\n(.*?)<!-- PROMPT END -->", rules, re.S)
    if not m:
        sys.exit("rules/3-upload.md에 PROMPT START/END 틀이 없음")
    prompt = m.group(1).strip()
    now = dt.datetime.now(KST)
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    open(os.path.join(ROOT, "out/aside-post-routine.txt"), "w", encoding="utf-8").write(prompt + "\n")
    shared = "/mnt/project-files/production"
    if os.path.isdir(shared):
        open(os.path.join(shared, "aside-post-routine.md"), "w", encoding="utf-8").write(
            f"# Aside 게시 루틴 (기업집중탐구, {now:%m/%d %H:%M} KST 생성, rules/3-upload.md 틀)\n\n"
            "- 시작 링크: https://www.instagram.com/\n"
            "- 실행: 매일 00:05·04:05·08:05·12:05·16:05·20:05 KST (각 슬롯 5분 뒤).\n"
            "- 먼저 Aside의 Business Suite 예약 루틴(23·03·07·11·15·19시)을 끄고, 아래 전체를 Aside에 붙여 넣음.\n"
            "- 결과는 Notion '인스타 게시 기록'에 남음.\n\n```\n" + prompt + "\n```\n")
    print(prompt)


if __name__ == "__main__":
    main()
