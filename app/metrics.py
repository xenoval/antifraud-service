from prometheus_client import Counter, Histogram, make_asgi_app

# Количество запросов по статусам
REQUESTS_TOTAL = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Время обработки запроса
REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in second',
    ['method', 'endpoint', 'status']
)

metrics_app = make_asgi_app()