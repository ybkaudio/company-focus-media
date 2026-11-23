#!/usr/bin/env python3
"""공동 원고 문서의 편 탭(Anthropic 형식, rules/1-wongo-common.md 6) → episodes/<stem>.json + photos/.
  python3 publisher/doc2episode.py <read_doc 결과 파일> "<탭 제목 또는 t.탭ID>" <stem>        # 바꿀 것만 보여 줌
  python3 publisher/doc2episode.py <read_doc 결과 파일> "<탭 제목 또는 t.탭ID>" <stem> --apply

read_doc 결과 파일 = Google Docs 커넥터 read_doc(documentId=공동 문서) 출력(크면 도구가 파일로 저장해 줌).
문서가 원본(사용자가 사진을 바꾸거나 글을 고침). 이 스크립트는 문서 → JSON 방향으로만 맞춤:
  - 표지 제목(= 사용자 제목, 그대로), 장 제목, 본문(문장 나눔), 회사 가치 줄
  - 장마다 사진: 첫 사진 → photos/NN.jpg(1.85:1 이상이면 위쪽 띠 합성), 표지의 로고 사진('사진 설명'에 '로고') → <stem>/sticker-logo.png
    한 장에 사진이 2개면 나란히(설명에 '위아래'가 있으면 위아래) 붙여 1600x2000 합성
  - 사진 설명 → photo_note (첫 문장만)
  - 떠날 때·지금(숫자)·마무리·설명란은 바꾸지 않고 다르면 '확인' 줄로만 알림(원고가 고침)
문서의 ■ 장 수와 JSON 장 수가 다르면 멈춤(장 구성은 원고 일)."""
import io, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def paragraphs(tab):
    dt = tab["documentTab"]
    objs = dt.get("inlineObjects", {})
    for el in dt["body"]["content"]:
        p = el.get("paragraph")
        if not p:
            continue
        style = p.get("paragraphStyle", {}).get("namedStyleType", "")
        text = "".join(e.get("textRun", {}).get("content", "") for e in p["elements"]).strip()
        imgs = []
        for e in p["elements"]:
            if "inlineObjectElement" in e:
                o = objs.get(e["inlineObjectElement"]["inlineObjectId"], {})
                ip = o.get("inlineObjectProperties", {}).get("embeddedObject", {}).get("imageProperties", {})
                if ip.get("contentUri"):
                    imgs.append(ip["contentUri"])
        yield style, text, imgs


def find_tab(tabs, key):
    for t in tabs:
        tp = t["tabProperties"]
        if key in (tp.get("tabId"), tp.get("title")):
            return t
        r = find_tab(t.get("childTabs", []), key)
        if r:
            return r


def sections(tab):
    secs, cur = [], None
    for style, text, imgs in paragraphs(tab):
        if text.startswith("■"):
            cur = {"head": text, "lines": [], "imgs": []}
            secs.append(cur)
            continue
        if cur is None:
            continue
        if text:
            cur["lines"].append(text)
        for u in imgs:
            cur["imgs"].append({"url": u, "note": None})
        if text.startswith("사진 설명:"):
            # 이 설명은 바로 앞 사진(설명 없는 마지막 사진)에 붙음
            for im in reversed(cur["imgs"]):
                if im["note"] is None:
                    im["note"] = text.split(":", 1)[1].strip()
                    break
    return secs


def field(lines, name):
    for l in lines:
        if l.startswith(name + ":"):
            return l.split(":", 1)[1].strip()
    return None


def sentences(t):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=\S)", t) if s.strip()]


def first_sentence(t):
    s = re.split(r"(?<=[.])\s+", t.strip())[0].strip()
    return s[:-1] if s.endswith(".") else s


def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        from PIL import Image
        return Image.open(io.BytesIO(r.read())).convert("RGBA")


def compose(ims, vertical):
    from PIL import Image, ImageOps
    W, H = 1600, 2000
    can = Image.new("RGB", (W, H), (14, 14, 16))
    if vertical:
        h = 1000
        for k, im in enumerate(ims[:2]):
            can.paste(ImageOps.fit(im.convert("RGB"), (W, h)), (0, k * h))
    else:
        w = W // 2
        for k, im in enumerate(ims[:2]):
            can.paste(ImageOps.fit(im.convert("RGB"), (w, H)), (k * w, 0))
    return can


