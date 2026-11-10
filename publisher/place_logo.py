#!/usr/bin/env python3
"""표지 로고 스티커를 인물 줄 오른쪽(중심 820,1137)에 글자와 안 겹치게 배치. 사용: python3 publisher/place_logo.py 19-apple-wayne ..."""
import json,sys,pathlib
import os; os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0,'.')
import render
from PIL import Image
from playwright.sync_api import sync_playwright
CX,CY=820,1137
eps=sys.argv[1:]
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome"); pg=b.new_page(viewport={"width":1080,"height":1350})
    for e in eps:
        p=pathlib.Path(f'episodes/{e}.json'); raw=p.read_text(); d=json.loads(raw); ep=render._rename(d)
        s=dict(ep['slides'][0]); k=s.pop('sticker')
        ph=p.parent/e/'photos'
        for ext in ('jpg','jpeg','png','webp'):
            c=ph/f'01.{ext}'
            if c.exists() and not s.get('photo'): s['photo']=str(c.relative_to(p.parent))
        pg.set_content(f'<html><head><meta charset="utf-8"><style>:root{{--a:{ep["accent"]}}}{render.CSS}</style></head><body>{render.slide_html(ep,s,1,len(ep["slides"]),p.parent)}</body></html>')
        rects=pg.evaluate("""()=>{const out=[];for(const q of ['.txt h1','.txt p','.txt .who','.txt .handle']){for(const el of document.querySelectorAll(q)){const rg=document.createRange();rg.selectNodeContents(el);for(const r of rg.getClientRects())out.push([r.left,r.top,r.right,r.bottom]);}}return out;}""")
        im=Image.open(p.parent/k['src']); asp=im.height/im.width
        maxw=170 if asp>0.6 else 240
        w=maxw
        while w>80:
            h=w*asp; L,T,R,B=CX-w/2,CY-h/2,CX+w/2,CY+h/2
            if R>1080-40: L-= (R-1040); R=1040
            if not any(L<r[2]+12 and R>r[0]-12 and T<r[3]+12 and B>r[1]-12 for r in rects): break
            w-=10
        k.update(size=int(w),right=int(1080-R),top=int(T))
        d['slides'][0]['sticker']=k
        p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+("\n" if raw.endswith("\n") else ""))
        print(e,k,round(asp,2))
    b.close()
