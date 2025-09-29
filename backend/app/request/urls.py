from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/")
def get_page(request: Request):
    path = request.scope["root_path"] + request.scope["route"].path
    return {f"You are on {path}"}
