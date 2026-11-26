#!/usr/bin/env python3
"""Aside 게시 프롬프트(한 번 넣으면 한 편) 만들기 (textbook/11-게시.md의 PROMPT 틀 그대로).
  python3 publisher/make_bs_prompt.py
결과: 화면 출력 + out/aside-post-one.txt (+ /mnt/project-files/production/aside-post-one.md, 있으면)
루틴은 매번 schedule.json을 새로 읽으므로 편성표가 바뀌어도 다시 만들 필요 없음. 틀이 바뀔 때만 실행.
(11/23 Business Suite는 인스타 캐러셀 10장 제한이라 instagram.com 직접 게시로 돌아감. 파일 이름은 그대로 둠.)"""
import datetime as dt, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KST = dt.timezone(dt.timedelta(hours=9))


def main():
    rules = open(os.path.join(ROOT, "textbook/11-게시.md"), encoding="utf-8").read()
    m = re.search(r"<!-- PROMPT START -->\n(.*?)<!-- PROMPT END -->", rules, re.S)
    if not m:
        sys.exit("textbook/11-게시.md에 PROMPT START/END 틀이 없음")
    prompt = m.group(1).strip()
    now = dt.datetime.now(KST)
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    open(os.path.join(ROOT, "out/aside-post-one.txt"), "w", encoding="utf-8").write(prompt + "\n")
    shared = "/mnt/project-files/production"
    if os.path.isdir(shared):
        open(os.path.join(shared, "aside-post-one.md"), "w", encoding="utf-8").write(
            f"# Aside 게시 프롬프트: 붙여 넣을 때마다 다음 편 1편 게시 (기업집중탐구, {now:%m/%d %H:%M} KST 생성, textbook/11-게시.md 틀)\n\n"
            "- 시작 링크: https://www.instagram.com/ (맥북 Aside에서 이 페이지를 열고 아래 전체를 붙여 넣음)\n"
            "- 아무 때나 한 번 넣으면 대기열 맨 앞의 안 올라간 편 1편이 올라감. 대기열 보기: https://github.com/ybkaudio/company-focus-media/blob/main/publisher/upcoming.txt\n"
            "- 로그인·2단계 인증 화면이 나오면 Aside가 멈추고 넘겨 줌. 직접 로그인한 뒤 다시 붙여 넣으면 됨.\n"
            "- 데스크탑 Aside의 예전 정시 루틴(00:05·04:05…)은 꺼 두기.\n"
            "- 결과는 Notion '인스타 게시 기록'에 남음.\n\n```\n" + prompt + "\n```\n")
    print(prompt)


if __name__ == "__main__":
    main()
