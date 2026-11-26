---
name: production-auto-render
description: 11/14 사용자 - 제작·게시는 수정이 오면 "끝"을 기다리지 않고 바로 자동 렌더(사진 위치 클릭 피드백만 예외)
metadata:
  type: feedback
---
- 2026-11-14 14:29 사용자: "앞으로 사진에 내가 위치 클릭해서 피드백하는 거 아니면 바로바로 자동으로 렌더해."
- 옛 규칙(11/11 "끝"이라고 하기 전까지 렌더하지 않음, 코멘트 모아 한 번에)을 대신함. 예외: 사용자가 overview·사진 위에 위치를 찍어 주는 피드백은 기존처럼 모아 두었다가 "끝" 뒤 렌더.
- 렌더 후 바뀐 장/overview를 스레드에 바로 보여 줌. 내보내기(export.py)까지 하고 편성에 알림.

**Why:** 렌더를 미뤄 확인이 늦어짐.
**How to apply:** 사진 교체·글 수정·레이아웃 지시가 오면 그 턴에 export.py 실행. [[production-publishing-dept]] [[kiup-jipjung-tamgu]]
