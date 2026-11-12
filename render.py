"""기업집중탐구 캐러셀 렌더러 v2 (korea_titans식: 전면 사진 + 하단 그라데이션)
사용법: python3 render.py episodes/01-apple.json
- 각 장의 "photo"에 이미지 파일(episodes/ 기준 경로)을 넣으면 배경 사진으로 들어감
- photo가 없으면 '사진 자리' 표시가 있는 시안으로 렌더됨
출력: out/<에피소드>/NN.png (1080x1350) + caption.txt
"""
import html, json, sys, base64, pathlib, subprocess
from playwright.sync_api import sync_playwright

W, H = 1080, 1350

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px;background:#000;color:#fff;
 font-family:'Noto Sans CJK KR';word-break:keep-all}
.s{position:relative;width:1080px;height:1350px;overflow:hidden;background:#0b0b0d}
.bg{position:absolute;inset:0;background-size:cover;background-repeat:no-repeat;background-position:center top}
.ph{position:absolute;left:0;right:0;top:0;height:78%;
 background:repeating-linear-gradient(135deg,#17171b 0 26px,#131316 26px 52px);
 display:flex;align-items:center;justify-content:center}
.ph span{position:absolute;top:250px;font-size:30px;letter-spacing:.3em;color:#3a3a42;font-weight:700;
 border:3px dashed #2c2c33;padding:22px 40px;border-radius:14px}
/* 사용자 규칙(11/8): 사진을 가리는 진한 검정은 금지. #02 마이크로소프트 수준의 옅은 그라데이션 + 글자 그림자만 */
.shade.on~.txt h1,.shade.on~.txt p,.shade.on~.txt .pt,.shade.on~.txt .q,.shade.on~.txt .st,.shade.on~.txt .who,.shade.on~.txt .handle,.shade.on~.txt .c,.shade.on~.txt .u{text-shadow:1px 0 0 rgba(0,0,0,.5),-1px 0 0 rgba(0,0,0,.5),0 1px 0 rgba(0,0,0,.5),0 -1px 0 rgba(0,0,0,.5),0 0 14px rgba(0,0,0,.5)}
.shade.on~.idx{text-shadow:1px 0 0 rgba(0,0,0,.5),-1px 0 0 rgba(0,0,0,.5),0 1px 0 rgba(0,0,0,.5),0 -1px 0 rgba(0,0,0,.5),0 0 14px rgba(0,0,0,.5)}
.shade{position:absolute;inset:0;
 background:linear-gradient(180deg,rgba(0,0,0,.45) 0%,rgba(0,0,0,0) 16%,rgba(0,0,0,0) 38%,rgba(0,0,0,.82) 62%,#000 82%)}
.shade.on{background:linear-gradient(180deg,rgba(0,0,0,.4) 0%,rgba(0,0,0,.05) 14%,rgba(0,0,0,.08) 42%,rgba(0,0,0,.5) 62%,rgba(0,0,0,.68) 82%,rgba(0,0,0,.72) 100%)}
.shade.on.tall{background:linear-gradient(180deg,rgba(0,0,0,.4) 0%,rgba(0,0,0,.1) 12%,rgba(0,0,0,.45) 34%,rgba(0,0,0,.62) 56%,rgba(0,0,0,.72) 100%)}
.idx{position:absolute;top:96px;left:80px;font-size:32px;font-weight:700;letter-spacing:.12em;color:#fff}
.idx:after{content:"";display:block;width:84px;height:5px;background:var(--a);margin-top:22px}
.pg{position:absolute;top:84px;right:72px;font-size:32px;font-weight:500;color:#fff;
 background:rgba(0,0,0,.55);padding:12px 26px;border-radius:40px}
.pn{position:absolute;right:40px;bottom:26px;max-width:700px;text-align:right;font-size:19px;line-height:1.3;color:rgba(255,255,255,.72);text-shadow:0 1px 4px rgba(0,0,0,.8);z-index:5}
.when{position:absolute;top:96px;right:80px;font-size:30px;font-weight:700;letter-spacing:.04em;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.7)}
/* 11/11 사용자: 연도·나이 아래 그때 회사 가치(추정) — 장마다 비교 */
.val{position:absolute;top:140px;right:80px;font-size:30px;font-weight:700;letter-spacing:.04em;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.7)}
.txt{position:absolute;left:80px;right:80px;bottom:120px}
h1{font-size:88px;line-height:1.2;font-weight:900;letter-spacing:-.025em;white-space:pre-line}
.cover h1{font-size:90px}
.dv{width:84px;height:5px;background:var(--a);margin:44px 0 40px}
p{font-size:36px;line-height:1.55;color:#ececf0;font-weight:400}
.who{font-size:42px;font-weight:700;color:#fff;margin-bottom:6px;letter-spacing:-.01em}
.handle{font-size:30px;letter-spacing:.28em;font-weight:700;margin-bottom:34px;color:#fff}
.stats{margin-top:8px}
.st{margin-bottom:34px}
.st .c{font-size:32px;color:#ececf0;margin-bottom:6px}
.st .n{font-size:150px;font-weight:900;line-height:1;letter-spacing:-.03em}
.st .u{font-size:44px;font-weight:500;margin-left:14px;color:#ececf0}
.st .ln{height:4px;background:#fff;opacity:.85;margin:18px 0 0}
.pt{font-size:36px;line-height:1.55;color:#ececf0;padding-left:30px;position:relative;margin-bottom:6px}
.pt:before{content:"·";position:absolute;left:4px}
.q{font-size:44px;font-weight:900;margin-top:44px}
.qa{font-size:32px;color:#ececf0;margin-top:10px}
.ft{margin-top:56px;font-size:28px;letter-spacing:.24em;font-weight:700}
.stk{position:absolute;filter:drop-shadow(0 8px 18px rgba(0,0,0,.55))}
.btn{display:inline-block;margin-top:24px;background:#fff;color:#000;font-size:34px;font-weight:700;
 padding:22px 56px;border-radius:6px}
"""

def e(t):
    return html.escape(t or "")

def lines(xs):
    # 문장 단위로 적힌 본문(한 항목이 길면)은 이어 붙여 자연스럽게 줄바꿈, 짧은 줄 단위면 줄마다 끊음
    if any(len(x) > 30 for x in xs):
        import re
        out = " ".join(e(x) for x in xs)
        return re.sub(r"&lt;([^&]{1,30})&gt;", r'<span style="white-space:nowrap">&lt;\1&gt;</span>', out)
    return "<br>".join(e(x) for x in xs)

def slide_html(ep, s, i, n, base):
    t = s.get("type", "text")
    if s.get("photo"):
        p = base / s["photo"]
        mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
        uri = f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()
        extra = (f';background-size:{s["bgsize"]}' if s.get("bgsize") else '') + (f';background-position:{s["bgpos"]}' if s.get("bgpos") else '')
        if s.get("photo_fade"):   # 11/12 사용자: 사진은 위쪽 N%까지만, 그 아래는 검정 그라데이션 ("a-b" = 흐려지기 시작%-끝%)
            a, b = s["photo_fade"].split("-")
            extra += f';-webkit-mask-image:linear-gradient(180deg,#000 {a}%,transparent {b}%);mask-image:linear-gradient(180deg,#000 {a}%,transparent {b}%)'
        bg = f'<div class="bg" style="background-image:url({uri}){extra}"></div>'
    else:
        bg = '<div class="ph"><span>사진 자리</span></div>'
    shade = 'shade' + (' on' if s.get('photo') else '') + (' tall' if t in ('stats', 'outro') else '') + (' strong' if s.get('shade') == 'strong' else '')
    head = ''
    if s.get("sticker"):
        k = s["sticker"]; sp = base / k["src"]
        su = "data:image/png;base64," + base64.b64encode(sp.read_bytes()).decode()
        head += f'<img class="stk" src="{su}" style="width:{k.get("size",260)}px;right:{k.get("right",80)}px;top:{k.get("top",120)}px">'
    if t != "cover":
        head += f'<div class="idx">{e(s["index"])}</div>'
    if s.get("when"):
        head += f'<div class="when">{e(s["when"])}</div>'
    # 11/11 사용자: 연도·나이와 같은 글씨. 회사 설립 전 장과 떠날 때(stats) 장에는 넣지 않음
    # 숫자(회사 가치 …)일 때만. 떠날 때(stats) 장과 그 뒤 '떠난 뒤' 장에는 넣지 않음
    sl = ep.get("slides", [])
    st = next((k for k, x in enumerate(sl, 1) if x.get("type") == "stats"), n + 1)
    if s.get("value", "").startswith("회사 가치") and t != "stats" and i < st:
        head += f'<div class="val">{e(s["value"])}</div>'
    if s.get("photo_note"):   # 11/12 사용자: 사진 맨 아래 오른쪽에 아주 작게 원본 사진 설명(한국어)
        head += f'<div class="pn">{e(s["photo_note"])}</div>'
    if t == "cover":
        h1 = e(s["title"])
        if s.get("title_logo"):   # 제목 속 "{logo}" 자리에 로고 이미지를 글자 대신 넣음
            tl = s["title_logo"]; lp = base / tl["src"]
            lu = "data:image/png;base64," + base64.b64encode(lp.read_bytes()).decode()
            h1 = h1.replace("{logo}", f'<img src="{lu}" style="height:{tl.get("height",96)}px;vertical-align:{tl.get("valign","-8px")};{tl.get("css","")}">')
        chs = f' style="font-size:{s["title_size"]}px"' if s.get("title_size") else ''
        body = (f'<div class="handle">{e(ep["handle"]).upper()}</div><h1{chs}>{h1}</h1>'
                f'<div class="dv"></div><div class="who">{e(ep["person"])} · {e(ep.get("company_ko") or ep["company"])}</div><p>{lines(s["body"])}</p>')
        return f'<div class="s cover">{bg}<div class="{shade}"></div>{head}<div class="txt">{body}</div></div>'
    hs = f' style="font-size:{s["title_size"]}px"' if s.get("title_size") else ''
    if t == "stats":
        st = "".join(f'<div class="st"><div class="c">{e(x["cap"])}</div><div class="n">{e(x["num"])}<span class="u">{e(x["unit"])}</span></div></div>' for x in s["stats"])
        body = f'<h1{hs}>{e(s["title"])}</h1><div class="dv"></div><div class="stats">{st}</div><p>{lines(s["body"])}</p>'
    elif t == "outro":
        pts = "".join(f'<div class="pt">{e(x)}</div>' for x in s["points"])
        q = (f'<div class="q">{e(s["question"])}</div><div class="qa">{e(s.get("ask",""))}</div>' if s.get("question") else '')
        body = (f'<h1>{e(s["title"])}</h1><div class="dv"></div>{pts}{q}'
                f'<div class="ft">{e(ep["handle"]).upper()}</div><div class="btn">{e(s["button"])}</div>')
    else:
        body = f'<h1{hs}>{e(s["title"])}</h1><div class="dv"></div><p>{lines(s["body"])}</p>'
    return f'<div class="s">{bg}<div class="{shade}"></div>{head}<div class="txt">{body}</div></div>'

FONT = "Noto Sans CJK KR"   # 고정 폰트. 없으면 대체 폰트로 렌더하지 않고 멈춤

def check_font():
    # 굵기(Regular·Bold·Black)마다 진짜 Noto Sans CJK KR로 잡히는지 확인
    for w in ("regular", "bold", "black"):
        r = subprocess.run(["fc-match", "-f", "%{family}", f"{FONT}:weight={w}"], capture_output=True, text=True)
        if FONT not in r.stdout:
            sys.exit(f"폰트 '{FONT}'({w})가 없음 (지금 잡히는 폰트: {r.stdout or '없음'}). "
                     "apt-get install -y fonts-noto-cjk fonts-noto-cjk-extra && fc-cache -f 후 다시 렌더")

OLD_NAME, NEW_NAME = "기업인집중탐구", "기업집중탐구"  # 11/10 인스타 이름 변경

def _rename(o):
    if isinstance(o,str): return o.replace(OLD_NAME, NEW_NAME)
    if isinstance(o,list): return [_rename(x) for x in o]
    if isinstance(o,dict): return {k:_rename(v) for k,v in o.items()}
    return o

def main(path):
    check_font()
    path = pathlib.Path(path)
    ep = _rename(json.loads(path.read_text()))
    slides = ep["slides"]
    assert 1 <= len(slides) <= 20, "인스타 캐러셀은 최대 20장"
    if len(slides) > 10:
        print(f"알림: {len(slides)}장이라 자동 게시(Metricool·API, 최대 10장)는 안 됨 → 사용자가 앱에서 수동 게시")
    out = pathlib.Path("out") / path.stem
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("[0-9]*.png"):
        old.unlink()
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = b.new_page(viewport={"width": W, "height": H})
        photos = path.parent / path.stem / "photos"   # episodes/01-apple/photos/01.jpg ... 자동 연결
        for i, s in enumerate(slides, 1):
            if not s.get("photo"):
                for ext in ("jpg", "jpeg", "png", "webp"):
                    cand = photos / f"{i:02d}.{ext}"
                    if cand.exists():
                        s["photo"] = str(cand.relative_to(path.parent))
                        break
            doc =(f'<html><head><meta charset="utf-8"><style>:root{{--a:{ep["accent"]}}}{CSS}</style></head>'
                   f'<body>{slide_html(ep, s, i, len(slides), path.parent)}</body></html>')
            pg.set_content(doc)
            pg.wait_for_timeout(150)
            # 레이아웃 검사: 본문 블록이 위 주석(.idx·.when·.pg)과 겹치거나 화면 밖으로 나가면 멈춤
            bad = pg.evaluate("""() => {
              const t = document.querySelector('.txt'); if (!t) return null;
              const r = t.getBoundingClientRect(); let lim = 0;
              for (const q of ['.idx','.when','.val','.pg']) { const el = document.querySelector(q); if (el) lim = Math.max(lim, el.getBoundingClientRect().bottom); }
              if (r.top < lim + 40) return `본문 시작 ${Math.round(r.top)}px가 위 주석 아래 ${Math.round(lim)}px+40과 겹침`;
              if (r.bottom > innerHeight) return '본문이 화면 아래로 넘침';
              const k = document.querySelector('.stk');
              if (k) { const a = k.getBoundingClientRect();
                for (const q of ['.idx','.when','.val','.txt h1','.txt p','.txt .who','.txt .handle','.txt .stats']) {
                  for (const el of document.querySelectorAll(q)) { const rg = document.createRange(); rg.selectNodeContents(el);
                    const fs = parseFloat(getComputedStyle(el).fontSize);
                    for (const r0 of rg.getClientRects()) {   // 실제 글자 줄의 영역만 검사(줄 간격 여백은 빼고 글자 높이만)
                      const pad = Math.max(0, (r0.height - fs) / 2), b = {left: r0.left, right: r0.right, top: r0.top + pad, bottom: r0.bottom - pad};
                      if (a.left < b.right + 8 && a.right > b.left - 8 && a.top < b.bottom + 8 && a.bottom > b.top - 8)
                        return `스티커가 ${q} 글자와 겹침(스티커 top·size 조정)`; } } } }
              return null; }""")
            if bad:
                sys.exit(f"{i:02d}장 레이아웃 문제: {bad}. 본문·제목을 줄이고 다시 렌더")
            pg.screenshot(path=str(out / f"{i:02d}.png"))
        b.close()
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "publisher"))
    from caption_split import split_caption
    cap, comment = split_caption(ep["caption"])   # 💬 질문은 캡션 대신 첫 댓글로 (11/11)
    comment = (ep.get("first_comment") or comment.lstrip("💬").strip()).strip()   # 원고 first_comment 우선
    (out / "caption.txt").write_text(cap)
    (out / "comment.txt").write_text(comment + "\n" if comment else "")
    # 장별 필요한 사진 목록 (photos 폴더에 01.jpg부터 이 순서로 넣으면 자동 반영)
    hints = [f"{i:02d}.jpg  {s.get('index', '표지')}: {s.get('photo_hint', '')}" for i, s in enumerate(slides, 1)]
    (out / "사진_목록.txt").write_text("\n".join(hints) + "\n")
    # 한눈에 보기 PNG 한 장 (4열)
    from PIL import Image
    fs = sorted(out.glob("[0-9]*.png"))
    cw, ch, cols = 360, 450, 4
    rows = (len(fs) + cols - 1) // cols
    sheet = Image.new("RGB", (cw * cols, ch * rows), (40, 40, 40))
    for k, f in enumerate(fs):
        sheet.paste(Image.open(f).resize((cw, ch)), ((k % cols) * cw, (k // cols) * ch))
    sheet.save(out / f"{path.stem}_한눈에보기.png")
    print(f"{len(slides)} slides -> {out}")

if __name__ == "__main__":
    main(sys.argv[1])
