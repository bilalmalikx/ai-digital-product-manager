from fastapi import APIRouter
from app.core.graph import build_graph

router = APIRouter()
graph = build_graph()

@router.post("/generate")
def generate_product(data: dict):
    result = graph.invoke({
        "input": data["idea"],
        "strategist_output": None,
        "prd_output": None
    })

    return result