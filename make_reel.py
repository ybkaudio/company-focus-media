"""캐러셀 카드 -> 릴스 영상 (1080x1920, 9:16)
사용법: python3 make_reel.py out/03-whatsapp posts/03-whatsapp-final/reel.mp4 [음악.mp3]
- 배경: 카드 자체를 흐리고 어둡게 깔고, 가운데에 카드(1080x1350)
- 표지 2.5초, 본문 장 3.5초, 마무리 3초, 장 사이 0.4초 크로스페이드
- 음악 파일을 주면 영상 길이에 맞춰 넣고 끝에서 페이드아웃
"""
import glob, os, subprocess, sys, tempfile
from PIL import Image, ImageFilter, ImageEnhance

W, H = 1080, 1920
FADE = 0.4


def frame(card_path, dst):
    card = Image.open(card_path).convert("RGB")
    bg = card.resize((int(H * card.width / card.height), H))
    x = (bg.width - W) // 2
    bg = bg.crop((x, 0, x + W, H)).filter(ImageFilter.GaussianBlur(40))
    bg = ImageEnhance.Brightness(bg).enhance(0.35)
    bg.paste(card, (0, (H - card.height) // 2))
    bg.save(dst)


def main(src_dir, out_mp4, music=None):
    cards = sorted(glob.glob(os.path.join(src_dir, "[0-9][0-9].png")) or glob.glob(os.path.join(src_dir, "[0-9][0-9].jpg")))
    n = len(cards)
    durs = [2.5] + [3.5] * (n - 2) + [3.0]
    tmp = tempfile.mkdtemp()
    inputs = []
    for i, c in enumerate(cards):
        f = os.path.join(tmp, f"{i:02d}.png")
        frame(c, f)
        inputs += ["-loop", "1", "-t", str(durs[i] + FADE), "-i", f]
    # xfade 체인: 각 클립 길이 d+FADE, 겹침 FADE -> i번째 시작 = sum(d[:i])
    chain = []
    last, acc = "[0:v]", 0.0
    for i in range(1, n):
        acc += durs[i - 1]
        out = f"[v{i}]"
        chain.append(f"{last}[{i}:v]xfade=transition=fade:duration={FADE}:offset={acc:.2f}{out}")
        last = out
    total = acc + durs[-1] + FADE
    fc = ";".join(chain) + f";{last}format=yuv420p,fps=30[vout]"
    cmd = ["ffmpeg", "-y", "-loglevel", "error"] + inputs
    maps = ["-map", "[vout]"]
    if music:
        cmd += ["-i", music]
        fc += f";[{n}:a]atrim=0:{total:.2f},afade=t=out:st={total - 1.5:.2f}:d=1.5[aout]"
        maps += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-filter_complex", fc] + maps + ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                                             "-movflags", "+faststart", "-t", f"{total:.2f}", out_mp4]
    os.makedirs(os.path.dirname(out_mp4) or ".", exist_ok=True)
    subprocess.run(cmd, check=True)
    print(out_mp4, f"{total:.1f}s")


if __name__ == "__main__":
    main(*sys.argv[1:4])
