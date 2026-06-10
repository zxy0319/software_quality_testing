"""
个人助手 GUI 应用程序

设计要点：
  - 6 个核心业务功能，每个功能独立一个 Tab，视觉上清晰区分
  - 每个 Tab 内含「输入区 + 操作按钮 + 历史记录列表」三段式布局
  - 记录持久化到 records.json，重启后历史仍在
  - GUI 层只负责输入收集、调用 backend、展示结果，不参与业务判定
  - 业务规则全部委托给 PersonalAssistant 类，保证可测性
"""
import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from personal_assistant import PersonalAssistant


RECORDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "records.json")

# 6 个功能在 records.json 中的分类键名
RECORD_KEYS = [
    "transaction",
    "diary",
    "water",
    "bmi",
    "budget",
    "sleep",
]


def load_all_records():
    """从 records.json 加载全部记录，文件不存在或损坏时返回空模板。"""
    if not os.path.exists(RECORDS_FILE):
        return {k: [] for k in RECORD_KEYS}
    try:
        with open(RECORDS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k in RECORD_KEYS:
            data.setdefault(k, [])
        return data
    except (json.JSONDecodeError, OSError):
        return {k: [] for k in RECORD_KEYS}


def save_all_records(data):
    """把全部记录写回 records.json。"""
    try:
        with open(RECORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        messagebox.showerror("保存失败", f"无法写入 records.json：{e}")


def now_iso():
    """返回当前时间的 ISO 字符串（精确到秒），便于字典序排序。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class AssistantGUI:
    """主窗口控制器，负责装配 6 个功能 Tab 和后端业务实例。"""

    def __init__(self, root):
        self.root = root
        self.root.title("智幼助手 - 6 大核心功能独立面板")
        self.root.geometry("780x640")
        self.root.configure(bg="#f5f5f5")

        # 业务核心引擎，所有判定规则在 PersonalAssistant 中
        self.backend = PersonalAssistant()

        # 全量记录字典：{ "transaction": [...], "diary": [...], ... }
        self.records = load_all_records()

        # 顶部信息条
        header = tk.Label(
            self.root,
            text="个人助手 PersonalAssistant ｜ 6 大独立功能 + 历史回顾",
            font=("Microsoft YaHei", 12, "bold"),
            bg="#2c3e50",
            fg="white",
            pady=10,
        )
        header.pack(fill="x")

        # Notebook，6 个 Tab 一一对应 6 个功能
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)

        # 每个 Tab 内的「历史记录」Listbox 句柄，便于追加后实时刷新
        self.history_widgets = {}

        # 依次创建 6 个 Tab
        self._create_tab_transaction()   # 功能 1
        self._create_tab_diary()         # 功能 2
        self._create_tab_water()         # 功能 3
        self._create_tab_bmi()           # 功能 4
        self._create_tab_budget()        # 功能 5
        self._create_tab_sleep()         # 功能 6

        # 启动时刷新所有 Tab 的历史列表
        for key in RECORD_KEYS:
            self._refresh_history(key)

    # ======================================================================
    # 通用工具：在 Tab 内构建「历史记录」区
    # ======================================================================
    def _build_history_area(self, parent, record_key, title="📜 历史记录（最近 10 条）"):
        frame = tk.LabelFrame(
            parent, text=title, padx=8, pady=8, bg="#ffffff",
            font=("Microsoft YaHei", 10, "bold"), fg="#34495e",
        )
        frame.pack(fill="both", expand=True, pady=(10, 0))

        listbox = tk.Listbox(
            frame, height=8, font=("Consolas", 10),
            bg="#fafafa", selectbackground="#3498db",
        )
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(frame, command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scrollbar.set)

        self.history_widgets[record_key] = listbox

    def _refresh_history(self, record_key):
        """从 self.records 取最近 10 条，刷新到对应 Listbox。"""
        listbox = self.history_widgets.get(record_key)
        if listbox is None:
            return
        listbox.delete(0, tk.END)
        recent = self.backend.get_recent_records(self.records.get(record_key, []))
        if not recent:
            listbox.insert(tk.END, "（暂无记录）")
            return
        for rec in recent:
            listbox.insert(tk.END, self._format_record(record_key, rec))

    def _format_record(self, record_key, rec):
        """把一条记录格式化成一行字符串展示。"""
        t = rec.get("time", "????-??-?? ??:??:??")
        if record_key == "transaction":
            return f"[{t}]  金额={rec.get('amount')}  状态={rec.get('result')}"
        if record_key == "diary":
            return f"[{t}]  字数={rec.get('length')}  结果={rec.get('result')}"
        if record_key == "water":
            return f"[{t}]  饮水={rec.get('ml')}ml  评级={rec.get('result')}"
        if record_key == "bmi":
            return f"[{t}]  身高={rec.get('height')}m 体重={rec.get('weight')}kg  评级={rec.get('result')}"
        if record_key == "budget":
            return f"[{t}]  已花={rec.get('spent')}/{rec.get('budget')}  状态={rec.get('result')}"
        if record_key == "sleep":
            return f"[{t}]  时长={rec.get('hours')}h  评级={rec.get('result')}"
        return str(rec)

    def _append_record(self, record_key, payload):
        """追加记录并立刻持久化、刷新 UI。"""
        payload["time"] = now_iso()
        self.records.setdefault(record_key, []).append(payload)
        save_all_records(self.records)
        self._refresh_history(record_key)

    # ======================================================================
    # 功能 1：单笔收支限额检查
    # ======================================================================
    def _create_tab_transaction(self):
        tab = tk.Frame(self.notebook, bg="#f5f5f5", padx=15, pady=15)
        self.notebook.add(tab, text="  1. 收支限额  ")

        title = tk.Label(
            tab, text="💰 功能 1：单笔收支限额风控",
            font=("Microsoft YaHei", 13, "bold"),
            bg="#f5f5f5", fg="#2980b9",
        )
        title.pack(anchor="w", pady=(0, 8))

        form = tk.LabelFrame(tab, text=" 输入区 ", padx=10, pady=10, bg="#ffffff")
        form.pack(fill="x")
        tk.Label(form, text="单笔金额（正=收入，负=支出）：", bg="#ffffff").pack(anchor="w")
        self.entry_amount = tk.Entry(form, width=40)
        self.entry_amount.pack(anchor="w", pady=4)
        tk.Button(
            form, text="校验本笔交易", command=self.handle_transaction,
            bg="#3498db", fg="white", padx=12, pady=4,
        ).pack(anchor="e")

        self._build_history_area(tab, "transaction")

    def handle_transaction(self):
        raw = self.entry_amount.get().strip()
        try:
            amount = float(raw)
        except ValueError:
            messagebox.showerror("格式错误", "请输入有效的数字！")
            return
        is_safe = self.backend.check_transaction(amount)
        result = "Safe" if is_safe else "RiskAlert"
        if is_safe:
            messagebox.showinfo("提示", "✅ 金额正常，已记录该笔账单。")
        else:
            messagebox.showwarning("大额风控", "⚠️ 触发风控！支出 > 5000 或收入 > 10000，请二次核对。")
        self._append_record("transaction", {"amount": amount, "result": result})
        self.entry_amount.delete(0, tk.END)

    # ======================================================================
    # 功能 2：日记字数规范
    # ======================================================================
    def _create_tab_diary(self):
        tab = tk.Frame(self.notebook, bg="#f5f5f5", padx=15, pady=15)
        self.notebook.add(tab, text="  2. 日记规范  ")

        tk.Label(
            tab, text="📔 功能 2：日记字数合规校验（10–200 字）",
            font=("Microsoft YaHei", 13, "bold"),
            bg="#f5f5f5", fg="#16a085",
        ).pack(anchor="w", pady=(0, 8))

        form = tk.LabelFrame(tab, text=" 输入区 ", padx=10, pady=10, bg="#ffffff")
        form.pack(fill="x")
        tk.Label(form, text="日记内容：", bg="#ffffff").pack(anchor="w")
        self.text_diary = tk.Text(form, height=4, width=60)
        self.text_diary.pack(pady=4)
        tk.Button(
            form, text="提交日记", command=self.handle_diary,
            bg="#16a085", fg="white", padx=12, pady=4,
        ).pack(anchor="e")

        self._build_history_area(tab, "diary")

    def handle_diary(self):
        content = self.text_diary.get("1.0", tk.END)
        stripped = content.strip()
        is_valid = self.backend.validate_diary(content)
        result = "Valid" if is_valid else "Rejected"
        if is_valid:
            messagebox.showinfo("成功", "🎉 字数合规，已存档。")
        else:
            messagebox.showerror("规范拦截", "❌ 去首尾空格后需 10–200 字。")
        self._append_record("diary", {"length": len(stripped), "result": result})
        self.text_diary.delete("1.0", tk.END)

    # ======================================================================
    # 功能 3：每日饮水量
    # ======================================================================
    def _create_tab_water(self):
        tab = tk.Frame(self.notebook, bg="#f5f5f5", padx=15, pady=15)
        self.notebook.add(tab, text="  3. 饮水打卡  ")

        tk.Label(
            tab, text="💧 功能 3：每日饮水量评估",
            font=("Microsoft YaHei", 13, "bold"),
            bg="#f5f5f5", fg="#1abc9c",
        ).pack(anchor="w", pady=(0, 8))

        form = tk.LabelFrame(tab, text=" 输入区 ", padx=10, pady=10, bg="#ffffff")
        form.pack(fill="x")
        tk.Label(form, text="今日饮水量（毫升 ml，整数）：", bg="#ffffff").pack(anchor="w")
        self.entry_water = tk.Entry(form, width=40)
        self.entry_water.pack(anchor="w", pady=4)
        tk.Button(
            form, text="提交评估", command=self.handle_water,
            bg="#1abc9c", fg="white", padx=12, pady=4,
        ).pack(anchor="e")

        self._build_history_area(tab, "water")

    def handle_water(self):
        raw = self.entry_water.get().strip()
        try:
            ml = int(raw)
        except ValueError:
            messagebox.showerror("格式错误", "请输入合法的整数毫升数！")
            return
        result = self.backend.evaluate_water_intake(ml)
        msg_map = {
            "Invalid": ("数据异常", "饮水量不能为负数！", messagebox.showerror),
            "Healthy": ("饮水评估", "🟢 Healthy：已达每日 2000ml 基础需水线。", messagebox.showinfo),
            "Warning": ("饮水评估", "🟡 Warning：当前偏少（1000–1999ml），请补水。", messagebox.showwarning),
            "Danger":  ("脱水警告", "🔴 Danger：严重缺水（<1000ml），立刻喝水！", messagebox.showerror),
        }
        title, msg, fn = msg_map[result]
        fn(title, msg)
        self._append_record("water", {"ml": ml, "result": result})
        self.entry_water.delete(0, tk.END)

    # ======================================================================
    # 功能 4：BMI 评级
    # ======================================================================
    def _create_tab_bmi(self):
        tab = tk.Frame(self.notebook, bg="#f5f5f5", padx=15, pady=15)
        self.notebook.add(tab, text="  4. BMI 评级  ")

        tk.Label(
            tab, text="⚖️ 功能 4：身体质量指数 BMI 计算",
            font=("Microsoft YaHei", 13, "bold"),
            bg="#f5f5f5", fg="#8e44ad",
        ).pack(anchor="w", pady=(0, 8))

        form = tk.LabelFrame(tab, text=" 输入区 ", padx=10, pady=10, bg="#ffffff")
        form.pack(fill="x")
        tk.Label(form, text="身高（米 m，例如 1.75）：", bg="#ffffff").pack(anchor="w")
        self.entry_height = tk.Entry(form, width=40)
        self.entry_height.pack(anchor="w", pady=2)
        tk.Label(form, text="体重（公斤 kg，例如 65.5）：", bg="#ffffff").pack(anchor="w")
        self.entry_weight = tk.Entry(form, width=40)
        self.entry_weight.pack(anchor="w", pady=2)
        tk.Button(
            form, text="计算 BMI", command=self.handle_bmi,
            bg="#8e44ad", fg="white", padx=12, pady=4,
        ).pack(anchor="e")

        self._build_history_area(tab, "bmi")

    def handle_bmi(self):
        try:
            h = float(self.entry_height.get())
            w = float(self.entry_weight.get())
        except ValueError:
            messagebox.showerror("格式错误", "身高/体重请输入合法数字。")
            return
        result = self.backend.evaluate_bmi(h, w)
        msg_map = {
            "Invalid":     ("非法输入", "身高和体重必须 > 0！", messagebox.showerror),
            "Underweight": ("BMI 报告", "⚪ Underweight：BMI<18.5，注意补充营养。", messagebox.showwarning),
            "Normal":      ("BMI 报告", "🟢 Normal：体型标准，请保持。", messagebox.showinfo),
            "Overweight":  ("BMI 报告", "🟡 Overweight：BMI∈[24,28)，注意控制饮食。", messagebox.showwarning),
            "Obese":       ("严重警告", "🔴 Obese：BMI≥28，请关注体重管理！", messagebox.showerror),
        }
        title, msg, fn = msg_map[result]
        fn(title, msg)
        self._append_record("bmi", {"height": h, "weight": w, "result": result})

    # ======================================================================
    # 功能 5：月度预算预警
    # ======================================================================
    def _create_tab_budget(self):
        tab = tk.Frame(self.notebook, bg="#f5f5f5", padx=15, pady=15)
        self.notebook.add(tab, text="  5. 月度预算  ")

        tk.Label(
            tab, text="📊 功能 5：月度预算状态分析",
            font=("Microsoft YaHei", 13, "bold"),
            bg="#f5f5f5", fg="#e67e22",
        ).pack(anchor="w", pady=(0, 8))

        form = tk.LabelFrame(tab, text=" 输入区 ", padx=10, pady=10, bg="#ffffff")
        form.pack(fill="x")
        tk.Label(form, text="本月已花金额（元）：", bg="#ffffff").pack(anchor="w")
        self.entry_spent = tk.Entry(form, width=40)
        self.entry_spent.pack(anchor="w", pady=2)
        tk.Label(form, text="本月总预算（元）：", bg="#ffffff").pack(anchor="w")
        self.entry_budget = tk.Entry(form, width=40)
        self.entry_budget.pack(anchor="w", pady=2)
        tk.Button(
            form, text="评估预算", command=self.handle_budget,
            bg="#e67e22", fg="white", padx=12, pady=4,
        ).pack(anchor="e")

        self._build_history_area(tab, "budget")

    def handle_budget(self):
        try:
            spent = float(self.entry_spent.get())
            budget = float(self.entry_budget.get())
        except ValueError:
            messagebox.showerror("格式错误", "请输入合法数字！")
            return
        result = self.backend.check_monthly_budget(spent, budget)
        msg_map = {
            "Invalid": ("错误",     "预算总额必须 > 0！",                      messagebox.showerror),
            "Safe":    ("预算状态", "🟢 Safe：消费节奏良好。",                 messagebox.showinfo),
            "Warning": ("预算预警", "🟡 Warning：开销已达预算 80% 以上！",     messagebox.showwarning),
            "Over":    ("超支告警", "🔴 Over：开销已穿透总预算，立即控制！",   messagebox.showerror),
        }
        title, msg, fn = msg_map[result]
        fn(title, msg)
        self._append_record("budget", {"spent": spent, "budget": budget, "result": result})

    # ======================================================================
    # 功能 6：睡眠时长评级
    # ======================================================================
    def _create_tab_sleep(self):
        tab = tk.Frame(self.notebook, bg="#f5f5f5", padx=15, pady=15)
        self.notebook.add(tab, text="  6. 睡眠监测  ")

        tk.Label(
            tab, text="😴 功能 6：睡眠时长健康评级",
            font=("Microsoft YaHei", 13, "bold"),
            bg="#f5f5f5", fg="#34495e",
        ).pack(anchor="w", pady=(0, 8))

        form = tk.LabelFrame(tab, text=" 输入区 ", padx=10, pady=10, bg="#ffffff")
        form.pack(fill="x")
        tk.Label(form, text="昨晚睡眠时长（小时，可带小数）：", bg="#ffffff").pack(anchor="w")
        self.entry_sleep = tk.Entry(form, width=40)
        self.entry_sleep.pack(anchor="w", pady=4)
        tk.Button(
            form, text="分析睡眠", command=self.handle_sleep,
            bg="#34495e", fg="white", padx=12, pady=4,
        ).pack(anchor="e")

        self._build_history_area(tab, "sleep")

    def handle_sleep(self):
        try:
            hours = float(self.entry_sleep.get())
        except ValueError:
            messagebox.showerror("格式错误", "请输入有效的睡眠小时数！")
            return
        result = self.backend.evaluate_sleep(hours)
        msg_map = {
            "Invalid":      ("异常数据", "睡眠时长必须在 0–24 小时之间。",          messagebox.showerror),
            "Insufficient": ("睡眠报告", "⚠️ Insufficient：长期 <6h 损害免疫力！", messagebox.showwarning),
            "Healthy":      ("睡眠报告", "🟢 Healthy：6–9 小时健康区间。",         messagebox.showinfo),
            "Excessive":    ("睡眠报告", "🟡 Excessive：>9h 请关注作息规律。",     messagebox.showwarning),
        }
        title, msg, fn = msg_map[result]
        fn(title, msg)
        self._append_record("sleep", {"hours": hours, "result": result})
        self.entry_sleep.delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TNotebook.Tab", padding=[18, 8], font=("Microsoft YaHei", 10))
    app = AssistantGUI(root)
    root.mainloop()
