"""캡션에서 '💬 …댓글로 알려 주세요.' 줄과 '📌 저장해 두고…' 줄을 빼고, 💬 질문은 첫 댓글 문구로 돌려줌 (11/11 사용자 지시).
  split_caption(text) -> (caption, comment)"""
import re

def split_caption(text):
    comment, kept = "", []
    for line in text.split("\n"):
        s = line.strip()
        if s.startswith("💬"):
            comment = re.sub(r"\s*댓글로[^.!?]*주세요[.!]?\s*$", "", s).strip()
            continue
        if s.startswith("📌"):
            continue
        kept.append(line)
    cap = re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip()
    return cap, comment
