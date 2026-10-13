from app import notify


def test_message_kg_and_lb():
    m = {"measured_at": "2026-10-12T07:30:00", "weight_kg": 80.0, "impedance": 500,
         "metrics": {"body_fat": 20.0, "fat_mass": 16.0, "muscle_mass": 60.0, "water": 55.0, "protein": 18.0,
                     "bone_mass": 3.0, "bmi": 25.2, "visceral_fat": 9, "bmr": 1700}}
    prev = {"measured_at": "2026-10-11T07:30:00", "weight_kg": 80.5}
    profile = {"name": "Alex", "height_cm": 178, "birth": "1990-01-01"}
    text = notify.message(m, profile, [prev], "kg", "en")
    assert text.startswith("⚖️ Alex · 80.00 kg")
    assert "−0.50 kg since" in text and "Impedance 500 Ω" in text
    assert "176.37 lb" in notify.message(m, profile, [], "lb", "en")
    assert "80,00 kg" in notify.message(m, profile, [], "kg", "pt-BR")


def test_unknown_person():
    m = {"measured_at": "2026-10-12T07:30:00", "weight_kg": 80.0, "metrics": {}}
    assert "doesn't match any profile" in notify.message(m, None, [], "kg", "en")


def test_chinese_measurement_and_missing_impedance():
    m = {"measured_at": "2026-10-12T07:30:00", "weight_kg": 80.0, "impedance": 500,
         "metrics": {"body_fat": 20.0, "fat_mass": 16.0, "muscle_mass": 60.0, "water": 55.0,
                     "protein": 18.0, "bone_mass": 3.0, "bmi": 25.2, "visceral_fat": 9, "bmr": 1700}}
    profile = {"name": "小明", "height_cm": 178, "birth": "1990-01-01"}
    prev = {"measured_at": "2026-10-11T07:30:00", "weight_kg": 80.5}
    text = notify.message(m, profile, [prev], "kg", "zh-CN")
    assert "体脂率 20.0%" in text and "阻抗 500 Ω" in text
    assert "较 10月11日 07:30 变化 −0.50 kg" in text
    assert "176.37 lb" in notify.message(m, profile, [], "lb", "zh-CN")
    assert "未识别用户" in notify.message(m, None, [], "kg", "zh-CN")
    m["impedance"] = None
    assert "请赤脚站上秤" in notify.message(m, profile, [], "kg", "zh-CN")
    a = {"week_start": "2026-10-04", "week_end": "2026-10-10", "text": "本周体重下降。"}
    assert "本周分析：小明（10月04日至10月10日）" in notify.analysis_message(a, profile, "zh-CN")
