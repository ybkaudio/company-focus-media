#!/usr/bin/env python3
"""AI기업집중탐구에 넘길 원고 지침 합본을 rules/ 원본으로 다시 만든다.
원본: rules/1-wongo-common.md, 1-wongo-ai.md, 6-ai-process.md, 7-ai-structure-check.md, 8-ai-upload.md, 9-ai-promo.md (+ 아래 머리말·점검 블록)
출력: /mnt/project-files/ai-pack/AI기업집중탐구-원고-지침.md (합본은 직접 고치지 않음, 원본을 고치고 다시 실행)
"""
import datetime, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RULES = ROOT / "rules"
OUT = pathlib.Path("/mnt/project-files/ai-pack/AI기업집중탐구-원고-지침.md")
TEMPLATE = "https://docs.google.com/document/d/1WSuovwgqQjITPS2_eP9HWgWfPhMQhoPCBtzEYzALma8/edit"
PARTS = [("1-wongo-common.md", "① 원고 규칙 (두 계정 공통)"),
         ("1-wongo-ai.md", "② AI기업집중탐구만의 차이"),
         ("6-ai-process.md", "③ 제작 과정 (순서·도구)")]
TAIL = [("7-ai-structure-check.md", "⑤ 작업 구조 점검 (한 번 실행)"),
        ("8-ai-upload.md", "⑥ 자동 흐름·업로드 + Aside 게시 루틴 프롬프트"),
        ("9-ai-promo.md", "⑦ 끝 홍보 장·마무리 버튼·장 수")]

HEADER = f"""# AI기업집중탐구 원고 지침 (합본)

> 자동 생성 파일: 직접 고치지 말 것. 원본은 GitHub ybkaudio/company-focus-media 의 rules/ 이고, `python3 publisher/make_ai_pack.py`로 다시 만듦. 생성: {{date}}

## 0. 먼저 읽을 것 (5줄)
1. 이 합본 하나로 AI기업집중탐구 원고를 처음부터 끝까지 만들 수 있게 묶었음. 순서: ① 공통 규칙 → ② AI 차이 → ③ 제작 과정 → ④ 별도 점검 → ⑤ 작업 구조 점검(처음 한 번) → ⑥ 자동 흐름·업로드(Aside 게시 루틴 부록) → ⑦ 끝 홍보 장. ①은 기업집중탐구 쪽 원본과 같아야 하므로 따로 고치지 않음.
2. **기준 원고(템플릿)**: [AI] Anthropic 편 {TEMPLATE} — 사용자가 직접 고친 판. 형식·말투·장 구성이 헷갈리면 이 문서를 그대로 따름. **단, 이 기준 문서는 21장이지만 규칙은 본문 최대 19장 + 끝 고정 홍보 장 1장 = 20장(⑦)**. 기준 문서는 AI 쪽이 본문 19장으로 고칠 예정.
3. 사용자 최신 지시(11/23, 자세히는 ① 6절): 문서 맨 위 `제목:`·`상태:` 줄 없음(사용자 제목은 표지 장 `표지 제목:` 줄) / 장마다 새 페이지 / **모든 장에 사진** / 마무리 장은 로고가 아니라 아직 안 쓴, 가장 의미 있는 실제 사진 / 로고는 표지 장에 표지 사진과 함께.
4. 규칙끼리 부딪치면 줄 끝 날짜가 늦은 쪽. 아래 본문의 "(11/15 카프)" 같은 괄호는 정한 날짜와 예시 편(기업집중탐구 편 이름일 수 있음)임.
5. 사용자 피드백이 규칙이면 합본이 아니라 rules/ 원본 한 곳을 고치게 기업집중탐구 쪽에 알림(이 합본은 다시 생성됨).

## 계정 섞임 방지 (게시 전 반드시, 업로드 규칙 맨 앞 줄)
- 이 계정은 **AI기업집중탐구(@aicompany.focus)**. 기업집중탐구(@company.focus)와 다른 계정임. 원고 탭은 `[AI] 회사명`, 해시태그 첫머리는 이 계정 이름 해시태그(①의 '#기업집중탐구 먼저'는 AI 쪽에선 자기 계정 해시태그로 읽음, 기준 원고 설명란 참고), 매일 00:00 자동 흐름, 슬롯 02·06·10·14·18·22시, Aside가 instagram.com에 직접 게시(⑥).
- 게시 화면에서 **로그인된 계정 이름을 눈으로 확인**한 뒤에만 누르고, 공유 직전에 한 번 더 확인. 계정이 다르거나 확인이 안 되면 멈추고 사용자에게 넘김.
- 기업집중탐구 쪽 편성표(publisher/schedule.json)·`[기업인]` 탭·@company.focus 게시 루틴을 건드리지 않음. AI 쪽 파일은 저장소 `ai/`.
"""

