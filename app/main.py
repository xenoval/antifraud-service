from fastapi import FastAPI, Request, HTTPException
from app.schemas import AntifraudRequest, AntifraudResponse
from app.logic import check_antifraud
from app.metrics import REQUESTS_TOTAL, REQUEST_DURATION, metrics_app
from app.healthz import router as healthz_router
import time

app = FastAPI(title="Antifraud Service")

@app.get("/")
async def root():
    return {
        "message": "Anti-Fraud Service",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "check": "/check",
            "metrics": "/metrics"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "anti-fraud"}


app.mount("/metrics", metrics_app)
app.include_router(healthz_router)

@app.post("/check", response_model=AntifraudResponse)
async def check_fraud(request: AntifraudRequest, http_request: Request) -> AntifraudResponse:
    start_time = time.time()
    
    try:
        response = check_antifraud(request)
        
        # Если есть стоп-факторы - считаем как "422" (бизнес-ошибка)
        if not response.result:
            status = "422"
        else:
            status = "200"
        
        return response
        
    except HTTPException as e:
        # Ошибки валидации FastAPI/Pydantic
        status = str(e.status_code)
        raise e
    except Exception as e:
        # Внутренние ошибки сервера
        status = "500"
        raise e
        
    finally:
        duration = time.time() - start_time
        
        REQUESTS_TOTAL.labels(
            method=http_request.method,
            endpoint="/check",
            status=status
        ).inc()
        
        REQUEST_DURATION.labels(
            method=http_request.method,
            endpoint="/check",
            status=status
        ).observe(duration)