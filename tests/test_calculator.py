from services.math_calc import calculate_bmi, calculate_bmr


# ---------- BMI TESTS ----------

def test_bmi_normal():
    result = calculate_bmi(95, 185)
    assert round(result, 2) == 27.76


def test_bmi_low():
    result = calculate_bmi(50, 185)
    assert result < 18.5


def test_bmi_overweight():
    result = calculate_bmi(90, 175)
    assert result > 25


def test_bmi_obesity():
    result = calculate_bmi(120, 170)
    assert result > 35


def test_bmi_round_value():
    result = calculate_bmi(80, 180)
    assert round(result, 2) == 24.69


# ---------- BMR TESTS ----------

def test_bmr_male():
    result = calculate_bmr(95, 185, 18, "Чоловік")
    assert result > 2000


def test_bmr_female():
    result = calculate_bmr(60, 165, 22, "Жінка")
    assert result > 1300


def test_bmr_gender_difference():
    male = calculate_bmr(80, 180, 25, "Чоловік")
    female = calculate_bmr(80, 180, 25, "Жінка")
    assert male > female


def test_bmr_age_difference():
    young = calculate_bmr(80, 180, 20, "Чоловік")
    old = calculate_bmr(80, 180, 50, "Чоловік")
    assert young > old


def test_bmr_weight_difference():
    light = calculate_bmr(60, 180, 25, "Чоловік")
    heavy = calculate_bmr(100, 180, 25, "Чоловік")
    assert heavy > light