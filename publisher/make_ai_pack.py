#!/usr/bin/env python3
"""AI기업집중탐구에 넘길 합본을 textbook/(교과서)으로 다시 만든다. [기업인] 줄·절은 빼고 공통·[AI]만 묶음.
원본: textbook/00~10, 12, 13장 + 부록 A·B + 개정이력(맨 위 '이번에 바뀐 것'). 11장(기업인 게시)은 뺌.
출력: /mnt/project-files/ai-pack/AI기업집중탐구-원고-지침.md (합본은 직접 고치지 않음, 교과서를 고치고 다시 실행)
"""
import datetime, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TB = ROOT / "textbook"
OUT = pathlib.Path("/mnt/project-files/ai-pack/AI기업집중탐구-원고-지침.md")
TEMPLATE = "https://docs.google.com/document/d/1WSuovwgqQjITPS2_eP9HWgWfPhMQhoPCBtzEYzALma8/edit"
CHAPTERS = ["00-시작.md", "01-목표.md", "02-편고르기.md", "03-리서치.md", "04-구성.md", "05-본문.md",
            "06-제목.md", "07-사진.md", "08-문서.md", "09-사용자검토.md", "10-렌더.md",
            "12-개정.md", "13-소통.md", "A-AI계정.md", "B-예외.md"]

HEADER = f"""# AI기업집중탐구 원고 지침 (합본)

> 자동 생성 파일: 직접 고치지 말 것. 원본은 GitHub ybkaudio/company-focus-media 의 textbook/(작업 교과서) 이고, `python3 publisher/make_ai_pack.py`로 다시 만듦. 생성: {{date}}

## 0. 먼저 읽을 것 (5줄)
1. 이 합본은 **작업 교과서**임: 일하는 순서대로 0장(쓰는 법) → 1장 목표 → 2~10장(편 고르기·리서치·구성·본문·제목·사진·문서·사용자 검토·렌더) → 12장 개정 → 13장 소통 → 부록 A(AI 계정 게시·홍보 장·작업 구조) → 부록 B 예외. **일을 시작할 때마다 그 단계의 장을 처음부터 읽고, 장의 '순서'대로 하고, '통과 기준' 칸을 다 채운 뒤 다음 장으로.** 기업집중탐구 쪽 원본과 같아야 하므로 따로 고치지 않음.
2. **기준 원고(템플릿)**: [AI] Anthropic 편 {TEMPLATE} — 사용자가 직접 고친 판. 형식·말투·장 구성이 헷갈리면 이 문서를 그대로 따름. **단, 이 기준 문서는 21장이지만 규칙은 본문 최대 19장 + 끝 고정 홍보 장 1장 = 20장(부록 A-2)**. 기준 문서는 AI 쪽이 본문 19장으로 고칠 예정.
3. 사용자 최신 지시(11/23, 자세히는 ① 6절): 문서 맨 위 `제목:`·`상태:` 줄 없음(사용자 제목은 표지 장 `표지 제목:` 줄) / 장마다 새 페이지 / **모든 장에 사진** / 마무리 장은 로고가 아니라 아직 안 쓴, 가장 의미 있는 실제 사진 / 로고는 표지 장에 표지 사진과 함께.
4. 규칙끼리 부딪치면 줄 끝 날짜가 늦은 쪽. 아래 본문의 "(11/15 카프)" 같은 괄호는 정한 날짜와 예시 편(기업집중탐구 편 이름일 수 있음)임.
5. 사용자 피드백이 규칙이면 합본이 아니라 교과서 원본 한 곳을 고치게 기업집중탐구 쪽에 알림(12장, 이 합본은 다시 생성됨). 새 합본을 받으면 맨 위 '이번에 바뀐 것'을 이미 만든 [AI] 탭에도 반영하고, 반영한 탭을 표로 보고.

## ★ 지금 바로 할 일 (11/23 사용자 지시, 아직 안 끝났으면 이 순서로 실행)
1. 공동 구글 문서(16w0KTBVATdwjiNuUlaoKIVjDcRc0CmgvAKbI2xlIzc0)의 **모든 `[AI]` 탭을 Anthropic 템플릿 형식으로 고침**: 맨 위 `제목:`·`상태:` 줄 삭제, 장마다 새 페이지, 표지 장에 `표지 제목:`(빈칸)·후보 3개·표지 사진·로고, 모든 장 사진+사진 설명, 마무리는 아직 안 쓴 가장 의미 있는 실제 사진, 본문 최대 19장(넘으면 장 합침), 마무리 '지금 팔로우' 버튼 없음, 끝에 ■ 설명란·■ 음악 추천·■ 작성 메모. 방법은 8장(별도 문서 만들지 말고 그 탭을 고침).
2. **사진을 전부 찾아 넣음**(빈 장·"사진 필요" 금지, ③ 7절).
3. 사용자가 손으로 고쳐 둔 탭(예: Google 편)은 사용자 문장·사진을 살린 채 형식만 맞추고, **무엇을 바꿨는지 탭별로 보고**(뺀 줄, 합친 장, 바꾼 사진, 고친 사실).
3-1. **[AI] 탭 전체 사진 점검**(11/23 사용자 "많이 실망", 기업집중탐구에서 나온 실수): ① 다른 시기 인물 사진·장 내용과 무관한 사진으로 '대신' 채운 장 → 그 장 내용과 이어지는 장소·물건·문서 사진으로 교체(7장) ② 사진 설명에 누구인지 안 붙은 이름 → "이름(누구)"로 ③ 설명 없는 사진 → 사진을 보고 써 넣음. 고친 장을 탭별로 보고.
3-2. **[AI] 탭 전체 ■ 음악 추천 다시 고르기**: 8장 음악 추천 기준(인지도 대신 그 편 핵심 장면·감정과 맞는 곡, 뻔한 히트곡 피함)으로 탭마다 다시 고르고 바꾼 곡을 보고. (11/23)
4. 기준 Anthropic 편도 21장 → 본문 19장으로 줄임.
5. 그다음 부록 A 자동 흐름(매일 00:00 원고 대기열 5편·표지 제목 = 최종 합격·02/06/10/14/18/22시 슬롯·Aside 직접 게시)과 부록 A-2 끝 홍보 장을 설정함.
6. 끝나면 사용자에게: 고친 탭 수, 탭별 바뀐 점, 바꾼 사진과 이유, 남은 확인 필요만 짧게.

## 계정 섞임 방지 (게시 전 반드시, 업로드 규칙 맨 앞 줄)
- 이 계정은 **AI기업집중탐구(@aicompany.focus)**. 기업집중탐구(@company.focus)와 다른 계정임. 원고 탭은 `[AI] 회사명`, 해시태그 첫머리는 이 계정 이름 해시태그(8장 설명란 [AI] 줄), 매일 00:00 자동 흐름, 슬롯 02·06·10·14·18·22시, Aside가 instagram.com에 직접 게시(부록 A-1).
- 게시 화면에서 **로그인된 계정 이름을 눈으로 확인**한 뒤에만 누르고, 공유 직전에 한 번 더 확인. 계정이 다르거나 확인이 안 되면 멈추고 사용자에게 넘김.
- 기업집중탐구 쪽 편성표(publisher/schedule.json)·`[기업인]` 탭·@company.focus 게시 루틴을 건드리지 않음. AI 쪽 파일은 저장소 `ai/`.
"""

