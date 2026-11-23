# company-focus-media
인스타 @company.focus(기업집중탐구) 제작 키트와 게시 이미지.
- **규칙: `rules/` 폴더(README.md부터)**. 렌더 전 `python3 render.py --check episodes/NN-slug.json`
- `episodes/NN-slug.json` 원고 → `python3 render.py episodes/NN-slug.json` → `out/NN-slug/`
- `posts/NN-slug-final/01.jpg…` Business Suite 예약에 쓰는 공개 이미지 (`publisher/make_bs_prompt.py`)
- 사진 원본(`episodes/*/photos/`)은 올리지 않음
- 폰트는 Noto Sans CJK KR 고정. 없으면 render.py가 멈춤 → `apt-get install -y fonts-noto-cjk fonts-noto-cjk-extra && fc-cache -f`
