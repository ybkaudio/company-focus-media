---
name: production-publishing-dept
description: 기업인집중탐구 🖼 제작·게시 부서의 작업 흐름과 2026-11-08 기준 대기열 상태
metadata:
  type: project
  modified: 2026-11-07T21:29:17.282Z
---

- 사진 원본은 이전 프로젝트에서 저장소 episodes/<편>/photos/에 커밋해 둠(04 넷플릭스 01·02·05~10, 05 나이키 10장, 특별편 01 10장). 세션에 사진이 없으면 저장소부터 확인하고, 빠진 장만 원고 부서가 요청하게 코디네이터에 알림.
- Metricool 예약 현황은 getScheduledPosts로 확인(uuid 고정, id는 수정마다 바뀜). 11/10 21:05 #09~#18(#12·#14·#16 수동 제외) 이미지 9e7fe8f로 교체 완료. 한눈에 보기는 /mnt/project-files/production/NN-slug-overview.png.
- Metricool 게시 성공 여부는 getScheduledPosts의 providers.status=PUBLISHED로 확인하고 Notion 상태를 맞춤.

- 보고 형식(업로드 예정 줄 + 한눈에 보기 링크, 사진 요청 안 함)은 [[kiup-jipjung-tamgu]] 참고.

**Why:** 새 스레드가 사진을 10장 다시 요청하거나, 게시된 편을 '예약'으로 남겨 두지 않게 하려고.
**How to apply:** 사진이 올라오면 저장소 photos/와 합쳐 렌더. 아침마다 게시 결과를 Notion과 맞춤. [[company-focus-episode]]

- 렌더 환경: python playwright가 없으면 `pip install playwright`. 폰트 Noto Sans CJK KR이 없으면 fallback 폰트로 렌더돼 사용자가 "폰트가 다르다"고 지적함 → 렌더 전 `apt-get install -y fonts-noto-cjk fonts-noto-cjk-extra` 후 `fc-match "Noto Sans CJK KR"` 확인. 사진 photos/는 .gitignore라 커밋하려면 add -f.
- (11/09 사용자) 내용이 많으면 10장 넘어도 됨. (11/11부터) Aside가 schedule.json count만큼 올려 20장까지 자동 게시됨 → render.py의 '10장 초과 수동 게시' 알림은 옛 Metricool 규칙이라 무시(11/16 편성 정정).
- (11/09) 사진을 어둡게·흐리게 하지 말 것. 새 편은 원본 밝기·선명도 그대로, 가독성은 그라데이션으로만. 워터마크는 크롭, 흐림은 그 부분에만 마지막 수단. 이미 확정된 편은 사용자가 지적한 장만 원본으로. 마무리 로고는 제목 뒤가 아니라 위쪽 빈 공간 가운데(#16).
- render.py 장별 title_size(px) 옵션 있음: 사용자 제목이 3줄로 넘치면 80으로 줄여 2줄 맞춤. 사진 배치(사용자 11/10 재정정): 기본은 배경 꽉 채우기. '너무 가로로만 긴' 사진(약 1.85:1 이상)만 위쪽+아래 검정 그라데이션. 1.5:1 정도 사진이나 화면 캡처도 꽉 채움(#21에서 지적).
- (11/10 사용자) 인스타 이름 '기업집중탐구'로 변경. render.py가 JSON의 '기업인집중탐구'를 자동으로 '기업집중탐구'로 바꿈(표지 줄·캡션). 핸들 @company.focus는 그대로. #01~#08은 이미 게시돼 손대지 않음.
- (11/11 사용자, #15) 로고 하나뿐인 사진을 배경으로 쓸 때는 로고(글자+심볼 포함)를 가로 정중앙에. 잘리지 않게 bgsize/bgpos로 맞추고, 세로는 제목 위 빈 공간 가운데(제목과 겹치지 않게). #15 03·마무리장 적용(9e31106).
- (11/11 사용자) 표지 로고: 가로 중심 820, 세로 중심 1137(줄 사이 가운데는 '너무 낮다'로 되돌림, 11/11). 정사각형 최대 260, 가로형 360. 제목이 짧으면 사용자가 제목 오른쪽 위를 지정하기도 함(#13) → sticker에 "fixed": true. 표지 사진에 로고 없으면 로고 요청.
- (11/11 사용자 "너무 오래 걸려") 코멘트마다 재렌더하지 말고 JSON만 고쳐 두고, 사용자가 "끝"이라고 하면 한 번에 렌더 후 바뀐 장만 보여 줌. 게시가 임박해도 먼저 렌더하지 말고 코디네이터에게 알림(11/11 코디네이터 정정). (11/11 코디네이터 재정정: 빈 사진이 들어오는 편도 예외 없음. 사진은 넣어 두고 "끝" 뒤 렌더.)
- (11/11 사용자 "사진 재탕하냐?") 한 편 안에서 같은 사진을 두 장에 쓰지 말 것. 사진이 없어 임시로 다른 장 사진을 넣었으면 반드시 보여 줄 때 알리고, 렌더 전 photos/ md5 중복 점검.

- (2026-11-23 사용자 확정) 게시는 Aside 루틴 대신 Meta Business Suite 예약. Aside 일회용 프롬프트 /mnt/project-files/production/business-suite-schedule.md를 편성표가 바뀔 때(주 1회 등) 붙여 넣어 미래 편을 한꺼번에 예약 → PC 켜 둘 필요 없음. 10장 넘는 캐러셀이 Business Suite에서 막히면 그 편은 '확인 필요'로 남김(장 빼기 금지).
- (2026-11-23 코디네이터) 규칙 원본은 저장소 rules/ 하나(README부터). 렌더 전 `python3 render.py --check`, overview 보이기 전 rules/4-review.md로 따로 점검. 예약 프롬프트는 publisher/make_bs_prompt.py → production/business-suite-prompt.md로 만듦.
