"""CLI para ingestar en bloque una carpeta de archivos .txt hacia Postgres.

Uso:
    python -m scripts.ingest_cli --path data
"""
import argparse

from app.database import SessionLocal
from app.ingestion import ingest_folder


def main():
    parser = argparse.ArgumentParser(description="Ingesta documentos legales .txt en Postgres")
    parser.add_argument("--path", required=True, help="Carpeta que contiene los .txt")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        docs, chunks = ingest_folder(db, args.path)
        print(f"Ingestados {docs} documentos en {chunks} chunks.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
