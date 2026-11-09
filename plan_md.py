"""기획안 JSON -> 읽기 쉬운 .md (장마다: 사진 한 줄, 제목 한 줄, 상세설명 n줄)
사용법: python3 plan_md.py episodes/03-whatsapp.json  -> plans/03-whatsapp.md
"""
import json, re, sys, pathlib


def sentences(lines):
    text = " ".join(x.strip() for x in lines)
    return [s.strip() for s in re.split(r"(?<=다\.)\s+|(?<=\.)\s+(?=[가-힣0-9\"'])", text) if s.strip()]


def main(path):
    path = pathlib.Path(path)
    ep = json.loads(path.read_text())
    no = ep["no"]
    label = f"특별편 #{no:02d}" if ep.get("special") else f"#{no:02d}"
    out = [f"# 기업인집중탐구 {label} · {ep['person']} ({ep['company']})", ""]
    out += ["> 사진은 아래 장 순서대로 01.jpg부터 올려 주세요. 고칠 제목이 있으면 같이 적어 주세요.", ""]
    if ep.get("music"):
        out += [f"🎵 **추천 음악:** {ep['music']}", ""]
    for i, s in enumerate(ep["slides"], 1):
        t = s.get("type", "text")
        name = "표지" if t == "cover" else s["index"]
        out.append(f"## {i:02d}.jpg · {name}")
        out.append("")
        out.append(f"📷 **Photo:** {s.get('photo_hint', '')}")
        out.append("")
        out.append(f"**제목:** {s['title'].replace(chr(10), ' ')}")
        out.append("")
        if t == "stats":
            for x in s["stats"]:
                out.append(f"- **{x['num']}{x['unit']}** — {x['cap']}")
            out.append("")
        if t == "outro":
            for x in s["points"]:
                out.append(f"- {x}")
            out.append("")
            if s.get('question'): out.append(f"댓글 질문: {s['question']}")
        else:
            for x in sentences(s.get("body", [])):
                out.append(x)
                out.append("")
        out.append("")
    out += ["---", "", "## 설명란 (캡션)", "", ep["caption"].strip(), ""]
    dst = pathlib.Path("plans") / f"{path.stem}.md"
    dst.parent.mkdir(exist_ok=True)
    dst.write_text("\n".join(out))
    print(dst)


if __name__ == "__main__":
    main(sys.argv[1])