REVIEW = """
---

# ④ 별도 점검 (넘기기 전)

쓴 Claude가 자기 원고를 점검하면 같은 곳을 또 놓침. 원고를 사용자에게 넘기기 **직전**, 쓰지 않은 점검자(새 서브에이전트 하나)에게 아래 프롬프트를 그대로 줌. 점검자는 고치지 않고 표만 냄 → 쓴 쪽이 고친 뒤 넘김. 보고 첫 줄: "점검: 어긴 곳 N개 고침, 확인 필요 M개".

```
너는 인스타 캐러셀 'AI기업집중탐구'의 원고 점검자다. 이 원고를 쓰지 않았다. 고치지 말고 어긴 곳만 찾는다.
읽을 것(전부): 이 합본의 ①②③ (/mnt/project-files/ai-pack/AI기업집중탐구-원고-지침.md), 기준 원고(템플릿) 링크의 형식.
점검 대상: <원고 Google 문서 링크>
방법: 규칙 줄을 위에서부터 하나씩 모든 장에 대어 본다. 해당 없으면 건너뛴다. 사실 확인이 필요한 숫자는 "확인 필요"로만 표시한다.
출력: 어긴 곳만 표로. 열 = 장(표지=00) | 규칙(절·줄 요약) | 어긴 내용(원문 인용) | 고칠 안. 없으면 "어긴 곳 없음" 한 줄. 칭찬·요약은 쓰지 않는다.
특히 볼 것: 맨 위 제목·상태 줄이 남았나, 장마다 새 페이지인가, 사진 없는 장, 같은 사진 두 번, 마무리 사진이 로고인가, 로고가 표지에 있나, 사진 설명 누락·불일치, 장 이름이 목록 밖(AI는 '지금'), 장 제목에 사건·숫자 두 개, "~하자"로 이유 없이 이어진 사건, 무엇을 보고 했나 빠진 투자·계약, 성격 모를 돈, 그 장 시점이 아닌 숫자, 출처 1곳뿐인 숫자, 회사가 밝힌 동기를 사실처럼 쓴 곳, 미래 전망, 처음 나오는 인물 소개, 회사·인물 표기, '지금' 장 숫자 2개(기준·연월), 마무리 3줄이 구체 사건과 붙었나, 설명란 순서(훅→연도 문단→질문+"댓글로 알려 주세요."→해시태그→출처)와 금지 줄(💬📌👇).
```
"""

def shift(md):
    # 원본의 # 제목을 합본 안에서 한 단계 내리고, rules 안 상대 링크를 저장소 경로로 바꿈
    md = re.sub(r"^(#+) ", lambda m: "#" + m.group(1) + " ", md, flags=re.M)
    md = re.sub(r"\]\((\d-[\w-]+\.md)\)", r"](https://github.com/ybkaudio/company-focus-media/blob/main/rules/\1)", md)
    md = md.replace("](archive/", "](https://github.com/ybkaudio/company-focus-media/blob/main/rules/archive/")
    return md

def main():
    out = [HEADER.replace("{date}", datetime.date.today().isoformat())]
    for fn, title in PARTS:
        p = RULES / fn
        if not p.exists():
            sys.exit(f"원본 없음: {p}")
        out.append(f"\n---\n\n# {title}  ·  원본 rules/{fn}\n\n" + shift(p.read_text()))
    out.append(REVIEW)
    for fn, title in TAIL:
        out.append(f"\n---\n\n# {title}  ·  원본 rules/{fn}\n\n" + shift((RULES / fn).read_text()))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(out))
    print(OUT, len("".join(out)), "자")

if __name__ == "__main__":
    main()
