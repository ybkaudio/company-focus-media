---
name: photo-candidates-openverse
description: 공동 구글 문서에 추천 사진 넣을 때 후보 검색·삽입 방법과 Docs API 함정(한글 깨짐, 리비전)
metadata:
  type: reference
  modified: 2026-11-23T12:39:26.449Z
---
- 후보 찾기(11/23 기준): 사용자 지시로 위키미디어보다 웹 전체(뉴스·회사 사이트, 저작권 무관)를 먼저 뒤짐. WebSearch → 기사 페이지 og:image 추출 → 받아서 직접 보고 고름이 잘 됨(한국 기사 etnews·hankyung·khan, fortune 등은 Docs 삽입도 됨). DuckDuckGo 등 검색엔진 직접 긁기는 auto mode가 막음. Openverse 403, Commons API·upload.wikimedia.org 직접 받기는 429가 잦음(Docs 삽입은 됨).
- 상위 결과는 엉뚱한 게 많아 장마다 시대·내용 보고 직접 고름. 딱 맞는 사진이 없으면 비슷한 실제 사진으로 대신하고 그 장 번호를 탭 '■ 작성 메모'에 적음.
- 구글 문서 insertInlineImage는 flickr(live.staticflickr.com)와 wikimedia URL을 받음. 큰 원본은 /thumb/.../1280px-X 썸네일로, svg는 png 썸네일로. 지워진 파일·큰 사진은 "image not found / problem retrieving"으로 배치 전체가 실패하니 그 장만 다른 후보로 바꿔 재전송.
- 폭은 360pt, 표지 로고만 240pt. 이미지는 높은 인덱스부터 넣음.
- 도구 호출에 한글을 그대로 보내면 글자가 깨짐(그만뒀다→그만둬다 등). 문서에 쓰는 한글은 항상 \u 이스케이프로 보냄. 깨진 글자는 replaceAllText+tabsCriteria로 고침.
- 쓰기는 writeControl.requiredRevisionId를 응답에서 받은 값으로 이어 감. 사용자가 중간에 고치면 실패하니 다시 읽고 바뀐 탭만 확인.
- 사용자가 붙여 넣은 사진은 sourceUri가 없음. 템플릿으로 다시 쓸 때 그 사진은 지우지 않고 주변 글만 바꿈.
- 11/23 [기업인] 12탭을 Anthropic 템플릿으로 다시 씀(서식·사진 전부, 검증 완료).
- 관련: [[company-focus-gdoc]]
