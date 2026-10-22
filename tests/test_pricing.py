"""Pricing service tests."""

from pathlib import Path

from teleprism.app.config import Settings
from teleprism.app.db.connection import Database
from teleprism.app.db.migrations import migrate
from teleprism.app.repositories.packages import PackageRepository
from teleprism.app.services.pricing_service import PricingService


async def test_pricing_uses_active_package(tmp_path: Path) -> None:
    """Package price is fixed from SQLite."""

    database = Database(tmp_path / "test.sqlite3")
    settings = Settings(database_path=tmp_path / "test.sqlite3")
    async with database.connect() as db:
        await migrate(db)
        service = PricingService(PackageRepository(db), settings)
        price = await service.price_for_stars(500)
    assert price["total_amount"] == "9.80"
    assert price["package_id"] is not None


async def test_custom_pricing_uses_best_lower_package(tmp_path: Path) -> None:
    """Custom price uses active tariff unit price."""

    database = Database(tmp_path / "test.sqlite3")
    settings = Settings(database_path=tmp_path / "test.sqlite3")
    async with database.connect() as db:
        await migrate(db)
        service = PricingService(PackageRepository(db), settings)
        price = await service.price_for_stars(750)
    assert price["total_amount"] == "14.700000"
    assert price["package_id"] is None
