from pydantic import BaseModel, ConfigDict


class QueryRequest(BaseModel):
    query: str
    top_k: int | None = None


class SourceChunk(BaseModel):
    document_id: int
    filename: str
    expediente: str | None = None
    chunk_index: int
    content: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    expediente: str | None
    num_chunks: int


class IngestResponse(BaseModel):
    ingested_documents: int
    ingested_chunks: int
