---
name: queue-image-default
description: 사용자가 "대기열"을 물으면 글이 아니라 표지 이미지 overview 2장으로 답함 (11/13 사용자)
metadata:
  type: feedback
---
- 2026-11-13 사용자: "대기열 보여줘 렌더된 건 대기중 사진들, 아직 렌더 안된 것도 사진 없이 렌더해서. 앞으로 대기열 보여달라 하면 이렇게 해서 줘 글로 알려달라고 하지 않는 이상."
- 형식: (a) 게시 대기 = posts/<폴더>/01.jpg 실제 표지 + 칸 아래 게시 시각·인물·회사·장수, (b) 사진 대기 = 원고 JSON 표지 글자만 사진 없이 렌더('미리보기 · 확정 아님' 띠) + '사진 대기'·순서.
- 도구: /mnt/project-files/production/queue-tool/covers.py(표지만 렌더, 저장소 render.py 사용) → grid.py(5열 묶기). 결과 production/queue-MMDD-a-rendered.png, -b-photo-wait.png. 제작·게시 스레드가 만들어 첨부.

**Why:** 사용자는 대기열을 표지로 한눈에 보고 싶어 함.
**How to apply:** "대기열" 요청 = 이 이미지 2장. 사용자가 "글로"라고 할 때만 글 목록. [[production-publishing-dept]]
