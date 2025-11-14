import os

# Temporal Configuration
TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost:7233")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")

ORDER_TASK_QUEUE = "order-tq"
SHIPPING_TASK_QUEUE = "shipping-tq"

# Database Configuration
# IMPORTANT: Set DB_URL environment variable in production!
# Format: postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DATABASE
DB_USER = os.getenv("DB_USER", "trellis")
DB_PASSWORD = os.getenv("DB_PASSWORD")  # No default - must be set!
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "trellis")

# Construct DB_URL from components or use direct override
if os.getenv("DB_URL"):
    DB_URL = os.getenv("DB_URL")
elif DB_PASSWORD:
    DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # Development fallback - DO NOT USE IN PRODUCTION
    import warnings
    warnings.warn(
        "DB_PASSWORD not set! Using insecure default for development only. "
        "Set DB_PASSWORD environment variable in production!",
        UserWarning
    )
    DB_URL = f"postgresql+psycopg2://{DB_USER}:trellis@{DB_HOST}:{DB_PORT}/{DB_NAME}"
