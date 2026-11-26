---
name: aside-account-check
description: Aside 게시 전 계정 확인 - company.focus가 아니면(AI기업집중탐구 등) 전환, 실패 시 게시 중단 (2026-11-13 사용자 요청)
metadata:
  type: feedback
---
- 2026-11-13 사용자: Aside가 다른 계정 'AI기업집중탐구'로 게시할까 걱정. 계정이 다르면 전환하라는 명령을 넣으라고 함.
- 적용: production/aside-routine.md에 0단계(프로필로 계정 확인 → 다르면 더 보기 > 계정 전환 → 재확인 → 실패 시 게시 중단, Notion '로그인 필요' + '계정 전환 실패')와 공유 직전 재확인, 지키기 줄 추가. 사용자에게 기존 루틴 수정용 붙여 넣기 문구를 줌.
- 일회용 블록: production/aside-account-check.md.

**Why:** 같은 브라우저에 다른 인스타 계정이 로그인돼 있을 수 있어 잘못 게시될 위험이 있음.
**How to apply:** 앞으로 쓰는 모든 일회용 Aside 프롬프트 맨 앞에 aside-account-check.md 단계를 넣는다. [[production-publishing-dept]]
