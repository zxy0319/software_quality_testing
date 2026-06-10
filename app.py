import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

from personal_assistant import PersonalAssistant


DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assistant_data.json")


def _load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "transactions": [],
        "diaries": [],
        "waters": [],
        "bmis": [],
        "budgets": [],
        "sleeps": [],
    }


def _save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class AssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("个人小助手")
        self.root.geometry("780x640")
        self.root.minsize(640, 520)
        self.root.configure(bg="#f0f0f0")

        self.backend = PersonalAssistant()
        self.data = _load_data()

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#f0f0f0")
        style.configure("TNotebook.Tab", padding=[16, 5], font=("Microsoft YaHei UI", 10))
        style.configure("TLabel", font=("Microsoft YaHei UI", 10))
        style.configure("TButton", font=("Microsoft YaHei UI", 10), padding=4)
        style.configure("Header.TLabel", font=("Microsoft YaHei UI", 12, "bold"))
        style.configure("Treeview", font=("Microsoft YaHei UI", 9), rowheight=26)
        style.configure("Treeview.Heading", font=("Microsoft YaHei UI", 9, "bold"))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_transaction = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_transaction, text="  记账  ")
        self._build_transaction_tab()

        self.tab_diary = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_diary, text="  日记  ")
        self._build_diary_tab()

        self.tab_water = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_water, text="  饮水  ")
        self._build_water_tab()

        self.tab_bmi = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_bmi, text="  BMI  ")
        self._build_bmi_tab()

        self.tab_budget = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_budget, text="  月度预算  ")
        self._build_budget_tab()

        self.tab_sleep = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_sleep, text="  睡眠  ")
        self._build_sleep_tab()

        self.tab_records = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_records, text="  全部记录  ")
        self._build_records_tab()

    @staticmethod
    def _now_str():
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    @staticmethod
    def _format_time(iso_str):
        try:
            dt = datetime.fromisoformat(iso_str)
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return iso_str

    def _make_tree(self, parent, cols, headings, widths, height=6):
        tree = ttk.Treeview(parent, columns=cols, show="headings", height=height)
        for col, heading, width in zip(cols, headings, widths):
            tree.heading(col, text=heading)
            anchor = "w" if col in ("note", "preview", "content") else "center"
            tree.column(col, width=width, anchor=anchor)
        sb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        return tree

    def _make_input_row(self, parent, label_text, entry_width=20):
        row = ttk.Frame(parent)
        row.pack(fill="x", padx=10, pady=6)
        ttk.Label(row, text=label_text).pack(side="left")
        entry = ttk.Entry(row, width=entry_width)
        entry.pack(side="left", padx=4)
        return entry

    def _make_buttons(self, parent, save_text, save_cmd, query_cmd):
        bf = ttk.Frame(parent)
        bf.pack(fill="x", padx=10, pady=(4, 10))
        ttk.Button(bf, text=save_text, command=save_cmd).pack(side="left", padx=4)
        ttk.Button(bf, text="查询历史", command=query_cmd).pack(side="left", padx=4)
        return bf

    # ------------------------------------------------------------------
    # Tab 1: 记账
    # ------------------------------------------------------------------
    def _build_transaction_tab(self):
        frame = self.tab_transaction
        ttk.Label(frame, text="记账助手 - 收支限额检查",
                  style="Header.TLabel").pack(anchor="w", padx=16, pady=(12, 4))

        inp = ttk.LabelFrame(frame, text="新增记录")
        inp.pack(fill="x", padx=16, pady=6)
        self.entry_amount = self._make_input_row(inp, "金额：", 20)
        row_hint = ttk.Frame(inp)
        row_hint.pack(fill="x", padx=10)
        ttk.Label(row_hint, text="  (正数=收入，负数=支出)",
                  foreground="gray").pack(side="left")
        self.entry_tx_note = self._make_input_row(inp, "备注：", 36)
        self._make_buttons(inp, "校验并保存",
                           self.handle_transaction, self.query_transactions)

        lf = ttk.LabelFrame(frame, text="历史记录")
        lf.pack(fill="both", expand=True, padx=16, pady=6)
        self.tree_tx = self._make_tree(
            lf,
            ("time", "amount", "result", "note"),
            ("时间", "金额", "校验结果", "备注"),
            (140, 100, 100, 200),
        )

    def handle_transaction(self):
        try:
            amount = float(self.entry_amount.get())
        except ValueError:
            messagebox.showerror("格式错误", "请输入合法的数字！")
            return
        note = self.entry_tx_note.get().strip()
        is_safe = self.backend.check_transaction(amount)
        result_text = "正常" if is_safe else "异常，需确认"
        if is_safe:
            messagebox.showinfo("结果", "金额正常，已保存。")
        else:
            if not messagebox.askyesno("提示", "金额异常，是否仍要保存？"):
                return
        self.data["transactions"].append({
            "time": self._now_str(),
            "amount": amount,
            "result": result_text,
            "note": note,
        })
        _save_data(self.data)
        self.entry_amount.delete(0, tk.END)
        self.entry_tx_note.delete(0, tk.END)
        self.query_transactions()

    def query_transactions(self):
        for item in self.tree_tx.get_children():
            self.tree_tx.delete(item)
        for r in self.backend.get_recent_records(self.data["transactions"]):
            self.tree_tx.insert("", "end", values=(
                self._format_time(r.get("time", "")),
                f"{r.get('amount', 0):.2f}",
                r.get("result", ""),
                r.get("note", ""),
            ))

    # ------------------------------------------------------------------
    # Tab 2: 日记
    # ------------------------------------------------------------------
    def _build_diary_tab(self):
        frame = self.tab_diary
        ttk.Label(frame, text="记录生活 - 日记字数规范",
                  style="Header.TLabel").pack(anchor="w", padx=16, pady=(12, 4))

        inp = ttk.LabelFrame(frame, text="写日记")
        inp.pack(fill="both", expand=True, padx=16, pady=6)
        self.text_diary = tk.Text(inp, height=6,
                                  font=("Microsoft YaHei UI", 10), wrap="word")
        self.text_diary.pack(fill="both", expand=True, padx=10, pady=(8, 4))
        self.lbl_diary_count = ttk.Label(
            inp, text="已输入 0 字 (10-200)", foreground="gray")
        self.lbl_diary_count.pack(anchor="e", padx=10)
        self.text_diary.bind("<KeyRelease>", self._on_diary_key)
        self._make_buttons(inp, "校验并保存",
                           self.handle_diary, self.query_diaries)

        lf = ttk.LabelFrame(frame, text="历史日记")
        lf.pack(fill="both", expand=True, padx=16, pady=(0, 6))
        self.tree_diary = self._make_tree(
            lf,
            ("time", "preview", "valid"),
            ("时间", "内容预览", "合规"),
            (140, 360, 60),
        )

    def _on_diary_key(self, _event=None):
        length = len(self.text_diary.get("1.0", tk.END).strip())
        self.lbl_diary_count.config(text=f"已输入 {length} 字 (10-200)")

    def handle_diary(self):
        content = self.text_diary.get("1.0", tk.END)
        if self.backend.validate_diary(content):
            self.data["diaries"].append({
                "time": self._now_str(),
                "content": content.strip(),
                "valid": "是",
            })
            _save_data(self.data)
            messagebox.showinfo("结果", "日记字数合规，已保存。")
            self.text_diary.delete("1.0", tk.END)
            self._on_diary_key()
            self.query_diaries()
        else:
            messagebox.showwarning("提示", "日记字数需在 10-200 字之间！")

    def query_diaries(self):
        for item in self.tree_diary.get_children():
            self.tree_diary.delete(item)
        for r in self.backend.get_recent_records(self.data["diaries"]):
            preview = r.get("content", "")
            if len(preview) > 50:
                preview = preview[:50] + "..."
            self.tree_diary.insert("", "end", values=(
                self._format_time(r.get("time", "")),
                preview,
                r.get("valid", ""),
            ))

    # ------------------------------------------------------------------
    # Tab 3: 饮水
    # ------------------------------------------------------------------
    def _build_water_tab(self):
        frame = self.tab_water
        ttk.Label(frame, text="健康助手 - 每日饮水量评估",
                  style="Header.TLabel").pack(anchor="w", padx=16, pady=(12, 4))

        inp = ttk.LabelFrame(frame, text="记录饮水")
        inp.pack(fill="x", padx=16, pady=6)
        self.entry_water = self._make_input_row(inp, "饮水量(毫升)：", 16)
        self._make_buttons(inp, "评估并保存",
                           self.handle_water, self.query_waters)

        lf = ttk.LabelFrame(frame, text="历史记录")
        lf.pack(fill="both", expand=True, padx=16, pady=6)
        self.tree_water = self._make_tree(
            lf,
            ("time", "water_ml", "level"),
            ("时间", "饮水量(ml)", "评级"),
            (160, 120, 120),
        )

    def handle_water(self):
        try:
            water_ml = int(self.entry_water.get())
        except ValueError:
            messagebox.showerror("格式错误", "请输入合法的整数毫升数！")
            return
        result = self.backend.evaluate_water_intake(water_ml)
        msgs = {
            "Invalid": "饮水量非法，请重新输入！",
            "Healthy": "饮水量充足，继续保持！",
            "Warning": "饮水量偏少，建议多喝水。",
            "Danger": "饮水量过低，请立即补水！",
        }
        levels = {
            "Invalid": "非法",
            "Healthy": "充足",
            "Warning": "偏少",
            "Danger": "危险",
        }
        if result == "Invalid":
            messagebox.showerror("饮水评估", msgs[result])
            return
        self.data["waters"].append({
            "time": self._now_str(),
            "water_ml": water_ml,
            "level": levels.get(result, result),
        })
        _save_data(self.data)
        messagebox.showinfo("饮水评估", msgs[result])
        self.entry_water.delete(0, tk.END)
        self.query_waters()

    def query_waters(self):
        for item in self.tree_water.get_children():
            self.tree_water.delete(item)
        for r in self.backend.get_recent_records(self.data["waters"]):
            self.tree_water.insert("", "end", values=(
                self._format_time(r.get("time", "")),
                r.get("water_ml", ""),
                r.get("level", ""),
            ))

    # ------------------------------------------------------------------
    # Tab 4: BMI
    # ------------------------------------------------------------------
    def _build_bmi_tab(self):
        frame = self.tab_bmi
        ttk.Label(frame, text="健康助手 - BMI 评级",
                  style="Header.TLabel").pack(anchor="w", padx=16, pady=(12, 4))

        inp = ttk.LabelFrame(frame, text="计算 BMI")
        inp.pack(fill="x", padx=16, pady=6)
        self.entry_height = self._make_input_row(inp, "身高(米)：", 12)
        self.entry_weight = self._make_input_row(inp, "体重(公斤)：", 12)
        self._make_buttons(inp, "评估并保存",
                           self.handle_bmi, self.query_bmis)

        lf = ttk.LabelFrame(frame, text="历史记录")
        lf.pack(fill="both", expand=True, padx=16, pady=6)
        self.tree_bmi = self._make_tree(
            lf,
            ("time", "height", "weight", "bmi", "level"),
            ("时间", "身高(m)", "体重(kg)", "BMI", "评级"),
            (130, 80, 80, 70, 80),
        )

    def handle_bmi(self):
        try:
            height = float(self.entry_height.get())
            weight = float(self.entry_weight.get())
        except ValueError:
            messagebox.showerror("格式错误", "请输入合法的数字！")
            return
        result = self.backend.evaluate_bmi(height, weight)
        msgs = {
            "Invalid": "输入非法，请重新输入！",
            "Underweight": "偏瘦，建议增加营养摄入。",
            "Normal": "体重正常，请保持！",
            "Overweight": "超重，建议控制饮食、加强运动。",
            "Obese": "肥胖，建议咨询医生并制定减重计划。",
        }
        levels = {
            "Invalid": "非法",
            "Underweight": "偏瘦",
            "Normal": "正常",
            "Overweight": "超重",
            "Obese": "肥胖",
        }
        if result == "Invalid":
            messagebox.showerror("BMI 评估", msgs[result])
            return
        bmi_val = weight / (height * height)
        self.data["bmis"].append({
            "time": self._now_str(),
            "height": height,
            "weight": weight,
            "bmi": round(bmi_val, 1),
            "level": levels.get(result, result),
        })
        _save_data(self.data)
        messagebox.showinfo("BMI 评估", msgs[result])
        self.entry_height.delete(0, tk.END)
        self.entry_weight.delete(0, tk.END)
        self.query_bmis()

    def query_bmis(self):
        for item in self.tree_bmi.get_children():
            self.tree_bmi.delete(item)
        for r in self.backend.get_recent_records(self.data["bmis"]):
            self.tree_bmi.insert("", "end", values=(
                self._format_time(r.get("time", "")),
                r.get("height", ""),
                r.get("weight", ""),
                r.get("bmi", ""),
                r.get("level", ""),
            ))

    # ------------------------------------------------------------------
    # Tab 5: 月度预算
    # ------------------------------------------------------------------
    def _build_budget_tab(self):
        frame = self.tab_budget
        ttk.Label(frame, text="记账助手 - 月度预算预警",
                  style="Header.TLabel").pack(anchor="w", padx=16, pady=(12, 4))

        inp = ttk.LabelFrame(frame, text="预算检查")
        inp.pack(fill="x", padx=16, pady=6)
        self.entry_spent = self._make_input_row(inp, "本月已花费：", 14)
        self.entry_budget = self._make_input_row(inp, "本月预算：", 14)
        self._make_buttons(inp, "检查并保存",
                           self.handle_budget, self.query_budgets)

        lf = ttk.LabelFrame(frame, text="历史记录")
        lf.pack(fill="both", expand=True, padx=16, pady=6)
        self.tree_budget = self._make_tree(
            lf,
            ("time", "spent", "budget", "ratio", "status"),
            ("时间", "已花费", "预算", "使用比例", "状态"),
            (130, 80, 80, 80, 80),
        )

    def handle_budget(self):
        try:
            spent = float(self.entry_spent.get())
            budget = float(self.entry_budget.get())
        except ValueError:
            messagebox.showerror("格式错误", "请输入合法的数字！")
            return
        result = self.backend.check_monthly_budget(spent, budget)
        msgs = {
            "Invalid": "预算非法，请重新输入！",
            "Safe": "消费安全，继续保持。",
            "Warning": "已接近预算上限，注意节制！",
            "Over": "已超出预算，请控制支出！",
        }
        statuses = {
            "Invalid": "非法",
            "Safe": "安全",
            "Warning": "预警",
            "Over": "超支",
        }
        if result == "Invalid":
            messagebox.showerror("预算检查", msgs[result])
            return
        ratio = spent / budget if budget > 0 else 0
        self.data["budgets"].append({
            "time": self._now_str(),
            "spent": spent,
            "budget": budget,
            "ratio": f"{ratio:.0%}",
            "status": statuses.get(result, result),
        })
        _save_data(self.data)
        messagebox.showinfo("预算检查", msgs[result])
        self.entry_spent.delete(0, tk.END)
        self.entry_budget.delete(0, tk.END)
        self.query_budgets()

    def query_budgets(self):
        for item in self.tree_budget.get_children():
            self.tree_budget.delete(item)
        for r in self.backend.get_recent_records(self.data["budgets"]):
            self.tree_budget.insert("", "end", values=(
                self._format_time(r.get("time", "")),
                f"{r.get('spent', 0):.2f}",
                f"{r.get('budget', 0):.2f}",
                r.get("ratio", ""),
                r.get("status", ""),
            ))

    # ------------------------------------------------------------------
    # Tab 6: 睡眠
    # ------------------------------------------------------------------
    def _build_sleep_tab(self):
        frame = self.tab_sleep
        ttk.Label(frame, text="生活助手 - 睡眠时长评级",
                  style="Header.TLabel").pack(anchor="w", padx=16, pady=(12, 4))

        inp = ttk.LabelFrame(frame, text="记录睡眠")
        inp.pack(fill="x", padx=16, pady=6)
        self.entry_sleep = self._make_input_row(inp, "睡眠时长(小时)：", 14)
        self._make_buttons(inp, "评估并保存",
                           self.handle_sleep, self.query_sleeps)

        lf = ttk.LabelFrame(frame, text="历史记录")
        lf.pack(fill="both", expand=True, padx=16, pady=6)
        self.tree_sleep = self._make_tree(
            lf,
            ("time", "hours", "level"),
            ("时间", "时长(h)", "评级"),
            (160, 120, 120),
        )

    def handle_sleep(self):
        try:
            hours = float(self.entry_sleep.get())
        except ValueError:
            messagebox.showerror("格式错误", "请输入合法的数字！")
            return
        result = self.backend.evaluate_sleep(hours)
        msgs = {
            "Invalid": "输入非法，请重新输入！",
            "Insufficient": "睡眠不足，建议早点休息。",
            "Healthy": "睡眠时长健康，请保持！",
            "Excessive": "睡眠过量，建议调整作息。",
        }
        levels = {
            "Invalid": "非法",
            "Insufficient": "不足",
            "Healthy": "健康",
            "Excessive": "过量",
        }
        if result == "Invalid":
            messagebox.showerror("睡眠评估", msgs[result])
            return
        self.data["sleeps"].append({
            "time": self._now_str(),
            "hours": hours,
            "level": levels.get(result, result),
        })
        _save_data(self.data)
        messagebox.showinfo("睡眠评估", msgs[result])
        self.entry_sleep.delete(0, tk.END)
        self.query_sleeps()

    def query_sleeps(self):
        for item in self.tree_sleep.get_children():
            self.tree_sleep.delete(item)
        for r in self.backend.get_recent_records(self.data["sleeps"]):
            self.tree_sleep.insert("", "end", values=(
                self._format_time(r.get("time", "")),
                r.get("hours", ""),
                r.get("level", ""),
            ))

    # ------------------------------------------------------------------
    # Tab 7: 全部记录
    # ------------------------------------------------------------------
    def _build_records_tab(self):
        frame = self.tab_records
        ttk.Label(frame, text="全部记录汇总",
                  style="Header.TLabel").pack(anchor="w", padx=16, pady=(12, 4))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", padx=16, pady=6)
        ttk.Button(btn_frame, text="刷新全部",
                   command=self.query_all_records).pack(side="left", padx=4)

        lf = ttk.LabelFrame(frame, text="所有记录")
        lf.pack(fill="both", expand=True, padx=16, pady=6)
        self.tree_all = self._make_tree(
            lf,
            ("time", "category", "detail"),
            ("时间", "类别", "详情"),
            (140, 100, 400),
            height=12,
        )

    def query_all_records(self):
        for item in self.tree_all.get_children():
            self.tree_all.delete(item)
        all_records = []
        for r in self.data.get("transactions", []):
            all_records.append({
                "time": r.get("time", ""),
                "category": "记账",
                "detail": f"金额:{r.get('amount', 0):.2f} 结果:{r.get('result', '')} {r.get('note', '')}",
            })
        for r in self.data.get("diaries", []):
            preview = r.get("content", "")
            if len(preview) > 30:
                preview = preview[:30] + "..."
            all_records.append({
                "time": r.get("time", ""),
                "category": "日记",
                "detail": f"{preview} 合规:{r.get('valid', '')}",
            })
        for r in self.data.get("waters", []):
            all_records.append({
                "time": r.get("time", ""),
                "category": "饮水",
                "detail": f"{r.get('water_ml', '')}ml 评级:{r.get('level', '')}",
            })
        for r in self.data.get("bmis", []):
            all_records.append({
                "time": r.get("time", ""),
                "category": "BMI",
                "detail": f"身高:{r.get('height', '')}m 体重:{r.get('weight', '')}kg BMI:{r.get('bmi', '')} {r.get('level', '')}",
            })
        for r in self.data.get("budgets", []):
            all_records.append({
                "time": r.get("time", ""),
                "category": "预算",
                "detail": f"花费:{r.get('spent', 0):.2f} 预算:{r.get('budget', 0):.2f} 比例:{r.get('ratio', '')} {r.get('status', '')}",
            })
        for r in self.data.get("sleeps", []):
            all_records.append({
                "time": r.get("time", ""),
                "category": "睡眠",
                "detail": f"{r.get('hours', '')}h 评级:{r.get('level', '')}",
            })
        recent = self.backend.get_recent_records(all_records, n=50)
        for r in recent:
            self.tree_all.insert("", "end", values=(
                self._format_time(r.get("time", "")),
                r.get("category", ""),
                r.get("detail", ""),
            ))


if __name__ == "__main__":
    root = tk.Tk()
    app = AssistantGUI(root)
    root.mainloop()
