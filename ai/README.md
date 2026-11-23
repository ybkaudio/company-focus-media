# ai/ — AI기업집중탐구(@aicompany.focus) 업로드 폴더

기업집중탐구 파일(posts/, publisher/, episodes/)과 따로 씀. AI 쪽 Claude만 고침. 규칙: rules/8-ai-upload.md.

- 게시 방식: Aside가 사용자 PC의 instagram.com에서 **직접 게시**(Business Suite 예약 안 씀: 인스타 캐러셀 10장 제한).
- 시각: 슬롯 02·06·10·14·18·22시 KST. Aside 루틴은 각 슬롯 5분 뒤 **02:05·06:05·10:05·14:05·18:05·22:05**에 돌며, `schedule.json`에서 at이 지났고 3시간 안인 편을 올림.
- `posts/NN-slug/01.jpg…` + `caption.txt`: 렌더·점검을 통과한 편. Aside가 raw 주소로 내려받음.
- `schedule.json`: 편 목록. 칸 = at(+09:00), folder, episode, count, first_line, music. 칸 이름을 바꾸면 Aside 프롬프트(합본 ⑥ 부록)도 같이 고침.
- 둘 다 `/mnt/project-files/ai-pack/tools/publish_ai.py`가 씀. 손으로 고치지 않음. 이미 게시된 편의 caption.txt·first_line은 바꾸지 않음(중복 확인이 첫 줄 비교).
