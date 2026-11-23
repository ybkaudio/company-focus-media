# company-focus-media

기업집중탐구(@company.focus) 인스타 캐러셀 제작 저장소.

**규칙은 `rules/` 폴더 하나가 원본** (rules/README.md부터). 작업 전에 맡은 단계의 파일을 읽는다.
- 원고: rules/1-wongo-common.md + rules/1-wongo-kiupin.md
- 사진·렌더: rules/2-design.md, 렌더 전 `python3 render.py --check episodes/<stem>.json`
- 편성·예약: rules/3-upload.md, 예약 프롬프트는 `python3 publisher/make_bs_prompt.py`
- overview를 사용자에게 보이기 직전: rules/4-review.md 별도 점검

사용자 피드백이 규칙이면 rules/ 해당 파일 한 곳만 고치고(옛 줄은 지움, 날짜·예시 붙임), 적은 문장을 사용자에게 한 줄로 돌려준다. 메모리·스킬·인수인계 파일에 규칙 본문을 쓰지 않는다.
