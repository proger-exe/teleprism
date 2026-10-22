"""Stars pricing service."""

from decimal import Decimal
from typing import Any

from teleprism.app.config import Settings
from teleprism.app.core.errors import ValidationError
from teleprism.app.core.money import money, quantize_usdt
from teleprism.app.repositories.packages import PackageRepository


class PricingService:
    """Calculate fixed checkout prices."""

    def __init__(self, packages: PackageRepository, settings: Settings) -> None:
        """Store dependencies."""

        self.packages = packages
        self.settings = settings

    async def validate_stars(self, stars_count: int) -> None:
        """Validate custom Stars amount."""

        if stars_count < self.settings.min_stars:
            raise ValidationError(f"Минимум: {self.settings.min_stars} Stars.")
        if stars_count > self.settings.max_stars:
            raise ValidationError(f"Максимум: {self.settings.max_stars} Stars.")
        if stars_count % self.settings.custom_stars_step != 0:
            raise ValidationError(f"Шаг: {self.settings.custom_stars_step} Stars.")

    async def price_for_stars(self, stars_count: int) -> dict[str, Any]:
        """Return a fixed price for package or active custom tariff."""

        await self.validate_stars(stars_count)
        package = await self.packages.find_by_stars(stars_count)
        if package is not None:
            return {
                "package_id": package["id"],
                "stars_count": stars_count,
                "unit_price": str(quantize_usdt(money(package["price_usdt"]) / Decimal(stars_count))),
                "base_amount": package["price_usdt"],
                "fixed_fee": "0",
                "total_amount": package["price_usdt"],
            }
        active = await self.packages.active()
        if not active:
            raise ValidationError("Нет активного тарифа.")
        best = max(
            (item for item in active if item["stars_count"] <= stars_count),
            key=lambda item: item["stars_count"],
            default=None,
        )
        if best is None:
            raise ValidationError("Нет активного тарифа для такого количества.")
        unit_price = money(best["price_usdt"]) / Decimal(int(best["stars_count"]))
        total = quantize_usdt(unit_price * Decimal(stars_count))
        return {
            "package_id": None,
            "stars_count": stars_count,
            "unit_price": str(quantize_usdt(unit_price)),
            "base_amount": str(total),
            "fixed_fee": "0",
            "total_amount": str(total),
        }
