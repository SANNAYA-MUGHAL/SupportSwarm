import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.database.session import AsyncSessionLocal, async_engine
from app.database.base import Base
from app.seed.seed_data import seed_database
import app.models  # Register all models on Base

async def main():
    print("Ensuring database tables exist...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Running comprehensive database seeding...")
    async with AsyncSessionLocal() as session:
        await seed_database(session)
    print("Database seeding completed!")

if __name__ == "__main__":
    asyncio.run(main())
