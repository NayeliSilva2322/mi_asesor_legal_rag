from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.embeddings import embed_query
from app.llm_client import generate_answer
from app.models import Chunk, Document, QueryLog

settings = get_settings()


def retrieve(db: Session, query: str, top_k: int | None = None) -> list[dict]:
    top_k = top_k or settings.top_k
    query_vector = embed_query(query)
    distance_expr = Chunk.embedding.cosine_distance(query_vector)

    stmt = (
        select(Chunk, Document.filename, Document.expediente, distance_expr.label("distance"))
        .join(Document, Chunk.document_id == Document.id)
        .order_by(distance_expr)
        .limit(top_k)
    )
    rows = db.execute(stmt).all()

    results = []
    for chunk, filename, expediente, distance in rows:
        results.append(
            {
                "document_id": chunk.document_id,
                "filename": filename,
                "expediente": expediente,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "score": 1 - float(distance),
            }
        )
    return results


def answer_query(db: Session, query: str, top_k: int | None = None) -> dict:
    sources = retrieve(db, query, top_k)
    context_chunks = [s["content"] for s in sources]
    answer = generate_answer(query, context_chunks)

    log = QueryLog(query=query, answer=answer, sources=sources)
    db.add(log)
    db.commit()

    return {"answer": answer, "sources": sources}
