from temporal_app.db import engine
from sqlalchemy import text

def main():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("DB ok, result:", list(result))

if __name__ == "__main__":
    main()
