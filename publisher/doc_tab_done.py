#!/usr/bin/env python3
"""게시된 편의 공동 문서 탭에 ✅를 붙이고 문서 맨 뒤로 옮기는 요청 만들기 (11/25 사용자, AI기업집중탐구와 같은 방식. 탭은 지우지 않음).
  python3 publisher/doc_tab_done.py <read_doc 결과 파일> "<인물 · 회사 또는 탭 제목 일부>" [...]
출력 = Google Docs 커넥터 update_doc(documentId=공동 문서)의 requests JSON. 그대로 넘기면 됨.
이미 ✅가 붙은 탭은 건너뜀. 못 찾으면 '탭 없음'(문서 템플릿 이전 편은 탭이 없음)."""
import json, sys


def flat(tabs):
    for t in tabs:
        yield t
        yield from flat(t.get("childTabs", []))


def main():
    doc = json.load(open(sys.argv[1], encoding="utf-8"))
    doc = doc.get("content", doc)
    tabs = [t for t in flat(doc["tabs"]) if "parentTabId" not in t["tabProperties"]]
    last = max(t["tabProperties"].get("index", 0) for t in tabs)
    reqs = []
    for key in sys.argv[2:]:
        person = key.split(" · ")[0].strip()
        hit = [t for t in tabs if t["tabProperties"]["title"].startswith("[기업인]") and person in t["tabProperties"]["title"]]
        done = [t for t in tabs if t["tabProperties"]["title"].startswith("✅") and person in t["tabProperties"]["title"]]
        if not hit:
            print(f"{key}: {'이미 ✅' if done else '탭 없음'}", file=sys.stderr)
            continue
        tp = hit[0]["tabProperties"]
        reqs.append({"updateDocumentTabProperties": {
            "tabProperties": {"tabId": tp["tabId"], "title": "✅ " + tp["title"], "index": last},
            "fields": "title,index"}})
        print(f"{key}: {tp['title']} → ✅, 맨 뒤", file=sys.stderr)
    print(json.dumps(reqs, ensure_ascii=False))


if __name__ == "__main__":
    main()
