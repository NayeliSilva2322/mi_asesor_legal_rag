# Mi Asesor Legal — servicio RAG en produccion

Reescritura del notebook `RAG_mi_asesor_legal.ipynb` como un servicio dockerizado,
con **Postgres + pgvector** como unica base de datos (reemplaza a Chroma y a
Google Drive) y una API HTTP en lugar de celdas de notebook.

## Que cambio respecto al notebook

| Notebook (Colab) | Este proyecto |
|---|---|
| Chroma local (`persist_directory="chroma_db"`) | Postgres + extension `pgvector` |
| Documentos en Google Drive | Carpeta `./data` montada en el contenedor (o subida via API) |
| Token de Hugging Face hardcodeado (`hf_auth = 'token'`) | Variable de entorno `HF_TOKEN` en `.env` (nunca en el codigo) |
| Modelo Llama cargado en el mismo proceso Python | Servido aparte por un contenedor de inferencia (TGI) u otro endpoint compatible, configurable via `LLM_BASE_URL` |
| Ejecucion manual celda por celda | `docker compose up`, endpoints HTTP, script de ingesta reutilizable |
| Sin logs de las consultas | Tabla `query_logs` con pregunta, respuesta y fuentes usadas (trazabilidad, clave en un dominio legal) |

## Arquitectura

```
                     ┌─────────────┐
  archivos .txt ───► │   api (FastAPI)  │ ───► Postgres + pgvector
  (./data o upload)  │  embeddings +    │      (documents, chunks, query_logs)
                     │  retrieval       │
                     └────────┬────────┘
                              │ HTTP (prompt + contexto)
                              ▼
                     ┌─────────────┐
                     │  llm (TGI)  │  <- opcional, perfil "llm"
                     │  o endpoint │     (o apunta a un servicio externo)
                     │  externo    │
                     └─────────────┘
```

- **Embeddings**: `sentence-transformers/all-mpnet-base-v2` (igual que el notebook),
  corren en CPU dentro del contenedor `api`. Si el corpus es mayormente en espanol,
  considera cambiar `EMBEDDING_MODEL` a algo multilingue como
  `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (requiere re-ingestar).
- **Retrieval**: similitud coseno via pgvector, con indice `hnsw`.
- **LLM**: el backend NO viene embebido en la imagen de la API (una imagen con
  Llama-2-13B en 4-bit pesa varios GB y necesita GPU en runtime, no en el build).
  En su lugar, `LLM_BASE_URL` apunta a cualquier endpoint compatible con TGI:
  - el contenedor `llm` incluido (perfil opcional, requiere GPU + `nvidia-container-toolkit`), o
  - un servicio de inferencia que ya tengas corriendo en otro servidor/GPU.

## Requisitos

- Docker y Docker Compose
- Si vas a levantar el perfil `llm` local: GPU NVIDIA + `nvidia-container-toolkit`
- Un token de Hugging Face con acceso al modelo `NAYEIRN23/mi-asesor-legal` (o al que uses)

## Puesta en marcha

```bash
cp .env.example .env
# edita .env: contraseñas, HF_TOKEN, y LLM_BASE_URL si usas un servidor externo

# Solo API + Postgres (LLM_BASE_URL debe apuntar a un servidor externo)
docker compose up -d --build

# O, si quieres levantar tambien el servidor de inferencia local (requiere GPU):
docker compose --profile llm up -d --build
```

Verifica que este arriba:

```bash
curl http://localhost:8000/health
```

## Ingestar documentos

1. Copia tus `.txt` (los expedientes) dentro de `./data/`.
2. Dispara la ingesta:

```bash
curl -X POST http://localhost:8000/api/v1/documents/ingest-folder
```

O sin tocar el volumen, subiendo archivos directamente:

```bash
curl -X POST http://localhost:8000/api/v1/documents/ingest-upload \
  -F "files=@expediente1.txt" -F "files=@expediente2.txt"
```

Tambien puedes ingestar desde dentro del contenedor con el CLI:

```bash
docker compose exec api python -m scripts.ingest_cli --path /app/data
```

Listar lo ya ingestado:

```bash
curl http://localhost:8000/api/v1/documents
```

## Consultar (equivalente a `run_my_rag` del notebook)

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Cual es el estado del Expediente N 00114-2023-0-2001-JP-FC-07"}'
```

Respuesta:

```json
{
  "answer": "...",
  "sources": [
    {"document_id": 1, "filename": "...", "expediente": "00114-2023-0-2001-JP-FC-07", "chunk_index": 2, "content": "...", "score": 0.83}
  ]
}
```

Cada consulta y su respuesta quedan registradas en `query_logs` para auditoria.

## Variables de entorno (`.env`)

Ver `.env.example` para la lista completa: credenciales de Postgres, modelo de
embeddings, tamano/overlap de chunks, `top_k`, y todo lo relacionado al backend
del LLM (`LLM_BASE_URL`, `MODEL_ID`, `HF_TOKEN`, temperatura, etc. — mismos
valores que traia el notebook: `temperature=0.3`, `repetition_penalty=1.1`,
`max_new_tokens=512`).

## Estructura del proyecto

```
mi-asesor-legal/
├── docker-compose.yml       # postgres + api + llm (opcional)
├── Dockerfile               # imagen de la API
├── requirements.txt
├── .env.example
├── db/init.sql              # extension pgvector + tablas (se corre solo al crear el volumen)
├── app/
│   ├── config.py            # settings via variables de entorno
│   ├── database.py          # engine/sesion SQLAlchemy
│   ├── models.py            # Document, Chunk (vector), QueryLog
│   ├── schemas.py           # esquemas Pydantic de la API
│   ├── embeddings.py        # wrapper de sentence-transformers
│   ├── text_splitter.py     # chunking (mismos parametros del notebook)
│   ├── llm_client.py        # cliente HTTP hacia el servidor de inferencia
│   ├── rag_service.py       # retrieval + generacion + logging
│   ├── ingestion.py         # carga de .txt -> chunks -> embeddings -> Postgres
│   ├── main.py               # app FastAPI
│   └── routers/              # /health, /query, /documents
├── scripts/ingest_cli.py    # ingesta por linea de comandos
└── tests/                    # pruebas basicas
```

## Notas de produccion / siguientes pasos sugeridos

- El indice `hnsw` de pgvector acelera el retrieval a medida que crece la tabla `chunks`.
- Agregar autenticacion (API key / OAuth) antes de exponer esto fuera de tu red interna.
- Si el volumen de documentos es grande, mover la ingesta a un job en background
  (Celery/RQ) en vez de bloquear el request HTTP.
- Rotar `HF_TOKEN` y las credenciales de Postgres antes de ir a produccion; no
  reutilizar los valores de ejemplo de `.env.example`.
