import os

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost:7233")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")

ORDER_TASK_QUEUE = "order-tq"
SHIPPING_TASK_QUEUE = "shipping-tq"

DB_URL = os.getenv(
    "DB_URL",
    "postgresql+psycopg2://trellis:trellis@127.0.0.1:5432/trellis",
)
