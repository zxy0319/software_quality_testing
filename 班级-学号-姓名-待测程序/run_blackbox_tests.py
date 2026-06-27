"""
黑盒测试执行脚本 —— 逐条执行 61 个黑盒测试用例
方法：等价类划分 + 边界值分析
"""
import sys
sys.path.insert(0, ".")
from personal_assistant import PersonalAssistant

pa = PersonalAssistant()
passed = 0
failed = 0
results = []

def run(case_id, func_name, actual, expected, detail=""):
    global passed, failed
    status = "PASS" if actual == expected else "FAIL"
    if status == "PASS":
        passed += 1
    else:
        failed += 1
    results.append((case_id, func_name, detail, expected, actual, status))
    print(f"  [{status}] {case_id} {func_name}: {detail} → 期望={expected}, 实际={actual}")
    if status == "FAIL":
        print(f"         ❌ 不一致！期望 {expected}，实际 {actual}")

print("=" * 72)
print("黑盒测试执行 - 个人助手 PersonalAssistant")
print("=" * 72)

# ============================================================
# 功能 1: check_transaction（收支限额检查）—— 9 条
# ============================================================
print("\n📋 功能 1: check_transaction（收支限额检查）")
print("-" * 48)

# B1-1 ~ B1-9
run("B1-1", "check_transaction", pa.check_transaction(-100), True, "V1 正常支出 -100")
run("B1-2", "check_transaction", pa.check_transaction(500), True, "V1 正常收入 500")
run("B1-3", "check_transaction", pa.check_transaction(-5000), True, "边界 = -5000")
run("B1-4", "check_transaction", pa.check_transaction(-5000.01), False, "边界 -5000-ε (I1)")
run("B1-5", "check_transaction", pa.check_transaction(-99999), False, "I1 严重超额支出")
run("B1-6", "check_transaction", pa.check_transaction(10000), True, "边界 = +10000")
run("B1-7", "check_transaction", pa.check_transaction(10000.01), False, "边界 +10000+ε (I2)")
run("B1-8", "check_transaction", pa.check_transaction(999999), False, "I2 严重超额收入")
run("B1-9", "check_transaction", pa.check_transaction(0), True, "特殊值 0")

# ============================================================
# 功能 2: validate_diary（日记字数规范）—— 10 条
# ============================================================
print("\n📋 功能 2: validate_diary（日记字数规范）")
print("-" * 48)

run("B2-1", "validate_diary", pa.validate_diary("今天天气真好，去公园散步了。"), True, "V1 区间内 14字")
run("B2-2", "validate_diary", pa.validate_diary("一二三四五六七八九十"), True, "边界=10（下限）")
run("B2-3", "validate_diary", pa.validate_diary("一二三四五六七八九"), False, "边界=9（I1）")
run("B2-4", "validate_diary", pa.validate_diary("嗨"), False, "I1 极短 1字")
run("B2-5", "validate_diary", pa.validate_diary("A" * 200), True, "边界=200（上限）")
run("B2-6", "validate_diary", pa.validate_diary("A" * 201), False, "边界=201（I2）")
run("B2-7", "validate_diary", pa.validate_diary("A" * 1000), False, "I2 极长 1000字")
run("B2-8", "validate_diary", pa.validate_diary("   这是一段带有首尾空格的日记内容   "), True, "V2 strip路径 15字")
run("B2-9", "validate_diary", pa.validate_diary("          "), False, "I3 全空格")
run("B2-10", "validate_diary", pa.validate_diary(""), False, "I3 空字符串")

# ============================================================
# 功能 3: evaluate_water_intake（饮水量评级）—— 10 条
# ============================================================
print("\n📋 功能 3: evaluate_water_intake（饮水量评级）")
print("-" * 48)

