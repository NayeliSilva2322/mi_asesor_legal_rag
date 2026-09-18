from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.rag_service import answer_query
from app.schemas import QueryRequest, QueryResponse

router = APIRouter(prefix="/api/v1")


@router.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest, db: Session = Depends(get_db)):
    return answer_query(db, payload.query, payload.top_k)
