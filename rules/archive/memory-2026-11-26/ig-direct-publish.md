---
name: ig-direct-publish
description: 모든 편 인스타 게시는 Aside 루틴(schedule.json)으로. Metricool은 한도 도달로 안 씀(11/11). API 장치는 대기
metadata:
  type: project
---
2026-11-11 사용자 "진행해": Metricool은 캐러셀 10장까지라 10장 초과 편은 Instagram API(Instagram 로그인) 직접 게시로 자동화.
- 코드: 저장소 publisher/ig_publish.py, schedule.json(예약 목록), published.json(기록), .github/workflows/ig-publish.yml(10분마다), ig-token-refresh.yml(매달 1·15일).
- 비밀값: IG_TOKEN(필수), GH_PAT(토큰 갱신용, Secrets 쓰기). 사용자 설정 단계: /mnt/project-files/production/ig-auto-setup.md
- 첫 대상 #11 11/11 16:00(편성 하루 3회 체제, 11/15까지). 웹에선 음악 불가, 고급 설정에서 좋아요 수 숨김. 성공하면 나머지 수동 편(#12·#14·#15·#16·#17·#21·#23)을 schedule.json에 추가.
- 수동으로 먼저 올려도 캡션 첫 줄이 같으면 건너뜀. 3시간 넘게 늦으면 안 올림.
- 이 환경 프록시는 GitHub Actions 실행·로그 API를 막음 → 점검 실행·결과 확인은 사용자가 Actions 탭에서, 또는 published.json 커밋으로 확인.
- 11/11 Meta 개발자 가입이 '평소 안 쓰는 기기' 보안으로 막힘 → 사용자: 당분간 Facebook developers 없이 Aside로. Aside 루틴 프롬프트 publisher/aside-routine.md(=/mnt/project-files/production/aside-routine.md). Aside는 schedule.json(main raw)을 매일 00:05·08:05·12:05·16:05 읽어 이미지 내려받아 instagram.com에 올림. 루틴은 사용자 PC에서 돌아서 PC·Aside가 켜져 있어야 함. 워크플로는 IG_TOKEN 없으면 쉼.
- 11/11 사용자: Metricool 업로드 한도 도달 → 10장 이하 편도 모두 Aside. 렌더·내보내기 후 `python3 publisher/sched.py add NN-slug YYYY-MM-DDTHH:MM "#NN 이름"`(KST)로 넣고 푸시. music 필드는 episodes JSON의 music에서 자동, Aside는 음악을 넣지 않고 Notion 메모에 곡명만 남김(11/11 사용자 "음악 빼"). #11은 11/11 02:04 Aside로 게시 완료.
- 결과 기록: Notion DB "인스타 게시 기록" https://app.notion.com/p/6cc52ac73d8940b58891535d0091f736 (data source collection://5e7dd121-e858-4509-9361-41c8d391dd98, "공유 메모리 (Claude ↔ Aside)" 페이지 안). Aside가 편마다 한 줄. 9시 브리핑이 읽음.
- 대기(11/11): #11 재게시. 원고 수정 커밋 후 재렌더 → sched.py add 11-paypal 2026-11-15T16:00 "#11 일론 머스크·PayPal". 11/15 15:00까지 재렌더 안 되면 넣지 않음(옛 이미지 금지). 넣기 전에 overview를 제작·게시 스레드에 먼저 보여 주고 사용자 확인 받기. 1차 게시본은 삭제됨, Notion 행은 "(삭제됨) #11 1차 게시본".
- 제작·게시 스레드 11/11 02:45 갈아타기 요청(스레드당 첨부 24개 한도, 메시지당 6개). 인수인계 /mnt/project-files/production/handoff-2026-11-11.md.
**How to apply:** 10장 초과 편을 예약할 때 Metricool 대신 schedule.json에 at·folder·episode·count·first_line을 넣는다. [[kiup-jipjung-tamgu]]
