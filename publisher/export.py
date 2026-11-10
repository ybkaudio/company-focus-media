#!/usr/bin/env python3
"""렌더 → posts/NN-final 내보내기 → schedule.json 새로 채움.
  python3 publisher/export.py 17-samsung [14-amazon ...]
overview는 /mnt/project-files/production/NN-overview.png에도 복사(있으면)."""
import glob, os, shutil, subprocess, sys
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
for e in sys.argv[1:]:
    subprocess.run([sys.executable, "render.py", f"episodes/{e}.json"], check=True)
    src, dst = f"out/{e}", f"posts/{e}-final"
    os.makedirs(dst, exist_ok=True)
    for f in glob.glob(dst + "/[0-9][0-9].jpg"):
        os.remove(f)
    for f in sorted(glob.glob(src + "/[0-9][0-9].png")):
        Image.open(f).convert("RGB").save(f"{dst}/{os.path.basename(f)[:-4]}.jpg", quality=92)
    shutil.copy(f"{src}/caption.txt", f"{dst}/caption.txt")
    shutil.copy(f"{src}/{e}_한눈에보기.png", f"{dst}/overview.png")
    if os.path.isdir("/mnt/project-files/production"):
        shutil.copy(f"{dst}/overview.png", f"/mnt/project-files/production/{e}-overview.png")
subprocess.run([sys.executable, "publisher/sched.py", "refresh"], check=True)
