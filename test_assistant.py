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
    assert assistant.validate_diary("   带有空格的日记内容   ") is True

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