import tkinter as tk
from tkinter import ttk, messagebox
# 导入你已经扩展至 6 个功能的核心业务类
from personal_assistant import PersonalAssistant


class AssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("智幼助手 - 6大核心功能全量管理面板")
        self.root.geometry("550x650")
        self.root.configure(bg="#f5f5f5")

        # 实例化扩展后的底层业务核心（底层引擎）
        self.backend = PersonalAssistant()

        # 使用 ttk.Notebook 实现多标签页布局，让界面更整洁、不拥挤
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)

        # 初始化 6 个功能的界面
        self._create_finance_tab()  # 记账模块 (功能1 & 功能5)
        self._create_life_tab()  # 生活记录 (功能2 & 功能6)
        self._create_health_tab()  # 身体健康 (功能3 & 功能4)

    # ==========================================
    # 模块一：记账助手（功能1：交易检查 & 功能5：月度预算）
    # ==========================================
    def _create_finance_tab(self):
        tab = tk.Frame(self.notebook, bg="#f5f5f5", padx=10, pady=10)
        self.notebook.add(tab, text="  记账助手  ")

        # 功能 1：收支限额检查
        frame_tx = tk.LabelFrame(tab, text=" 单笔收支额度拦截 (功能1) ", padx=10, pady=10, bg="#f5f5f5")
        frame_tx.pack(fill="x", pady=10)
        tk.Label(frame_tx, text="单笔金额 (正数代表收入，负数代表支出):", bg="#f5f5f5").pack(anchor="w")
        self.entry_amount = tk.Entry(frame_tx, width=35)
        self.entry_amount.pack(side="left", padx=5, pady=5)
        tk.Button(frame_tx, text="校验单笔", command=self.handle_transaction, bg="#e1e1e1").pack(side="left", padx=5)

        # 功能 5：月度预算预警
        frame_bg = tk.LabelFrame(tab, text=" 月度预算状态分析 (功能5) ", padx=10, pady=10, bg="#f5f5f5")
        frame_bg.pack(fill="x", pady=10)
        tk.Label(frame_bg, text="本月已花金额 (元):", bg="#f5f5f5").pack(anchor="w")
        self.entry_spent = tk.Entry(frame_bg, width=35)
        self.entry_spent.pack(pady=2)
        tk.Label(frame_bg, text="本月总预算金额 (元):", bg="#f5f5f5").pack(anchor="w")
        self.entry_budget = tk.Entry(frame_bg, width=35)
        self.entry_budget.pack(pady=2)
        tk.Button(frame_bg, text="评估预算状态", command=self.handle_monthly_budget, bg="#e1e1e1").pack(anchor="e",
                                                                                                        pady=5)

    # ==========================================
    # 模块二：生活助手（功能2：日记规范 & 功能6：睡眠时长）
    # ==========================================
    def _create_life_tab(self):
        tab = tk.Frame(self.notebook, bg="#f5f5f5", padx=10, pady=10)
        self.notebook.add(tab, text="  生活助手  ")

        # 功能 2：记录生活 - 日记字数
        frame_diary = tk.LabelFrame(tab, text=" 随手记 - 日记字数质检 (功能2) ", padx=10, pady=10, bg="#f5f5f5")
        frame_diary.pack(fill="x", pady=10)
        tk.Label(frame_diary, text="日记内容 (字数限制 10-200 字):", bg="#f5f5f5").pack(anchor="w")
        self.text_diary = tk.Text(frame_diary, height=5, width=50)
        self.text_diary.pack(pady=5)
        tk.Button(frame_diary, text="提交保存", command=self.handle_diary, bg="#e1e1e1").pack(anchor="e")

        # 功能 6：生活助手 - 睡眠评级
        frame_sleep = tk.LabelFrame(tab, text=" 睡眠健康监测 (功能6) ", padx=10, pady=10, bg="#f5f5f5")
        frame_sleep.pack(fill="x", pady=10)
        tk.Label(frame_sleep, text="昨晚睡眠时长 (小时):", bg="#f5f5f5").pack(anchor="w")
        self.entry_sleep = tk.Entry(frame_sleep, width=35)
        self.entry_sleep.pack(side="left", padx=5, pady=5)
        tk.Button(frame_sleep, text="分析睡眠", command=self.handle_sleep, bg="#e1e1e1").pack(side="left", padx=5)

    # ==========================================
    # 模块三：健康助手（功能3：饮水量 & 功能4：BMI计算）
    # ==========================================
    def _create_health_tab(self):
        tab = tk.Frame(self.notebook, bg="#f5f5f5", padx=10, pady=10)
        self.notebook.add(tab, text="  健康助手  ")

        # 功能 3：每日饮水量评标
        frame_water = tk.LabelFrame(tab, text=" 饮水打卡 (功能3) ", padx=10, pady=10, bg="#f5f5f5")
        frame_water.pack(fill="x", pady=10)
        tk.Label(frame_water, text="今日饮水量 (毫升 ml):", bg="#f5f5f5").pack(anchor="w")
        self.entry_water = tk.Entry(frame_water, width=35)
        self.entry_water.pack(side="left", padx=5, pady=5)
        tk.Button(frame_water, text="提交评估", command=self.handle_water, bg="#e1e1e1").pack(side="left", padx=5)

        # 功能 4：BMI 评级
        frame_bmi = tk.LabelFrame(tab, text=" 身体质量指数 BMI 分析 (功能4) ", padx=10, pady=10, bg="#f5f5f5")
        frame_bmi.pack(fill="x", pady=10)
        tk.Label(frame_bmi, text="身高 (米 m，例如 1.75):", bg="#f5f5f5").pack(anchor="w")
        self.entry_height = tk.Entry(frame_bmi, width=35)
        self.entry_height.pack(pady=2)
        tk.Label(frame_bmi, text="体重 (公斤 kg，例如 65.5):", bg="#f5f5f5").pack(anchor="w")
        self.entry_weight = tk.Entry(frame_bmi, width=35)
        self.entry_weight.pack(pady=2)
        tk.Button(frame_bmi, text="计算 BMI 评级", command=self.handle_bmi, bg="#e1e1e1").pack(anchor="e", pady=5)

    # ==========================================
    # 后端核心业务映射逻辑（事件处理器）
    # ==========================================
    def handle_transaction(self):
        try:
            amount = float(self.entry_amount.get())
            is_safe = self.backend.check_transaction(amount)
            if is_safe:
                messagebox.showinfo("提示", "金额正常，已成功记录该笔账单。")
            else:
                messagebox.showwarning("大额风控", "⚠️ 触发大额风控提醒！支出已超 5000 或收入已超 10000，请二次核对。")
        except ValueError:
            messagebox.showerror("格式错误", "请输入有效的数字！")

    def handle_monthly_budget(self):
        try:
            spent = float(self.entry_spent.get())
            budget = float(self.entry_budget.get())
            status = self.backend.check_monthly_budget(spent, budget)

            if status == "Invalid":
                messagebox.showerror("错误", "预算总额必须大于 0！")
            elif status == "Safe":
                messagebox.showinfo("预算状态", "🟢 安全（Safe）：本月消费节奏良好，在合理预算范围内。")
            elif status == "Warning":
                messagebox.showwarning("预算预警", "🟡 预警（Warning）：本月开销已达预算 80% 以上！请注意节制。")
            elif status == "Over":
                messagebox.showerror("超支告警", "🔴 严重超支（Over）：本月开销已穿透总预算，请立刻控制消费！")
        except ValueError:
            messagebox.showerror("格式错误", "金额请输入有效的整数或浮点数！")

    def handle_diary(self):
        content = self.text_diary.get("1.0", tk.END)
        is_valid = self.backend.validate_diary(content)
        if is_valid:
            messagebox.showinfo("成功", "🎉 日记字数合规，生活随笔已成功存档。")
        else:
            messagebox.showerror("规范拦截", "❌ 存档失败！去首尾空格后核心文本需在 10 到 200 字之间。")

    def handle_sleep(self):
        try:
            hours = float(self.entry_sleep.get())
            result = self.backend.evaluate_sleep(hours)

            if result == "Invalid":
                messagebox.showerror("异常数据", "时间输入非法！睡眠时长必须在 0 到 24 小时之间。")
            elif result == "Insufficient":
                messagebox.showwarning("睡眠报告",
                                       "⚠️ 评级：Insufficient（睡眠不足）。长期低于 6 小时会降低免疫力，请早点休息！")
            elif result == "Healthy":
                messagebox.showinfo("睡眠报告", "🟢 评级：Healthy（优质睡眠）。达到了 6-9 小时的标准健康区间。")
            elif result == "Excessive":
                messagebox.showwarning("睡眠报告",
                                       "🟡 评级：Excessive（睡眠过多）。睡眠超 9 小时，请关注作息规律，避免越睡越累。")
        except ValueError:
            messagebox.showerror("格式错误", "请输入有效的睡眠小时数（可带小数）！")

    def handle_water(self):
        try:
            water = int(self.entry_water.get())
            result = self.backend.evaluate_water_intake(water)

            if result == "Invalid":
                messagebox.showerror("数据异常", "饮水量怎么可能是负数呢？请输入正确数值。")
            elif result == "Healthy":
                messagebox.showinfo("饮水评估", "🟢 评级：Healthy。恭喜达到每日 2000ml 的基础需水线！")
            elif result == "Warning":
                messagebox.showwarning("饮水评估", "🟡 评级：Warning。当前饮水偏少（1000ml - 1999ml），请及时补水。")
            elif result == "Danger":
                messagebox.showerror("脱水警告", "🔴 评级：Danger！严重缺水（不足 1000ml），身体正在发出警报，请立刻喝水！")
        except ValueError:
            messagebox.showerror("格式错误", "请输入合法的整数毫升数！")

    def handle_bmi(self):
        try:
            height = float(self.entry_height.get())
            weight = float(self.entry_weight.get())
            result = self.backend.evaluate_bmi(height, weight)

            if result == "Invalid":
                messagebox.showerror("非法输入", "身高和体重必须是大于 0 的物理正数！")
            elif result == "Underweight":
                messagebox.showwarning("BMI 报告", "⚪ 评级：Underweight（偏瘦）。国标 BMI < 18.5，请注意补充营养。")
            elif result == "Normal":
                messagebox.showinfo("BMI 报告", "🟢 评级：Normal（正常）。体型非常标准，请继续保持健康生活方式。")
            elif result == "Overweight":
                messagebox.showwarning("BMI 报告",
                                       "🟡 评级：Overweight（超重）。国标 BMI 在 [24, 28) 之间，慢性病风险上升，注意控制饮食。")
            elif result == "Obese":
                messagebox.showerror("严重警告", "🔴 评级：Obese（肥胖）。国标 BMI >= 28，属于高风险体型，请立刻关注体重管理！")
        except ValueError:
            messagebox.showerror("格式错误", "身高或体重输入不合法，请输入标准的数字。")


if __name__ == "__main__":
    root = tk.Tk()
    # 应用统一的清爽样式风格
    style = ttk.Style()
    style.theme_use('clam')
    app = AssistantGUI(root)
    root.mainloop()