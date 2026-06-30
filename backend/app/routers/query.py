from fastapi import APIRouter

router = APIRouter()


@router.get("/query")
def placeholder_query():
    return {"message": "query endpoint coming soon!"}
