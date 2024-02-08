from dataclasses import dataclass
import typing as t


@dataclass
class Supp:
    name: str
    morning: int | float = 0
    lunch: int | float = 0
    dinner: int | float = 0
    bedtime: int | float = 0
    days_per_week: int = 7
    units: t.Literal["caps", "mg", "g", "ml", "mcg", "mcl", "iu"] = "mg"
    winter_only: bool = False

    def __mul__(self, other: int) -> float:
        return self.quantity_per_day * other

    @property
    def quantity_per_day(self) -> float:
        return (
            sum([self.morning, self.lunch, self.dinner, self.bedtime])
            * self.days_per_week
            / 7
        )