def main():
    src, key, stem = sys.argv[1], sys.argv[2], sys.argv[3]
    apply = "--apply" in sys.argv
    doc = json.load(open(src, encoding="utf-8"))
    doc = doc.get("content", doc)
    tab = find_tab(doc["tabs"], key)
    if not tab:
        sys.exit(f"탭을 못 찾음: {key}")
    secs = [s for s in sections(tab) if re.match(r"■\s*\d\d", s["head"])]
    jp = os.path.join(ROOT, "episodes", stem + ".json")
    ep = json.load(open(jp, encoding="utf-8"))
    slides = ep["slides"]
    if len(secs) != len(slides):
        sys.exit(f"장 수 다름: 문서 ■ {len(secs)}장, JSON {len(slides)}장 → 원고에 맞춰 달라고 할 것")
    pdir = os.path.join(ROOT, "episodes", stem, "photos")
    changes, checks, jobs = [], [], []
    for k, (sec, sl) in enumerate(zip(secs, slides)):
        nn = f"{k + 1:02d}"
        L = sec["lines"]
        def setv(key2, val, label):
            if val is not None and sl.get(key2) != val:
                changes.append(f"{nn} {label}: {str(sl.get(key2))[:40]!r} → {str(val)[:40]!r}")
                sl[key2] = val
        if k == 0:
            t = field(L, "표지 제목")
            if not t:
                sys.exit("표지 제목이 비어 있음 = 아직 확정 아님")
            setv("title", t.replace(" / ", "\n"), "표지 제목")
        else:
            t = field(L, "장 제목")
            if t:
                setv("title", t.replace(" / ", "\n"), "장 제목")
            b = field(L, "본문")
            if b and sl.get("type") not in ("stats", "outro"):
                setv("body", sentences(b), "본문")
            v = field(L, "회사 가치 줄")
            if v:
                setv("value", v, "회사 가치 줄")
            if sl.get("type") in ("stats", "outro") and (field(L, "숫자 1") or field(L, "본문")):
                checks.append(f"{nn} {sl.get('type')} 장 글은 자동으로 안 맞춤 → 문서와 JSON 직접 대조")
        imgs = sec["imgs"]
        logo = [i for i in imgs if k == 0 and i["note"] and "로고" in i["note"]]
        main_imgs = [i for i in imgs if i not in logo]
        if not main_imgs:
            checks.append(f"{nn} 사진 없음")
            continue
        note = main_imgs[0]["note"] or ""
        if len(main_imgs) >= 2 and not re.search("나란히|위아래", note):
            note += (" · " if note else "") + "나란히 붙임"
        setv("photo_note", first_sentence(note) if len(main_imgs) == 1 else note, "사진 설명")
        jobs.append((nn, main_imgs, logo[0] if logo else None, "위아래" in note))
    print("\n".join(changes) or "글·사진 설명 바뀐 것 없음")
    for c in checks:
        print("확인:", c)
    if not apply:
        print(f"(미리보기) 사진 {len(jobs)}장 받을 예정. --apply로 적용")
        return
    os.makedirs(pdir, exist_ok=True)
    for nn, ims, logo, vertical in jobs:
        pics = [fetch(i["url"]) for i in ims]
        out = os.path.join(pdir, nn + ".jpg")
        if len(pics) >= 2:
            img = compose(pics, vertical)
        elif pics[0].width / pics[0].height >= 1.85:   # 가로로 긴 사진: 위쪽에 가로 채우고 아래 검정(rules/2-design.md 배치)
            from PIL import Image
            im = pics[0].convert("RGB"); im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
            img = Image.new("RGB", (1600, 2000), (14, 14, 16)); img.paste(im, (0, 0))
        else:
            img = pics[0].convert("RGB")
        img.save(out, quality=92)
        if logo:
            fetch(logo["url"]).save(os.path.join(ROOT, "episodes", stem, "sticker-logo.png"))
            slides[0].setdefault("sticker", {"src": f"{stem}/sticker-logo.png", "size": 260, "right": 80, "top": 1100})
    json.dump(ep, open(jp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(jp, "a", encoding="utf-8").write("\n")
    print(f"적용: {jp}, 사진 {len(jobs)}장 → {pdir}")


if __name__ == "__main__":
    main()
