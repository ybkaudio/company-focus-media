"""기업집중탐구 캐러셀 렌더러 v2 (korea_titans식: 전면 사진 + 하단 그라데이션)
사용법: python3 render.py [--check] [--legacy] episodes/01-apple.json
규칙: textbook/ 폴더(00-시작.md). 잴 수 있는 규칙은 rule_check()가 렌더 전에 멈춤
- 각 장의 "photo"에 이미지 파일(episodes/ 기준 경로)을 넣으면 배경 사진으로 들어감
- photo가 없으면 '사진 자리' 표시가 있는 시안으로 렌더됨
출력: out/<에피소드>/NN.png (1080x1350) + caption.txt
"""
import html, json, re, sys, base64, pathlib, subprocess

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
        ar = wide_ratio(p)
        if ar and not s.get("bgsize") and not s.get("photo_fade"):   # 11/26 사용자: 가로로 긴 사진은 확대·자르기 없이 가로 폭에 맞춰 위에, 남는 아래는 검정 그라데이션
            h = 1080 / ar
            a, b = max(h - 220, h * 0.7), h
            extra += (';background-size:100% auto;background-position:center top'
                      f';-webkit-mask-image:linear-gradient(180deg,#000 {a:.0f}px,transparent {b:.0f}px);mask-image:linear-gradient(180deg,#000 {a:.0f}px,transparent {b:.0f}px)')
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
    if t == "promo":   # 11/23 사용자: 모든 편 맨 끝 고정 홍보 장(assets/promo/01~06.jpg 6분할, 문구 고정)
        cfg = json.loads((PROMO_DIR / "promo.json").read_text())
        cells = "".join(
            f'<div style="background:url(data:image/jpeg;base64,{base64.b64encode((PROMO_DIR / c["file"]).read_bytes()).decode()}) {c.get("pos","center 20%")}/cover"></div>'
            for c in cfg["photos"])
        grid = f'<div style="position:absolute;left:0;right:0;top:0;height:900px;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,1fr);gap:4px;background:#0b0b0d">{cells}</div>'
        body = (f'<div class="handle">{e(ep["handle"]).upper()}</div><h1>{e(cfg["title"])}</h1><div class="dv"></div>'
                f'<p>{"<br>".join(e(x) for x in cfg["body"])}</p><div class="btn">{e(cfg["button"])}</div>')
        return f'<div class="s">{grid}<div class="shade on tall"></div><div class="txt">{body}</div></div>'
    if t == "stats":
        st = "".join(f'<div class="st"><div class="c">{e(x["cap"])}</div><div class="n">{e(x["num"])}<span class="u">{e(x["unit"])}</span></div></div>' for x in s["stats"])
        body = f'<h1{hs}>{e(s["title"])}</h1><div class="dv"></div><div class="stats">{st}</div><p>{lines(s["body"])}</p>'
    elif t == "outro":
        pts = "".join(f'<div class="pt">{e(x)}</div>' for x in s["points"])
        q = (f'<div class="q">{e(s["question"])}</div><div class="qa">{e(s.get("ask",""))}</div>' if s.get("question") else '')
        body = (f'<h1>{e(s["title"])}</h1><div class="dv"></div>{pts}{q}'
                + (f'<div class="ft">{e(ep["handle"]).upper()}</div><div class="btn">{e(s["button"])}</div>' if not ep.get("_promo") else ''))
    else:
        body = f'<h1{hs}>{e(s["title"])}</h1><div class="dv"></div><p>{lines(s["body"])}</p>'
    return f'<div class="s">{bg}<div class="{shade}"></div>{head}<div class="txt">{body}</div></div>'

PROMO_DIR = pathlib.Path(__file__).resolve().parent / "assets" / "promo"
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

# 장 제목에 써도 되는 영어(제품·약어). 여기 없는 영어 낱말이 장 제목에 있으면 --check가 멈춤.
# 낯선 영어 회사명은 제목에서 빼고, 알려진 회사는 한글(구글·애플·인텔·엔비디아…)로. (11/26 사용자 결정 카드, textbook 6장)
TITLE_LATIN_OK = {"CEO", "CTO", "COO", "AI", "PC", "CD", "DVD", "GPU", "CPU", "VR", "IPO", "OS", "BASIC", "IBM", "HP",
                  "LG", "SK", "KAIST", "MIT", "CIA", "CES", "TSMC", "HBM", "HBM3E", "D", "A8", "II", "C.C.", "SNS",
                  "Android", "YouTube", "Blogger", "Sidekick", "Altair", "Micro-Soft", "Falcon", "GTX", "iPhone"}


