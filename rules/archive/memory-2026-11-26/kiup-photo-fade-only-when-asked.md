---
name: kiup-photo-fade-only-when-asked
description: 사진 축소·위쪽 배치 + 아래 검정 그라데이션(render.py photo_fade)은 사용자가 지정한 페이지에만 적용 (2026-11-12)
metadata:
  type: feedback
  modified: 2026-11-12T11:40:17.965Z
---
- 2026-11-12 젠슨 황 편에서 사용자가 10장(GeForce 칩)·11장(Xbox)에 "사진을 여기까지 내리고 아래는 검정 그라데이션", "사진 더 축소해서 넓게"를 요청함 → render.py에 photo_fade 옵션("시작%-끝%")을 추가하고 bgsize/bgpos와 함께 씀(2e6e97c).
- 사용자: "앞으로 계속 그라데이션 하지는 말고, 내가 하라고 할 때만 그 페이지에 한해서 적용해".

**Why:** 기본 디자인은 사진으로 배경을 꽉 채우는 것이고, 검정 페이드는 예외임.
**How to apply:** 사용자가 그 페이지를 콕 집어 말할 때만 photo_fade를 쓴다. 다른 장이나 다른 편으로 넓히지 않는다. [[kiup-photo-and-link-rules]]
