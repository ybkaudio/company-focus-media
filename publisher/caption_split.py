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


ASK_OLD = "첫 댓글에 답해 주세요 👇"


def question_into_caption(cap, question):
    """11/14 사용자: 첫 댓글은 달지 않고 질문은 설명란에. 새 형식(질문 줄 + '첫 댓글에 답해 주세요 👇')은
    그 줄만 '댓글로 알려 주세요.'로, 질문이 없는 옛 형식은 first_comment 질문을 🔗 줄(없으면 출처·해시태그) 앞에 넣음."""
    if ASK_OLD in cap:
        return cap.replace(ASK_OLD, "댓글로 알려 주세요.")
    q = (question or "").strip()
    if not q or q.split("?")[0] in cap:
        return cap
    paras = cap.split("\n\n")
    at = next((i for i, p in enumerate(paras) if p.lstrip().startswith(("🔗", "출처", "#"))), len(paras))
    paras.insert(at, q)
    return "\n\n".join(paras)