INDEX_OK = {"배경", "계기", "창업", "자금", "투자", "상장", "첫 성과", "방향 전환", "혁신", "성장", "확장",
            "경쟁", "갈등", "위기", "실수", "정점", "매각", "떠날 때", "그 뒤", "마무리", "지금"}   # textbook/04-구성.md (11/23)
DARK_KEYS = ("filter", "brightness", "blur", "dim", "darken", "opacity")   # textbook/10-렌더.md: 사진 어둡게·흐리게 금지 (11/09)

WIDE = 1.0   # 가로:세로 1:1 이상 = 가로로 긴 사진(11/26 사용자). 이보다 세로로 긴 사진만 꽉 채우기(cover)


def wide_ratio(p):
    """가로로 긴 사진이면 가로/세로 비율, 아니면 None."""
    try:
        from PIL import Image
        with Image.open(p) as im:
            r = im.width / im.height
        return r if r >= WIDE else None
    except Exception:
        return None


def resolve_photos(slides, path):
    photos = path.parent / path.stem / "photos"   # episodes/01-apple/photos/01.jpg ... 자동 연결
    for i, s in enumerate(slides, 1):
        if not s.get("photo"):
            for ext in ("jpg", "jpeg", "png", "webp"):
                cand = photos / f"{i:02d}.{ext}"
                if cand.exists():
                    s["photo"] = str(cand.relative_to(path.parent))
                    break

def final_caption(ep):
    """게시되는 설명란 그대로(caption.txt)."""
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "publisher"))
    from caption_split import split_caption, question_into_caption
    cap, comment = split_caption(ep["caption"])
    question = (ep.get("first_comment") or comment.lstrip("💬").strip()).strip()   # 원고 first_comment 우선
    return strip_sources(question_into_caption(cap, question))   # 11/14 사용자: 첫 댓글 없음, 질문은 설명란에


def strip_sources(cap):
    """11/24 사용자: 설명란에 출처를 넣지 않음(출처는 원고 문서에만). '출처' 줄부터 해시태그 줄 전까지 뺌."""
    out, skip = [], False
    for l in cap.split("\n"):
        if re.match(r"\s*(📚\s*)?출처\s*:?\s*$", l) or re.match(r"\s*(📚\s*)?출처\s*:", l):
            skip = True
            continue
        if skip and l.lstrip().startswith("#"):
            skip = False
        if not skip:
            out.append(l)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


CAP_MAX = 2200   # 인스타 설명란 한도. 이모지는 2자로 셀 수 있어 UTF-16 길이로 잼 (11/24 카프 편 2,368자로 게시 실패)