run("B3-1", "evaluate_water_intake", pa.evaluate_water_intake(2500), "Healthy", "V1 健康典型值 2500")
run("B3-2", "evaluate_water_intake", pa.evaluate_water_intake(2000), "Healthy", "边界=2000（V1下边界）")
run("B3-3", "evaluate_water_intake", pa.evaluate_water_intake(1999), "Warning", "边界=1999（V2上边界）")
run("B3-4", "evaluate_water_intake", pa.evaluate_water_intake(1500), "Warning", "V2 偏少典型值 1500")
run("B3-5", "evaluate_water_intake", pa.evaluate_water_intake(1000), "Warning", "边界=1000（V2下边界）")
run("B3-6", "evaluate_water_intake", pa.evaluate_water_intake(999), "Danger", "边界=999（V3上边界）")
run("B3-7", "evaluate_water_intake", pa.evaluate_water_intake(500), "Danger", "V3 缺水典型值 500")
run("B3-8", "evaluate_water_intake", pa.evaluate_water_intake(0), "Danger", "边界=0（V3下边界）")
run("B3-9", "evaluate_water_intake", pa.evaluate_water_intake(-1), "Invalid", "I1 非法 -1")
run("B3-10", "evaluate_water_intake", pa.evaluate_water_intake(-10000), "Invalid", "I1 非法极端 -10000")

# ============================================================
# 功能 4: evaluate_bmi（BMI 评级）—— 11 条
# ============================================================
print("\n📋 功能 4: evaluate_bmi（BMI 评级）")
print("-" * 48)

run("B4-1", "evaluate_bmi", pa.evaluate_bmi(0, 60), "Invalid", "I1 身高=0")
run("B4-2", "evaluate_bmi", pa.evaluate_bmi(-1.70, 60), "Invalid", "I1 身高<0")
run("B4-3", "evaluate_bmi", pa.evaluate_bmi(1.70, 0), "Invalid", "I2 体重=0")
run("B4-4", "evaluate_bmi", pa.evaluate_bmi(1.70, -50), "Invalid", "I2 体重<0")
run("B4-5", "evaluate_bmi", pa.evaluate_bmi(1.80, 55), "Underweight", "V1 偏瘦典型值 BMI≈16.98")
run("B4-6", "evaluate_bmi", pa.evaluate_bmi(2.00, 74), "Normal", "边界 BMI=18.5（V2下边界）")
run("B4-7", "evaluate_bmi", pa.evaluate_bmi(1.70, 60), "Normal", "V2 正常典型值 BMI≈20.76")
run("B4-8", "evaluate_bmi", pa.evaluate_bmi(2.00, 96), "Overweight", "边界 BMI=24.0（V3下边界）")
run("B4-9", "evaluate_bmi", pa.evaluate_bmi(1.70, 75), "Overweight", "V3 超重典型值 BMI≈25.95")
run("B4-10", "evaluate_bmi", pa.evaluate_bmi(2.00, 112), "Obese", "边界 BMI=28.0（V4下边界）")
run("B4-11", "evaluate_bmi", pa.evaluate_bmi(1.70, 90), "Obese", "V4 肥胖典型值 BMI≈31.14")

# ============================================================
# 功能 5: check_monthly_budget（月度预算预警）—— 10 条
# ============================================================
print("\n📋 功能 5: check_monthly_budget（月度预算预警）")
print("-" * 48)

