# Aside 루틴 프롬프트 (10장 넘는 편 인스타그램 자동 게시)

아래 "루틴 프롬프트"를 Aside 채팅에 그대로 붙여 넣으면 Aside가 루틴을 만든다.

## 루틴 프롬프트

매일 00:05, 08:05, 12:05, 16:05(한국 시간) 하루 네 번 아래 일을 하는 루틴을 만들어 줘(루틴 하나에 네 시각). 게시 시각은 목록이 정하니, 올릴 편이 없는 시각에는 확인만 하고 끝내면 돼. 매번 처음부터 아래 순서대로 해.

1. https://raw.githubusercontent.com/ybkaudio/company-focus-media/main/publisher/schedule.json 을 열어.
   각 항목은 at(게시 시각), folder(폴더), episode(편 이름), count(장 수), first_line(캡션 첫 줄)이야.
2. at이 지금보다 이전이고 지금으로부터 3시간 안인 항목만 골라. 없으면 "올릴 편 없음"이라고 남기고 끝내.
3. 고른 편마다 https://www.instagram.com/company.focus/ 를 열어 최근 게시물 6개의 캡션을 확인해.
   first_line과 같은 문장으로 시작하는 게시물이 있으면 이미 올라간 거니까 그 편은 건너뛰어.
4. 이미지를 내려받아. 주소는 https://raw.githubusercontent.com/ybkaudio/company-focus-media/main/{folder}/01.jpg 부터 count번까지(두 자리 번호: 01, 02, … 12).
   다운로드 폴더 안 company-focus/{folder 마지막 이름}/ 에 저장해. 캡션은 https://raw.githubusercontent.com/ybkaudio/company-focus-media/main/{folder}/caption.txt 의 전문이야.
5. instagram.com에서 만들기 → 게시물 → 컴퓨터에서 선택 → 저장한 이미지를 01부터 번호 순서대로 모두 선택해.
   - 자르기 화면에서 비율을 "원본" 또는 4:5로 바꿔(정사각형 1:1이면 안 됨). 확대하지 마.
   - 필터·조정은 건드리지 마.
   - 캡션 칸에 caption.txt 전문을 그대로 붙여 넣어(줄바꿈 유지, 고치지 마).
   - 공유를 눌러.
6. 올라간 뒤 게시물을 열어 장 수가 count와 같은지 확인하고, 게시물 링크·장 수·시각을 결과로 남겨.
   장 수가 다르거나 오류가 나면 지우지 말고 "확인 필요"와 이유를 남겨.

지키기: 위 목록에 없는 게시물은 만들지 마. 이미 있는 게시물을 지우거나 고치지 마. 로그인 창이 뜨면 멈추고 "로그인 필요"라고 남겨.

## 손으로 바로 올릴 때 (루틴 없이)
"지금 {folder} 편을 위 3~6번대로 올려 줘"라고 쓰면 됨.
