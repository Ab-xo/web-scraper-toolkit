from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.services.ai_query_engine import run_query

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_html(payload: QueryRequest):
    try:
        result = await run_query(
            html=payload.html,
            intent=payload.intent,
            base_url=payload.base_url,
            max_results=payload.max_results,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Query failed: {exc}")
    return QueryResponse(**result)