def rule_check(ep, path, legacy=False):
    """textbook/ 규칙 중 기계로 잴 수 있는 것. 어긴 곳 목록을 돌려줌(비면 통과).
    legacy=True: 이미 게시된 옛 편(번호·옛 장 이름이 박힌 편)을 다시 렌더할 때만."""
    import hashlib, re
    bad, seen = [], {}
    lim = 20 if legacy else 19   # 11/23: 새 편은 렌더러가 홍보 장을 붙이므로 원고는 최대 19장
    if len(ep["slides"]) > lim:
        bad.append(f"장 수 {len(ep['slides'])}장: 한 편 최대 {lim}장(표지·마무리 포함, 홍보 장은 렌더러가 붙여 20장)")
    for i, s in enumerate(ep["slides"], 1):
        n = f"{i:02d}장"
        ph = s.get("photo")
        if ph:
            f = path.parent / ph
            if not f.exists():
                bad.append(f"{n}: 사진 파일 없음 {ph}")
                continue
            if not s.get("photo_note"):   # 11/14·11/15 사용자: 사진 있는 모든 장에 사진 설명
                bad.append(f"{n}: photo_note(사진 설명) 없음 (textbook 7장 사진 설명)")
            h = hashlib.md5(f.read_bytes()).hexdigest()
            if h in seen and not s.get("photo_dup_ok"):   # 11/11 사용자 "사진 재탕하냐?"
                bad.append(f"{n}: {seen[h]}과 같은 사진 (textbook 7장)")
            seen.setdefault(h, n)
            if wide_ratio(f) and s.get("bgsize") and not s.get("photo_small"):   # 로고만 놓는 장(photo_small)은 예외   # 11/26 사용자: 가로 사진은 확대해서 자르지 않음
                bad.append(f"{n}: 가로로 긴 사진에 bgsize(확대·자르기) 있음 → 빼면 가로 폭에 맞춰 위에 놓고 아래는 검정 그라데이션 (textbook 10장 배치)")
            if not s.get("photo_small") and s.get("type") != "stats":   # 11/15 사용자: 메인 사진은 좌우 끝까지
                try:
                    from PIL import Image
                    im = Image.open(f).convert("L")
                    bb = im.point(lambda v: 255 if v > 45 else 0).getbbox()
                    if abs(im.width / im.height - 0.8) < 0.02 and bb and (bb[2] - bb[0]) < im.width * 0.9:
                        bad.append(f"{n}: 메인 사진이 좌우를 다 채우지 않음(내용 폭 {(bb[2]-bb[0])*100//im.width}%) — 좌우 끝까지 키우기, 로고만·직접 그린 그래프는 photo_small: true")
                except ImportError:
                    pass
        if s.get("shade") == "strong" or any(k in s for k in DARK_KEYS) or any(k in str(s.get("bgsize", "")) + str(s.get("bgpos", "")) for k in DARK_KEYS):
            bad.append(f"{n}: 사진을 어둡게·흐리게 하는 설정 (textbook 10장 배치)")
        if legacy:
            continue
        if s.get("photo_fade") and not s.get("photo_fade_by_user"):   # 11/12·11/23 사용자: 검정 페이드는 내가 말한 장만
            bad.append(f"{n}: photo_fade는 사용자가 그 장을 지시했을 때만 (photo_fade_by_user에 날짜 적기, 아니면 photo_fade 빼고 사진 크기·위치로)")
        if s.get("type") != "cover" and "index" in s:
            w = s["index"].split("·")[-1].strip()
            if w not in INDEX_OK:
                bad.append(f"{n}: 장 이름 '{w}'은 목록에 없음 (textbook 4장 장 이름)")
        txt = json.dumps({k: s.get(k) for k in ("title", "body", "points", "index", "photo_note", "question", "stats")}, ensure_ascii=False)
        if re.search(r"#\d", txt):   # 11/13 사용자: 편 번호(#NN) 쓰지 않음
            bad.append(f"{n}: 편 번호(#숫자) 있음 → '(인물 · 회사 편)'으로")
    if ep.get("caption"):
        m = len(final_caption(ep).encode("utf-16-le")) // 2
        if m > CAP_MAX:
            bad.append(f"캡션: 설명란 {m}자 > {CAP_MAX}자(인스타 한도, 넘으면 게시 실패) → 연도 문단을 줄임(출처는 설명란에 넣지 않음)")
    if not legacy:
        cap = ep.get("caption", "")
        if re.search(r"#\d", cap):
            bad.append("캡션: 편 번호(#숫자) 있음 → '인물 · 회사 편'으로")
        tt = [re.sub(r"[\s.!?…\"'”’」』)]+$", "", str(s.get("title", ""))) for s in ep["slides"]
              if s.get("type") not in ("cover", "stats", "promo") and s.get("title")]
        da = sum(t.endswith("다") for t in tt)
        if tt and da * 2 > len(tt):   # 11/09·11/26 사용자: '-다' 끝 제목은 절반까지
            bad.append(f"제목: '-다'로 끝나는 장 제목 {da}/{len(tt)}개 > 절반 (textbook 6장 어미 섞기)")
        if ep.get("account", "kiupin") != "ai":   # [AI] 계정은 자기 기준
            for s in ep["slides"]:
                if s.get("type") in ("cover", "stats", "promo"):
                    continue
                t = str(s.get("title", "")).replace("Apple II", "II")   # 제품명 Apple II만 허용, 회사 Apple은 '애플'
                for w in re.findall(r"[A-Za-z][A-Za-z0-9.\-]*", t):
                    if w.rstrip(".") not in TITLE_LATIN_OK and w not in TITLE_LATIN_OK:
                        bad.append(f"제목: 장 제목의 영어 '{w}' → 낯선 영어 회사명은 빼고 알려진 회사는 한글로"
                                   f" (제품·약어면 render.py TITLE_LATIN_OK에 추가, textbook 6장)")
        for c in ("📌", "👇"):   # 11/14 사용자: 첫 댓글·저장 유도 줄 없음
            if c in cap:
                bad.append(f"캡션: '{c}' 줄 있음 (textbook 8장 설명란)")
        if not ep.get("company_ko"):
            bad.append("company_ko 없음 (표지 '인물 · 회사' 줄)")
        if ep.get("account", "kiupin") != "ai":
            bad += ch8_check(ep, cap)
    return bad


AFTER_SUCCESS_OK = {"정점", "상장", "성장", "첫 성과", "매각", "갈등"}   # 떠날 때 바로 앞 장(4장 끝 장: 성공담, 밀려난 편은 갈등)


