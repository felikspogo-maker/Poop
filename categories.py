"""Определение конкурсной категории по возрасту и семейному положению."""

# Варианты семейного положения
MARITAL_SINGLE = "Не замужем"
MARITAL_DIVORCED = "Разведена"
MARITAL_MARRIED = "Замужем"

MARITAL_OPTIONS = [MARITAL_SINGLE, MARITAL_DIVORCED, MARITAL_MARRIED]

# Категории конкурса
CATEGORIES = {
    "young_miss": "👑 Young Miss Russia Earth (14–18 лет)",
    "ms": "👑 Ms Russia Earth (18–40 лет)",
    "mrs": "👑 Mrs Russia Earth (18–45 лет)",
    "classic_mrs": "👑 Classic Mrs Russia Earth (45–60 лет)",
}


def suggest_category(age: int, marital: str) -> str:
    """Подбирает предполагаемую категорию.

    Финальное распределение по категориям остаётся за организаторами —
    здесь мы лишь подсказываем участнице наиболее подходящую.

    Логика:
      • 14–18 лет                         → Young Miss
      • 45–60 лет                         → Classic Mrs
      • замужем (18–45)                   → Mrs
      • не замужем / разведена (18–40)    → Ms
      • не замужем / разведена (40–45)    → Mrs
    """
    is_married = marital == MARITAL_MARRIED

    if 14 <= age <= 18:
        return CATEGORIES["young_miss"]
    if 45 <= age <= 60:
        return CATEGORIES["classic_mrs"]
    if is_married:
        return CATEGORIES["mrs"]
    if 18 <= age <= 40:
        return CATEGORIES["ms"]
    # 40–45, не замужем/разведена
    return CATEGORIES["mrs"]
