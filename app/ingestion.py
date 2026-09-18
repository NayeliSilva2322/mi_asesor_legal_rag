import glob
import os
import re

from sqlalchemy.orm import Session

from app.embeddings import embed_texts
from app.models import Chunk, Document
from app.text_splitter import split_text


def ingest_folder(db: Session, folder_path: str) -> tuple[int, int]:
    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
    total_docs = 0
    total_chunks = 0

    for path in txt_files:
        with open(path, encoding="utf-8") as f:
            content = f.read()

        filename = os.path.basename(path)
        expediente = _extract_expediente(filename, content)

        document = Document(filename=filename, expediente=expediente, content=content)
        db.add(document)
        db.flush()  # asigna document.id antes de crear los chunks

        chunks = split_text(content)
        if chunks:
            vectors = embed_texts(chunks)
            for idx, (chunk_text, vector) in enumerate(zip(chunks, vectors)):
                db.add(
                    Chunk(
                        document_id=document.id,
                        chunk_index=idx,
                        content=chunk_text,
                        embedding=vector,
                    )
                )
            total_chunks += len(chunks)

        total_docs += 1

    db.commit()
    return total_docs, total_chunks


def _extract_expediente(filename: str, content: str) -> str | None:
    match = re.search(r"Expediente\s*N[o°º]?\s*([\d\-A-Z]+)", content, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"(\d{5}-\d{4}-\d-\d{4}-[A-Z]{2}-[A-Z]{2}-\d{2})", filename)
    if match:
        return match.group(1)
    return None