def ch8_check(ep, cap):
    """11/26 Google 별도 점검에서 걸린 것 중 기계로 잴 수 있는 것(textbook 8장 통과 기준 '⚙ 자체 점검')."""
    import re
    bad, sl = [], ep["slides"]
    for i, s in enumerate(sl, 1):
        n = f"{i:02d}장"
        note = str(s.get("photo_note") or "")
        if s.get("photo") and note and not re.search(r"(1[89]|20)\d\d", note):
            bad.append(f"{n}: 사진 설명에 연도 없음 → 무엇·누구·연도 (textbook 7장 사진 설명)")
        t = str(s.get("title", ""))
        for u in ("달러", "%", "원"):
            if t.count(u) >= 2:
                bad.append(f"{n}: 장 제목에 숫자 두 개('{u}' 두 번) → 가장 큰 숫자 하나만 (textbook 6장)")
        w = str(s.get("index", "")).split("·")[-1].strip()
        if w == "떠날 때":
            prev = str(sl[i - 2].get("index", "")).split("·")[-1].strip() if i >= 2 else ""
            if prev not in AFTER_SUCCESS_OK:
                bad.append(f"{n}: 떠날 때 바로 앞 장이 '{prev}' → 성공담(정점·상장 등)을 앞에 (textbook 4장 끝 장)")
            body = s.get("body") or []
            last = body[-1] if body else ""
            if not re.search(r"뒤|이후|그 다음|떠난 다음|(19|20)\d\d년", last):
                bad.append(f"{n}: 떠날 때 본문 끝에 떠난 뒤 행보 한 줄 없음 (textbook 4장 끝 장)")
    if cap:
        lines = [l.strip() for l in cap.split("\n")]
        head = " ".join(lines[:2])
        if not re.search(r"\d", head):
            bad.append("캡션: 훅 2줄에 숫자 없음 (textbook 8장 설명란 ①)")
        if "댓글로 알려 주세요." not in lines:
            bad.append("캡션: '댓글로 알려 주세요.'가 질문 다음 줄에 따로 없음 (textbook 8장 설명란 ④)")
        if re.search(r"(어요|해요|예요|이에요|거든요)[.!]", cap):
            bad.append("캡션: 해요체 → 습니다체 (textbook 8장 설명란 ②)")
        if re.search(r"^\s*(📚\s*)?출처\s*:?\s*$", cap, re.M):
            bad.append("캡션: 출처 블록 있음 → 작성 메모로 (textbook 8장 설명란)")
        tags = [l for l in lines if l.startswith("#")]
        if tags and not tags[-1].startswith("#기업집중탐구"):
            bad.append("캡션: 해시태그 줄이 #기업집중탐구로 시작하지 않음 (textbook 8장 설명란 ⑥)")
        link = [l for l in lines if l.startswith("🔗")]
        if link and "시리즈" in link[0] and tags:
            ser = re.sub(r"\s", "", link[0][1:].split("시리즈")[0])
            second = (tags[-1].split() + ["", ""])[1]
            if ser and not second.startswith(f"#{ser}"):
                bad.append(f"캡션: 묶음 해시태그(#{ser}시리즈)가 #기업집중탐구 바로 뒤에 없음 (textbook 8장 묶음 편)")
    if not re.search(r"대안", str(ep.get("music", ""))):
        bad.append("음악: 대안 1곡 없음 (textbook 8장 음악 추천)")
    return bad

def main(path, check_only=False, legacy=False):
    path = pathlib.Path(path)
    ep = _rename(json.loads(path.read_text()))
    slides = ep["slides"]
    assert 1 <= len(slides) <= 20, "인스타 캐러셀은 최대 20장"
    resolve_photos(slides, path)
    bad = rule_check(ep, path, legacy)
    if bad:   # textbook/ 규칙 자동 멈춤 (11/23 규칙 정리)
        sys.exit("규칙 점검에 걸림(textbook/ 참고). 고치고 다시:\n- " + "\n- ".join(bad))
    if not legacy and len(slides) <= 19 and not ep.get("no_promo"):
        slides.append({"type": "promo", "index": "홍보"}); ep["_promo"] = True
    if check_only:
        print(f"규칙 점검 통과: {path.stem} ({len(slides)}장{', 홍보 장 포함' if ep.get('_promo') else ''})")
        return
    check_font()
    from playwright.sync_api import sync_playwright   # --check는 playwright 없이 돌게
    out = pathlib.Path("out") / path.stem
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("[0-9]*.png"):
        old.unlink()
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = b.new_page(viewport={"width": W, "height": H})
        for i, s in enumerate(slides, 1):
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
    (out / "caption.txt").write_text(final_caption(ep))
    (out / "comment.txt").write_text("")
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
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    # --check: 렌더 없이 규칙 점검만 (textbook/08·10장)
    # --legacy: 이미 게시된 옛 편(번호·옛 장 이름)을 다시 렌더할 때만
    main(args[0], check_only="--check" in sys.argv, legacy="--legacy" in sys.argv)
