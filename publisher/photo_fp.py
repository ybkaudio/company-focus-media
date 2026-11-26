#!/usr/bin/env python3
"""공동 원고 문서 [기업인] 탭의 장별 사진 지문 저장·비교 → 사용자가 바꾼 사진 찾기(rules/2-design.md '사용자 사진 교체에서 배운 점').
  python3 publisher/photo_fp.py <read_doc 결과 파일>           # 저장된 지문과 비교, 바뀐 장만 보여 줌
  python3 publisher/photo_fp.py <read_doc 결과 파일> --save    # 지금 문서 상태를 지문으로 저장(publisher/photo_fp.json)

지문 = 장마다 사진의 문서 객체 ID + sourceUri(우리가 URL로 넣은 사진만 있음, 사용자가 올린 사진은 없음) + 사진 설명.
'사용자 교체' = 저장 때 있던 사진이 사라지고 sourceUri 없는 새 사진이 들어온 장. 옛 사진 URL·옛 설명·새 사진 보기 링크를 보여 줌.
원고가 문서를 고친 뒤엔 --save(우리 변경이 사용자 교체로 잡히지 않게). 비교 결과를 학습에 반영한 뒤에도 --save."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FP = os.path.join(ROOT, "publisher", "photo_fp.json")


def tabs(ts):
    for t in ts:
        yield t
        yield from tabs(t.get("childTabs", []))


def slides(tab):
    dt = tab["documentTab"]
    objs = dt.get("inlineObjects", {})
    out, cur = {}, None
    for el in dt["body"]["content"]:
        p = el.get("paragraph")
        if not p:
            continue
        text = "".join(e.get("textRun", {}).get("content", "") for e in p["elements"]).strip()
        m = re.match(r"■\s*(\d\d)", text)
        if text.startswith("■"):
            cur = out.setdefault(m.group(1), []) if m else None
            continue
        if cur is None:
            continue
        for e in p["elements"]:
            if "inlineObjectElement" in e:
                oid = e["inlineObjectElement"]["inlineObjectId"]
                ip = objs.get(oid, {}).get("inlineObjectProperties", {}).get("embeddedObject", {}).get("imageProperties", {})
                cur.append({"id": oid, "src": ip.get("sourceUri", ""), "view": ip.get("contentUri", ""), "note": None})
        if text.startswith("사진 설명:"):
            for im in reversed(cur):
                if im["note"] is None:
                    im["note"] = text.split(":", 1)[1].strip()
                    break
    return out


def main():
    doc = json.load(open(sys.argv[1], encoding="utf-8"))
    doc = doc.get("content", doc)
    now = {}
    for t in tabs(doc["tabs"]):
        title = t["tabProperties"]["title"]
        if "[기업인]" in title:
            now[title.replace("✅", "").strip()] = slides(t)
    if "--save" in sys.argv:
        keep = {k: {n: [{x: im[x] for x in ("id", "src", "note")} for im in v] for n, v in s.items()} for k, s in now.items()}
        json.dump(keep, open(FP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"저장: {len(keep)}편 → {os.path.relpath(FP, ROOT)}")
        return
    old = json.load(open(FP, encoding="utf-8")) if os.path.exists(FP) else {}
    found = 0
    for title, s in now.items():
        if title not in old:
            print(f"(새 탭, 지문 없음) {title}")
            continue
        for n, ims in s.items():
            before = old[title].get(n, [])
            bid = {im["id"] for im in before}
            new = [im for im in ims if im["id"] not in bid and not im["src"]]
            gone = [im for im in before if im["id"] not in {x["id"] for x in ims}]
            if new:
                found += 1
                print(f"■ 사용자 교체: {title} {n}장")
                for im in gone:
                    print(f"   우리 사진: {im['src'] or '(사용자 사진)'} / 설명: {im['note']}")
                for im in new:
                    print(f"   새 사진 보기: {im['view']}\n   새 설명: {im['note'] or '(없음 → 렌더 전 써야 함)'}")
    print(f"사용자 교체 {found}장" + ("" if found else " (없음)"))


if __name__ == "__main__":
    main()
