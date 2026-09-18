import os
import shutil
import tempfile

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.ingestion import ingest_folder
from app.models import Chunk, Document
from app.schemas import DocumentOut, IngestResponse

router = APIRouter(prefix="/api/v1/documents")
settings = get_settings()


@router.get("", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    stmt = (
        select(Document, func.count(Chunk.id).label("num_chunks"))
        .join(Chunk, Chunk.document_id == Document.id, isouter=True)
        .group_by(Document.id)
    )
    rows = db.execute(stmt).all()
    return [
        DocumentOut(
            id=doc.id,
            filename=doc.filename,
            expediente=doc.expediente,
            num_chunks=num_chunks,
        )
        for doc, num_chunks in rows
    ]


@router.post("/ingest-folder", response_model=IngestResponse)
def ingest_from_data_dir(db: Session = Depends(get_db)):
    """Ingesta todos los .txt que estan actualmente en la carpeta montada DATA_DIR."""
    docs, chunks = ingest_folder(db, settings.data_dir)
    return IngestResponse(ingested_documents=docs, ingested_chunks=chunks)


@router.post("/ingest-upload", response_model=IngestResponse)
def ingest_uploaded_files(
    files: list[UploadFile] = File(...), db: Session = Depends(get_db)
):
    """Acepta uno o mas archivos .txt subidos directamente y los ingesta."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        for upload in files:
            dest = os.path.join(tmp_dir, upload.filename)
            with open(dest, "wb") as f:
                shutil.copyfileobj(upload.file, f)
        docs, chunks = ingest_folder(db, tmp_dir)
    return IngestResponse(ingested_documents=docs, ingested_chunks=chunks)