def keep_ai(md):
    """[기업인] 절(제목에 표시)·줄·줄 안 구간을 뺌."""
    out, drop = [], None
    for line in md.split("\n"):
        h = re.match(r"^(#+) ", line)
        if h:
            lv = len(h.group(1))
            if drop is not None and lv <= drop:
                drop = None
            if drop is None and "[기업인]" in line and "[AI]" not in line:
                drop = lv
                continue
        if drop is not None:
            continue
        if "[기업인]" in line:
            if re.match(r"^\s*[-|]?\s*(\[ \]\s*)?\d*\.?\s*\[기업인\]", line) and "[AI]" not in line:
                continue
            line = re.sub(r"\[기업인\].*?(?=\[AI\])", "", line)      # "[기업인] … [AI] …" → "[AI] …"
            line = re.sub(r"\s*\[기업인\].*$", "", line)              # 줄 끝 [기업인] 구간
        out.append(line)
    return "\n".join(out)


def recent_changes():
    p = TB / "개정이력.md"
    rows = [l for l in p.read_text().split("\n") if l.startswith("- ") and "[기업인]" not in l]
    return "\n".join(rows[:12])


def shift(md, fn):
    md = re.sub(r"^(#+) ", lambda m: "#" + m.group(1) + " ", md, flags=re.M)
    md = re.sub(r"\]\(((?:\d\d|[AB])-[^)]+\.md)\)", r"](#\1)", md)
    md = md.replace("'기업집중탐구'의 점검자", "'AI기업집중탐구'의 점검자").replace("[AI] 줄은 건너뛴다", "[기업인] 줄은 합본에 없다")
    return md


def main():
    out = [HEADER.replace("{date}", datetime.date.today().isoformat()),
           "\n## ★ 이번에 바뀐 것 (교과서 개정 이력, 최신이 위 — 이미 만든 [AI] 탭에도 반영)\n" + recent_changes() + "\n"]
    for fn in CHAPTERS:
        p = TB / fn
        if not p.exists():
            sys.exit(f"원본 없음: {p}")
        out.append(f"\n---\n\n<!-- 원본 textbook/{fn} -->\n" + shift(keep_ai(p.read_text()), fn))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(out)
    if "[기업인]" in text.replace("`[기업인]`", ""):
        print("주의: [기업인] 표시가 남음", file=sys.stderr)
    OUT.write_text(text)
    print(OUT, len(text), "자")

if __name__ == "__main__":
    main()
