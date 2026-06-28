from pathlib import Path
import asyncio
import os
import random
import time
from datetime import datetime, timedelta, timezone

import asyncpg
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

MERCHANTS = [
    "Dangote Supermart", "Shoprite Lagos", "Jumia Foods", "Konga Electronics",
    "GTBank Transfer", "Access Bank POS", "Zenith ATM", "First Bank Transfer",
    "Chicken Republic", "Tastee Fried Chicken", "Mr Biggs", "Dominos Pizza Lagos",
    "Slot Systems", "Fouani Nigeria", "Game Stores", "Spar Nigeria",
    "Total Energies", "NNPC Filling Station", "DHL Nigeria", "GIG Logistics",
]

STATUSES = ["success", "failed", "pending"]
WEIGHTS = [0.70, 0.20, 0.10]
TOTAL_ROWS = 1_000_000
BATCH_SIZE = 10_000


async def seed_database() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not set — check your .env file")
    start_time = time.perf_counter()

    conn = await asyncpg.connect(database_url)
    try:
        await conn.execute("DROP TABLE IF EXISTS transactions")
        await conn.execute(
            """
            CREATE TABLE transactions (
                id BIGSERIAL PRIMARY KEY,
                amount NUMERIC(10, 2) NOT NULL,
                merchant VARCHAR(100) NOT NULL,
                status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'failed', 'pending')),
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
        await conn.execute("CREATE INDEX idx_transactions_created_at ON transactions (created_at DESC)")
        await conn.execute("CREATE INDEX idx_transactions_id ON transactions (id DESC)")

        rng = random.Random(42)
        for row_index in range(0, TOTAL_ROWS, BATCH_SIZE):
            batch = []
            for _ in range(BATCH_SIZE):
                amount = round(rng.uniform(100.00, 500000.00), 2)
                merchant = rng.choice(MERCHANTS)
                status = rng.choices(STATUSES, weights=WEIGHTS, k=1)[0]
                created_at = datetime.now(timezone.utc) - timedelta(days=rng.randint(0, 730), hours=rng.randint(0, 23))
                batch.append((amount, merchant, status, created_at))

            await conn.executemany(
                "INSERT INTO transactions (amount, merchant, status, created_at) VALUES ($1, $2, $3, $4)",
                batch,
            )

            if row_index % 100_000 == 0:
                print(f"Inserted {row_index + BATCH_SIZE} rows...")

        elapsed = time.perf_counter() - start_time
        print(f"Seeded {TOTAL_ROWS} rows in {elapsed:.2f}s")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
