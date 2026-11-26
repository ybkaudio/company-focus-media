#!/usr/bin/env python3
"""사용자가 쓴 표지 제목을 '인스타 제목 제작 학습자료' 문서 3번 표 맨 아래에 한 줄 옮겨 적는 요청 만들기 (11/26 사용자: 렌더 전 제목 확인 때마다 루틴).
  python3 publisher/title_log.py <공동 문서 read_doc 파일> <학습자료 read_doc 파일> "[기업인] 인물" "인물 · 회사" [--lesson "배운 점"]
출력 = Google Docs update_doc(documentId=1riKkPaH0VyYqcUczPJ3gI6hGy2-Pw137piMVHG2oAq0)의 requests JSON.
이미 같은 편·같은 최종 문구 줄이 있으면 '이미 적힘'을 알리고 [] 출력(00시 스캔·즉시 렌더 중복 방지).
형식: 날짜(KST) · 기업인 · 인물 · 회사 · 개입 종류 · Claude 후보 · 최종 문구 · 배운 점."""
import datetime as dt, json, re, sys

LEARN_DOC = "1riKkPaH0VyYqcUczPJ3gI6hGy2-Pw137piMVHG2oAq0"


def load(p):
    d = json.load(open(p, encoding="utf-8"))
    return d.get("content", d)


def flat(tabs):
    for t in tabs:
        yield t
        yield from flat(t.get("childTabs", []))


def ptext(content):
    return "".join(e.get("textRun", {}).get("content", "")
                   for el in content if "paragraph" in el for e in el["paragraph"]["elements"]).strip()


def norm(s):
    return re.sub(r"[\s/·]+", "", s)


def cover_lines(doc, tab_title):
    tab = next(t for t in flat(doc["tabs"]) if t["tabProperties"]["title"] == tab_title)
    out, on = [], False
    for el in tab["documentTab"]["body"]["content"]:
        t = ptext([el]) if "paragraph" in el else ""
        if t.startswith("■"):
            if on:
                break
            on = True
            continue
        if on and t:
            out.append(t)
    return out


def main():
    a = sys.argv[1:]
    lesson = ""
    if "--lesson" in a:
        i = a.index("--lesson"); lesson = a[i + 1]; a = a[:i] + a[i + 2:]
    shared, learn, tab_title, name = a[0], a[1], a[2], a[3]
    L = cover_lines(load(shared), tab_title)
    final = next((l.split(":", 1)[1].strip() for l in L if l.startswith("표지 제목:")), "")
    if not final:
        sys.exit("표지 제목이 비어 있음 = 적을 것 없음")
    cands = [re.sub(r"^[①②③④⑤]\s*", "", l) for l in L if re.match(r"^[①②③④⑤]", l)]
    hit = [k for k, c in enumerate(cands, 1) if norm(c) == norm(final)]
    kind = f"후보 {hit[0]}번 채택" if hit else ("후보 고쳐 씀" if cands else "직접 쓴 제목")

    doc = load(learn)
    body = doc["tabs"][0]["documentTab"]["body"]["content"]
    tables = [el for el in body if "table" in el]
    tbl = tables[-1] if len(tables) == 1 else tables[2]   # '3. 개입 기록' 표
    rows = tbl["table"]["tableRows"]
    for r in rows:
        cells = [ptext(c["content"]) for c in r["tableCells"]]
        if len(cells) >= 6 and norm(name) in norm(cells[2]) and norm(final) in norm(cells[5]):
            print(f"이미 적힘: {name}", file=sys.stderr)
            print("[]")
            return
    vals = [dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).strftime("%m/%d"), "기업인", name, kind,
            "\n".join(f"{'①②③④⑤'[k]} {c}" for k, c in enumerate(cands)), "표지: " + final, lesson]
    R = rows[-1]["endIndex"]   # 새 줄 시작 위치. 빈 칸 k의 글자 자리 = R + 2 + 2k
    reqs = [{"insertTableRow": {"tableCellLocation": {"tableStartLocation": {"index": tbl["startIndex"]},
                                                      "rowIndex": len(rows) - 1, "columnIndex": 0}, "insertBelow": True}}]
    for k in reversed(range(len(vals))):   # 뒤 칸부터 넣어 앞 칸 위치가 안 밀리게
        if vals[k]:
            reqs.append({"insertText": {"location": {"index": R + 2 + 2 * k}, "text": vals[k]}})
    print(f"적을 줄: {' | '.join(vals)}", file=sys.stderr)
    print(json.dumps(reqs, ensure_ascii=False))


if __name__ == "__main__":
    main()
