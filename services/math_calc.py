def calculate_bmi(weight: float, height_cm: float) -> float:
    """Обчислює індекс маси тіла (ІМТ)."""
    if height_cm <= 0:
        return 0.0
    height_m = height_cm / 100
    return round(weight / (height_m ** 2), 2)


def calculate_bmr(weight: float, height_cm: float, age: int, gender: str) -> float:
    """Обчислює базову норму калорій (BMR) за формулою Міффліна-Сан Жеора."""
    base_bmr = 10 * weight + 6.25 * height_cm - 5 * age

    if gender.lower() == 'чоловік':
        return round(base_bmr + 5, 2)
    elif gender.lower() == 'жінка':
        return round(base_bmr - 161, 2)

    return round(base_bmr, 2)