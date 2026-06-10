import pytest
# 从你的文件里导入这个助手类
from personal_assistant import PersonalAssistant


@pytest.fixture
def assistant():
    """每个测试用例执行前，都会自动实例化一个助手对象"""
    return PersonalAssistant()


# ==========================================
# 1. 验证 功能1：收支限额检查 (check_transaction)
# ==========================================
def test_check_transaction(assistant):
    # 正常支出与收入
    assert assistant.check_transaction(-100) is True
    assert assistant.check_transaction(500) is True

    # 边界与超额支出 (阈值 5000)
    assert assistant.check_transaction(-5000) is True  # 刚好在边界
    assert assistant.check_transaction(-5000.1) is False  # 触发大额支出拦截

    # 边界与超额收入 (阈值 10000)
    assert assistant.check_transaction(10000) is True  # 刚好在边界
    assert assistant.check_transaction(10000.1) is False  # 触发大额收入拦截


# ==========================================
# 2. 验证 功能2：日记字数规范 (validate_diary)
# ==========================================
def test_validate_diary(assistant):
    # 正常字数
    assert assistant.validate_diary("今天天气真好，去公园散步了。") is True

    # 首尾空格干扰测试 (体现 strip() 的必要性)

    assert assistant.validate_diary("   这是一段带有首尾空格的日记内容   ") is True

    # 字数下限边界 (阈值 10)
    assert assistant.validate_diary("一二三四五六七八九十") is True  # 刚好10字
    assert assistant.validate_diary("小于十字") is False  # 太短
    assert assistant.validate_diary("          ") is False  # 全空格变0字

    # 字数上限边界 (阈值 200)
    assert assistant.validate_diary("A" * 200) is True  # 刚好200字
    assert assistant.validate_diary("A" * 201) is False  # 超过200字


# ==========================================
# 3. 验证 功能3：每日饮水量评标 (evaluate_water_intake)
# ==========================================
def test_evaluate_water_intake(assistant):
    # 异常值拦截
    assert assistant.evaluate_water_intake(-500) == "Invalid"

    # 各个健康区间与边界测试
    assert assistant.evaluate_water_intake(2500) == "Healthy"
    assert assistant.evaluate_water_intake(2000) == "Healthy"  # 刚好达到健康线

    assert assistant.evaluate_water_intake(1500) == "Warning"
    assert assistant.evaluate_water_intake(1000) == "Warning"  # 刚好达到预警线

    assert assistant.evaluate_water_intake(500) == "Danger"
    assert assistant.evaluate_water_intake(0) == "Danger"  # 滴水未进边界


# ==========================================
# 4. 验证 功能4：BMI 评级 (evaluate_bmi)
# ==========================================
def test_evaluate_bmi(assistant):
    # 非法输入：身高或体重 <= 0
    assert assistant.evaluate_bmi(0, 60) == "Invalid"
    assert assistant.evaluate_bmi(1.70, 0) == "Invalid"
    assert assistant.evaluate_bmi(-1.70, 60) == "Invalid"

    # 偏瘦：BMI < 18.5，例如 1.80m / 55kg ≈ 16.98
    assert assistant.evaluate_bmi(1.80, 55) == "Underweight"

    # 正常：BMI 在 [18.5, 24)，例如 1.70m / 60kg ≈ 20.76
    assert assistant.evaluate_bmi(1.70, 60) == "Normal"

    # 正常下边界：BMI = 18.5 (height=2.0, weight=74)
    assert assistant.evaluate_bmi(2.0, 74) == "Normal"

    # 超重：BMI 在 [24, 28)，例如 1.70m / 75kg ≈ 25.95
    assert assistant.evaluate_bmi(1.70, 75) == "Overweight"

    # 超重下边界：BMI = 24 (height=2.0, weight=96)
    assert assistant.evaluate_bmi(2.0, 96) == "Overweight"

    # 肥胖：BMI >= 28，例如 1.70m / 90kg ≈ 31.14
    assert assistant.evaluate_bmi(1.70, 90) == "Obese"

    # 肥胖下边界：BMI = 28 (height=2.0, weight=112)
    assert assistant.evaluate_bmi(2.0, 112) == "Obese"


# ==========================================
# 5. 验证 功能5：月度预算预警 (check_monthly_budget)
# ==========================================
def test_check_monthly_budget(assistant):
    # 非法预算
    assert assistant.check_monthly_budget(100, 0) == "Invalid"
    assert assistant.check_monthly_budget(100, -500) == "Invalid"

    # 退款大于支出 (spent < 0) 视为安全
    assert assistant.check_monthly_budget(-50, 1000) == "Safe"

    # 安全区间：ratio < 0.8
    assert assistant.check_monthly_budget(500, 1000) == "Safe"     # 0.5
    assert assistant.check_monthly_budget(799, 1000) == "Safe"     # 0.799

    # 预警下边界：ratio = 0.8
    assert assistant.check_monthly_budget(800, 1000) == "Warning"

    # 预警区间：0.8 <= ratio <= 1.0
    assert assistant.check_monthly_budget(1000, 1000) == "Warning"  # 刚好用完

    # 超支：ratio > 1.0
    assert assistant.check_monthly_budget(1001, 1000) == "Over"
    assert assistant.check_monthly_budget(3000, 1000) == "Over"


# ==========================================
# 6. 验证 功能6：睡眠时长评级 (evaluate_sleep)
# ==========================================
def test_evaluate_sleep(assistant):
    # 非法输入
    assert assistant.evaluate_sleep(-1) == "Invalid"
    assert assistant.evaluate_sleep(24.1) == "Invalid"

    # 不足：hours < 6
    assert assistant.evaluate_sleep(0) == "Insufficient"
    assert assistant.evaluate_sleep(5.9) == "Insufficient"

    # 健康下边界：hours = 6
    assert assistant.evaluate_sleep(6) == "Healthy"

    # 健康区间：[6, 9]
    assert assistant.evaluate_sleep(7.5) == "Healthy"

    # 健康上边界：hours = 9
    assert assistant.evaluate_sleep(9) == "Healthy"

    # 过量：hours > 9
    assert assistant.evaluate_sleep(9.1) == "Excessive"
    assert assistant.evaluate_sleep(24) == "Excessive"  # 24 小时仍属合法但过量