run("B5-1", "check_monthly_budget", pa.check_monthly_budget(100, 0), "Invalid", "I1 预算=0")
run("B5-2", "check_monthly_budget", pa.check_monthly_budget(100, -500), "Invalid", "I1 预算<0")
run("B5-3", "check_monthly_budget", pa.check_monthly_budget(-50, 1000), "Safe", "V4 退款大于支出")
run("B5-4", "check_monthly_budget", pa.check_monthly_budget(500, 1000), "Safe", "V1 安全区间 ratio=0.5")
run("B5-5", "check_monthly_budget", pa.check_monthly_budget(799, 1000), "Safe", "边界 ratio=0.799")
run("B5-6", "check_monthly_budget", pa.check_monthly_budget(800, 1000), "Warning", "边界 ratio=0.8（V2下边界）")
run("B5-7", "check_monthly_budget", pa.check_monthly_budget(900, 1000), "Warning", "V2 预警典型值 ratio=0.9")
run("B5-8", "check_monthly_budget", pa.check_monthly_budget(1000, 1000), "Warning", "边界 ratio=1.0（V2上边界）")
run("B5-9", "check_monthly_budget", pa.check_monthly_budget(1001, 1000), "Over", "边界 ratio=1.001（V3下边界）")
run("B5-10", "check_monthly_budget", pa.check_monthly_budget(3000, 1000), "Over", "V3 严重超支 ratio=3.0")

# ============================================================
# 功能 6: evaluate_sleep（睡眠时长评级）—— 11 条
# ============================================================
print("\n📋 功能 6: evaluate_sleep（睡眠时长评级）")
print("-" * 48)

run("B6-1", "evaluate_sleep", pa.evaluate_sleep(-1), "Invalid", "I1 负值")
run("B6-2", "evaluate_sleep", pa.evaluate_sleep(24.1), "Invalid", "I1 超出24")
run("B6-3", "evaluate_sleep", pa.evaluate_sleep(-9999), "Invalid", "I1 极端非法")
run("B6-4", "evaluate_sleep", pa.evaluate_sleep(3), "Insufficient", "V1 不足典型值 3h")
run("B6-5", "evaluate_sleep", pa.evaluate_sleep(5.9), "Insufficient", "边界=5.9（V1上边界）")
run("B6-6", "evaluate_sleep", pa.evaluate_sleep(6), "Healthy", "边界=6（V2下边界）")
run("B6-7", "evaluate_sleep", pa.evaluate_sleep(7.5), "Healthy", "V2 健康典型值 7.5h")
run("B6-8", "evaluate_sleep", pa.evaluate_sleep(9), "Healthy", "边界=9（V2上边界）")
run("B6-9", "evaluate_sleep", pa.evaluate_sleep(9.1), "Excessive", "边界=9.1（V3下边界）")
run("B6-10", "evaluate_sleep", pa.evaluate_sleep(12), "Excessive", "V3 过量典型值 12h")
run("B6-11", "evaluate_sleep", pa.evaluate_sleep(24), "Excessive", "边界=24（V3上边界）")

# ============================================================
# 汇总
# ============================================================
print()
print("=" * 72)
print("黑盒测试结果汇总")
print("=" * 72)
total = passed + failed
print(f"  总计: {total} 条")
print(f"  ✅ Pass: {passed} / {total} ({passed/total*100:.1f}%)")
print(f"  ❌ Fail: {failed} / {total} ({failed/total*100:.1f}%)")

# 按功能统计
print()
print("按功能统计:")
funcs = {}
for r in results:
    fname = r[1]
    if fname not in funcs:
        funcs[fname] = {"pass": 0, "fail": 0, "total": 0}
    funcs[fname]["total"] += 1
    if r[5] == "PASS":
        funcs[fname]["pass"] += 1
    else:
        funcs[fname]["fail"] += 1

for fname, stats in funcs.items():
    pct = stats["pass"] / stats["total"] * 100
    bar = "✅" if stats["fail"] == 0 else "⚠️"
    print(f"  {bar} {fname}: {stats['pass']}/{stats['total']} ({pct:.0f}%)")

print()
if failed == 0:
    print("🎉 所有 61 条黑盒测试用例全部通过！")
else:
    print(f"⚠️  有 {failed} 条用例失败，详情见上方输出。")
    print()
    print("失败用例列表:")
    for r in results:
        if r[5] == "FAIL":
            print(f"  [{r[0]}] {r[2]} → 期望={r[3]}, 实际={r[4]}")

sys.exit(0 if failed == 0 else 1)
