from fastapi import APIRouter, Response, status


router = APIRouter(
    prefix="/healthz",
    tags=["system"],
)

@router.get("/live")
async def liveness_probe() -> Response:
    """
    Простая проверка на то, что приложение запущено и работает.
    """
    return Response(status_code=status.HTTP_200_OK)
