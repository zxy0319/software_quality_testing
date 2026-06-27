import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

from personal_assistant import PersonalAssistant

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assistant_data.json")

# ============================================================
# 配色 & 字体常量
# ============================================================
COLOR_PRIMARY = "#4A90D9"
COLOR_PRIMARY_DARK = "#357ABD"
COLOR_BG = "#F5F6FA"
COLOR_CARD = "#FFFFFF"
COLOR_BORDER = "#E0E0E0"
COLOR_TEXT = "#2C3E50"
COLOR_HINT = "#95A5A6"
COLOR_SUCCESS = "#27AE60"
COLOR_WARNING = "#F39C12"
COLOR_DANGER = "#E74C3C"
COLOR_TREE_EVEN = "#F7F9FC"
COLOR_TREE_ODD = "#FFFFFF"
COLOR_SELECT = "#D6EAF8"
COLOR_HEADER_BG = "#3C7DC4"

FONT_FAMILY = "Microsoft YaHei UI"
FONT_HEADER = (FONT_FAMILY, 15, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 9)
FONT_TAB = (FONT_FAMILY, 11)
FONT_LABEL = (FONT_FAMILY, 10)
FONT_BUTTON = (FONT_FAMILY, 10)
FONT_TREE = (FONT_FAMILY, 9)
FONT_TREE_HEADING = (FONT_FAMILY, 9, "bold")
FONT_STATUS = (FONT_FAMILY, 9)
FONT_HINT = (FONT_FAMILY, 9)


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
        self.root.geometry("840x700")
        self.root.minsize(680, 560)
        self.root.configure(bg=COLOR_BG)

        self.backend = PersonalAssistant()
        self.data = _load_data()

        # ======== 全局样式 ========
        style = ttk.Style()
        style.theme_use("clam")

        # 全局默认字体 / 背景
        style.configure(".", font=FONT_LABEL, background=COLOR_BG)

        # Notebook (选项卡栏)
        style.configure("TNotebook",
                        background=COLOR_BG,
                        borderwidth=0,
                        tabmargins=[2, 2, 2, 0])
        style.configure("TNotebook.Tab",
                        font=FONT_TAB,
                        padding=[18, 8],
                        background=COLOR_CARD,
                        borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", COLOR_PRIMARY),
                              ("active", "#EBF5FB")],
                  foreground=[("selected", "#FFFFFF"),
                              ("!selected", COLOR_TEXT)])

        # 标签
        style.configure("TLabel", font=FONT_LABEL, background=COLOR_CARD)
        style.configure("Header.TLabel",
                        font=(FONT_FAMILY, 13, "bold"),
                        foreground=COLOR_TEXT,
                        background=COLOR_CARD)
        style.configure("Hint.TLabel",
                        font=FONT_HINT,
                        foreground=COLOR_HINT,
                        background=COLOR_CARD)

        # 卡片式 LabelFrame
        style.configure("Card.TLabelframe",
                        background=COLOR_CARD,
                        bordercolor=COLOR_BORDER,
                        borderwidth=1,
                        relief="solid")
        style.configure("Card.TLabelframe.Label",
                        font=(FONT_FAMILY, 11, "bold"),
                        foreground=COLOR_PRIMARY,
                        background=COLOR_CARD)

        # 输入框
        style.configure("Card.TEntry",
                        fieldbackground=COLOR_CARD,
                        borderwidth=1,
                        relief="solid",
                        padding=6)
        style.map("Card.TEntry",
                  bordercolor=[("focus", COLOR_PRIMARY)],
                  lightcolor=[("focus", COLOR_PRIMARY)],
                  darkcolor=[("focus", COLOR_PRIMARY)])

        # 主按钮 (蓝底白字)
        style.configure("Primary.TButton",
                        font=FONT_BUTTON,
                        background=COLOR_PRIMARY,
                        foreground="#FFFFFF",
                        borderwidth=0,
                        padding=[16, 6])
        style.map("Primary.TButton",
                  background=[("active", COLOR_PRIMARY_DARK),
                              ("pressed", COLOR_PRIMARY_DARK)],
                  foreground=[("active", "#FFFFFF")])

        # 次要按钮 (白底 + 蓝色边框)
        style.configure("Secondary.TButton",
                        font=FONT_BUTTON,
                        background=COLOR_CARD,
                        foreground=COLOR_PRIMARY,
                        borderwidth=1,
                        bordercolor=COLOR_PRIMARY,
                        padding=[16, 6])
        style.map("Secondary.TButton",
                  background=[("active", "#EBF5FB")],
                  foreground=[("active", COLOR_PRIMARY_DARK)])

        # 表格 (Treeview)
        style.configure("Treeview",
                        font=FONT_TREE,
                        rowheight=30,
                        background=COLOR_CARD,
                        fieldbackground=COLOR_CARD,
                        borderwidth=1)
        style.configure("Treeview.Heading",
                        font=FONT_TREE_HEADING,
                        background="#EBF0F5",
                        foreground=COLOR_TEXT,
                        borderwidth=1,
                        padding=[6, 6])
        style.map("Treeview",
                  background=[("selected", COLOR_SELECT)],
                  foreground=[("selected", COLOR_TEXT)])

        # ---------- 顶部标题栏 ----------
        self.header = tk.Frame(self.root, bg=COLOR_HEADER_BG, height=62)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        inner = tk.Frame(self.header, bg=COLOR_HEADER_BG)
        inner.pack(side="left", padx=24, pady=10)

        tk.Label(inner, text="🏠  个人小助手",
                 font=FONT_HEADER,
                 fg="#FFFFFF",
                 bg=COLOR_HEADER_BG).pack(anchor="w")
        tk.Label(inner, text="记录生活  ·  管理健康  ·  掌控财务",
                 font=FONT_SUBTITLE,
                 fg="#C5DCF7",
                 bg=COLOR_HEADER_BG).pack(anchor="w", pady=(2, 0))

        # ---------- 选项卡 ----------
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(12, 0))
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        self.tab_transaction = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_transaction, text="  💰  记账  ")
        self._build_transaction_tab()

        self.tab_diary = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_diary, text="  📔  日记  ")
        self._build_diary_tab()

        self.tab_water = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_water, text="  💧  饮水  ")
        self._build_water_tab()

        self.tab_bmi = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_bmi, text="  ⚖️  BMI  ")
        self._build_bmi_tab()

        self.tab_budget = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_budget, text="  💵  预算  ")
        self._build_budget_tab()

        self.tab_sleep = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_sleep, text="  😴  睡眠  ")
        self._build_sleep_tab()

        self.tab_records = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_records, text="  📋  全部  ")
        self._build_records_tab()

        # ---------- 底部状态栏 ----------
        self.status_bar = tk.Frame(self.root, bg=COLOR_BORDER, height=28)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar.pack_propagate(False)

        tk.Frame(self.status_bar, bg=COLOR_PRIMARY, height=3).pack(fill="x")

        status_inner = tk.Frame(self.status_bar, bg=COLOR_CARD)
        status_inner.pack(fill="both", expand=True)

        self.lbl_status = tk.Label(
            status_inner,
            text="",
            font=FONT_STATUS,
            fg=COLOR_HINT,
            bg=COLOR_CARD,
            anchor="w",
        )
        self.lbl_status.pack(side="left", padx=16, pady=3)

        self._update_status()

    # ========================================================
    # 辅助方法
    # ========================================================
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

    def _on_tab_change(self, _event=None):
        self._update_status()

    def _update_status(self):
        counts = []
        for key, label in [
            ("transactions", "记账"),
            ("diaries", "日记"),
            ("waters", "饮水"),
            ("bmis", "BMI"),
            ("budgets", "预算"),
            ("sleeps", "睡眠"),
        ]:
            n = len(self.data.get(key, []))
            counts.append(f"{label}:{n}条")
        total = sum(len(self.data.get(k, [])) for k, _ in [
            ("transactions", ""),
            ("diaries", ""),
            ("waters", ""),
            ("bmis", ""),
            ("budgets", ""),
            ("sleeps", ""),
        ])
        self.lbl_status.config(
            text=f"📊  共 {total} 条记录  |  " + "  |  ".join(counts)
        )

    def _make_tree(self, parent, cols, headings, widths, height=6):
        """创建带交替行色的表格"""
        tree = ttk.Treeview(parent, columns=cols, show="headings", height=height)
        for col, heading, width in zip(cols, headings, widths):
            tree.heading(col, text=heading)
            anchor = "w" if col in ("note", "preview", "content", "detail") else "center"
            tree.column(col, width=width, anchor=anchor)

        # 交替行颜色标签
        tree.tag_configure("even", background=COLOR_TREE_EVEN)
        tree.tag_configure("odd", background=COLOR_TREE_ODD)

        # Monkey-patch insert 以实现自动交替行色
        _orig_insert = tree.insert
        def _patched_insert(parent_item, index, **kw):
            item = _orig_insert(parent_item, index, **kw)
            children = tree.get_children(parent_item)
            idx = children.index(item)
            tag = "even" if idx % 2 == 0 else "odd"
            current_tags = list(tree.item(item, "tags") or ())
            if tag not in current_tags:
                tree.item(item, tags=(*current_tags, tag))
            return item
        tree.insert = _patched_insert

        sb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        return tree

    def _make_input_row(self, parent, label_text, entry_width=20):
        row = tk.Frame(parent, bg=COLOR_CARD)
        row.pack(fill="x", padx=14, pady=5)
        ttk.Label(row, text=label_text,
                  style="TLabel").pack(side="left")
        entry = ttk.Entry(row, width=entry_width, style="Card.TEntry")
        entry.pack(side="left", padx=6)
        return entry

    def _make_buttons(self, parent, save_text, save_cmd, query_cmd):
        bf = tk.Frame(parent, bg=COLOR_CARD)
        bf.pack(fill="x", padx=14, pady=(8, 14))
        ttk.Button(bf, text=save_text, command=save_cmd,
                   style="Primary.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(bf, text="📋 查询历史", command=query_cmd,
                   style="Secondary.TButton").pack(side="left")
        return bf

    # ========================================================
    # Tab 1: 记账
    # ========================================================
    def _build_transaction_tab(self):
        frame = self.tab_transaction
        frame.configure(style="TFrame")

        ttk.Label(frame, text="记账助手 - 收支限额检查",
                  style="Header.TLabel").pack(anchor="w", padx=20, pady=(16, 6))

        inp = ttk.LabelFrame(frame, text="  💳 新增记录  ", style="Card.TLabelframe")
        inp.pack(fill="x", padx=20, pady=(0, 8))

        self.entry_amount = self._make_input_row(inp, "金额：", 22)
        row_hint = tk.Frame(inp, bg=COLOR_CARD)
        row_hint.pack(fill="x", padx=14)
        ttk.Label(row_hint, text="   正数 = 收入，负数 = 支出",
                  style="Hint.TLabel").pack(side="left")
        self.entry_tx_note = self._make_input_row(inp, "备注：", 38)
        self._make_buttons(inp, "校验并保存",
                           self.handle_transaction, self.query_transactions)

        lf = ttk.LabelFrame(frame, text="  📜 历史记录  ", style="Card.TLabelframe")
        lf.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        self.tree_tx = self._make_tree(
            lf,
            ("time", "amount", "result", "note"),
            ("时间", "金额", "校验结果", "备注"),
            (140, 100, 100, 200),
        )

    # ========================================================
    # Tab 2: 日记
    # ========================================================
    def _build_diary_tab(self):
        frame = self.tab_diary
        frame.configure(style="TFrame")

        ttk.Label(frame, text="记录生活 - 日记字数规范",
                  style="Header.TLabel").pack(anchor="w", padx=20, pady=(16, 6))

        inp = ttk.LabelFrame(frame, text="  ✍️  写日记  ", style="Card.TLabelframe")
        inp.pack(fill="both", padx=20, pady=(0, 8))

        text_frame = tk.Frame(inp, bg=COLOR_CARD, bd=1, relief="solid")
        text_frame.configure(bg=COLOR_BORDER)
        text_frame.pack(fill="both", expand=True, padx=14, pady=(10, 4))

        self.text_diary = tk.Text(
            text_frame, height=6,
            font=(FONT_FAMILY, 10),
            wrap="word",
            bg=COLOR_CARD,
            fg=COLOR_TEXT,
            bd=0,
            padx=10, pady=8,
            insertbackground=COLOR_PRIMARY,
            selectbackground=COLOR_SELECT,
        )
        self.text_diary.pack(fill="both", expand=True)

        self.lbl_diary_count = ttk.Label(
            inp, text="已输入 0 字 (10-200)", style="Hint.TLabel")
        self.lbl_diary_count.pack(anchor="e", padx=14)
        self.text_diary.bind("<KeyRelease>", self._on_diary_key)
        self._make_buttons(inp, "校验并保存",
                           self.handle_diary, self.query_diaries)

        lf = ttk.LabelFrame(frame, text="  📖 历史日记  ", style="Card.TLabelframe")
        lf.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        self.tree_diary = self._make_tree(
            lf,
            ("time", "preview", "valid"),
            ("时间", "内容预览", "合规"),
            (140, 360, 60),
        )

    # ========================================================
    # Tab 3: 饮水
    # ========================================================
    def _build_water_tab(self):
        frame = self.tab_water
        frame.configure(style="TFrame")

        ttk.Label(frame, text="健康助手 - 每日饮水量评估",
                  style="Header.TLabel").pack(anchor="w", padx=20, pady=(16, 6))

        inp = ttk.LabelFrame(frame, text="  🥤 记录饮水  ", style="Card.TLabelframe")
        inp.pack(fill="x", padx=20, pady=(0, 8))

        self.entry_water = self._make_input_row(inp, "饮水量 (毫升)：", 18)
        self._make_buttons(inp, "评估并保存",
                           self.handle_water, self.query_waters)

        lf = ttk.LabelFrame(frame, text="  📜 历史记录  ", style="Card.TLabelframe")
        lf.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        self.tree_water = self._make_tree(
            lf,
            ("time", "water_ml", "level"),
            ("时间", "饮水量 (ml)", "评级"),
            (160, 120, 120),
        )

    # ========================================================
    # Tab 4: BMI
    # ========================================================
    def _build_bmi_tab(self):
        frame = self.tab_bmi
        frame.configure(style="TFrame")

        ttk.Label(frame, text="健康助手 - BMI 评级",
                  style="Header.TLabel").pack(anchor="w", padx=20, pady=(16, 6))

        inp = ttk.LabelFrame(frame, text="  ⚖️  计算 BMI  ", style="Card.TLabelframe")
        inp.pack(fill="x", padx=20, pady=(0, 8))

        self.entry_height = self._make_input_row(inp, "身高 (厘米)：", 14)
        self.entry_weight = self._make_input_row(inp, "体重 (公斤)：", 14)
        self._make_buttons(inp, "评估并保存",
                           self.handle_bmi, self.query_bmis)

        lf = ttk.LabelFrame(frame, text="  📜 历史记录  ", style="Card.TLabelframe")
        lf.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        self.tree_bmi = self._make_tree(
            lf,
            ("time", "height", "weight", "bmi", "level"),
            ("时间", "身高 (cm)", "体重 (kg)", "BMI", "评级"),
            (130, 90, 90, 70, 80),
        )

    # ========================================================
    # Tab 5: 月度预算
    # ========================================================
    def _build_budget_tab(self):
        frame = self.tab_budget
        frame.configure(style="TFrame")

        ttk.Label(frame, text="记账助手 - 月度预算预警",
                  style="Header.TLabel").pack(anchor="w", padx=20, pady=(16, 6))

        inp = ttk.LabelFrame(frame, text="  📊 预算检查  ", style="Card.TLabelframe")
        inp.pack(fill="x", padx=20, pady=(0, 8))

        self.entry_spent = self._make_input_row(inp, "本月已花费：", 16)
        self.entry_budget = self._make_input_row(inp, "本月预算：", 16)
        self._make_buttons(inp, "检查并保存",
                           self.handle_budget, self.query_budgets)

        lf = ttk.LabelFrame(frame, text="  📜 历史记录  ", style="Card.TLabelframe")
        lf.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        self.tree_budget = self._make_tree(
            lf,
            ("time", "spent", "budget", "ratio", "status"),
            ("时间", "已花费", "预算", "使用比例", "状态"),
            (130, 90, 90, 90, 80),
        )

    # ========================================================
    # Tab 6: 睡眠
    # ========================================================
    def _build_sleep_tab(self):
        frame = self.tab_sleep
        frame.configure(style="TFrame")

        ttk.Label(frame, text="生活助手 - 睡眠时长评级",
                  style="Header.TLabel").pack(anchor="w", padx=20, pady=(16, 6))

        inp = ttk.LabelFrame(frame, text="  🌙 记录睡眠  ", style="Card.TLabelframe")
        inp.pack(fill="x", padx=20, pady=(0, 8))

        self.entry_sleep = self._make_input_row(inp, "睡眠时长 (小时)：", 16)
        self._make_buttons(inp, "评估并保存",
                           self.handle_sleep, self.query_sleeps)

        lf = ttk.LabelFrame(frame, text="  📜 历史记录  ", style="Card.TLabelframe")
        lf.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        self.tree_sleep = self._make_tree(
            lf,
            ("time", "hours", "level"),
            ("时间", "时长 (h)", "评级"),
            (160, 120, 120),
        )

    # ========================================================
    # Tab 7: 全部记录
    # ========================================================
    def _build_records_tab(self):
        frame = self.tab_records
        frame.configure(style="TFrame")

        header_row = tk.Frame(frame, bg=COLOR_BG)
        header_row.pack(fill="x", padx=20, pady=(16, 6))

        ttk.Label(header_row, text="全部记录汇总",
                  style="Header.TLabel").pack(side="left")

        ttk.Button(header_row, text="🔄 刷新全部",
                   command=self.query_all_records,
                   style="Secondary.TButton").pack(side="right")

        lf = ttk.LabelFrame(frame, text="  📋 所有记录  ", style="Card.TLabelframe")
        lf.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        self.tree_all = self._make_tree(
            lf,
            ("time", "category", "detail"),
            ("时间", "类别", "详情"),
            (140, 100, 420),
            height=14,
        )

    # ========================================================
    # 业务处理方法 —— 以下方法完全保留原有逻辑不变
    # ========================================================

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
        self._update_status()

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
            self._update_status()
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
        self._update_status()

    def query_waters(self):
        for item in self.tree_water.get_children():
            self.tree_water.delete(item)
        for r in self.backend.get_recent_records(self.data["waters"]):
            self.tree_water.insert("", "end", values=(
                self._format_time(r.get("time", "")),
                r.get("water_ml", ""),
                r.get("level", ""),
            ))

    def handle_bmi(self):
        try:
            height_cm = float(self.entry_height.get())
            weight = float(self.entry_weight.get())
        except ValueError:
            messagebox.showerror("格式错误", "请输入合法的数字！")
            return
        # 将厘米转换为米再计算 BMI
        height_m = height_cm / 100.0
        result = self.backend.evaluate_bmi(height_m, weight)
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
        bmi_val = weight / (height_m * height_m)
        self.data["bmis"].append({
            "time": self._now_str(),
            "height": height_cm,
            "weight": weight,
            "bmi": round(bmi_val, 1),
            "level": levels.get(result, result),
        })
        _save_data(self.data)
        messagebox.showinfo("BMI 评估", msgs[result])
        self.entry_height.delete(0, tk.END)
        self.entry_weight.delete(0, tk.END)
        self.query_bmis()
        self._update_status()

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
        self._update_status()

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
        self._update_status()

    def query_sleeps(self):
        for item in self.tree_sleep.get_children():
            self.tree_sleep.delete(item)
        for r in self.backend.get_recent_records(self.data["sleeps"]):
            self.tree_sleep.insert("", "end", values=(
                self._format_time(r.get("time", "")),
                r.get("hours", ""),
                r.get("level", ""),
            ))

    def query_all_records(self):
        for item in self.tree_all.get_children():
            self.tree_all.delete(item)
        all_records = []
        for r in self.data.get("transactions", []):
            all_records.append({
                "time": r.get("time", ""),
                "category": "💰 记账",
                "detail": f"金额:{r.get('amount', 0):.2f}  结果:{r.get('result', '')}  {r.get('note', '')}",
            })
        for r in self.data.get("diaries", []):
            preview = r.get("content", "")
            if len(preview) > 30:
                preview = preview[:30] + "..."
            all_records.append({
                "time": r.get("time", ""),
                "category": "📔 日记",
                "detail": f"{preview}  合规:{r.get('valid', '')}",
            })
        for r in self.data.get("waters", []):
            all_records.append({
                "time": r.get("time", ""),
                "category": "💧 饮水",
                "detail": f"{r.get('water_ml', '')}ml  评级:{r.get('level', '')}",
            })
        for r in self.data.get("bmis", []):
            all_records.append({
                "time": r.get("time", ""),
                "category": "⚖️ BMI",
                "detail": f"身高:{r.get('height', '')}cm  体重:{r.get('weight', '')}kg  BMI:{r.get('bmi', '')}  {r.get('level', '')}",
            })
        for r in self.data.get("budgets", []):
            all_records.append({
                "time": r.get("time", ""),
                "category": "💵 预算",
                "detail": f"花费:{r.get('spent', 0):.2f}  预算:{r.get('budget', 0):.2f}  比例:{r.get('ratio', '')}  {r.get('status', '')}",
            })
        for r in self.data.get("sleeps", []):
            all_records.append({
                "time": r.get("time", ""),
                "category": "😴 睡眠",
                "detail": f"{r.get('hours', '')}h  评级:{r.get('level', '')}",
            })
        recent = self.backend.get_recent_records(all_records, n=50)
        for r in recent:
            self.tree_all.insert("", "end", values=(
                self._format_time(r.get("time", "")),
                r.get("category", ""),
                r.get("detail", ""),
            ))
        self._update_status()


if __name__ == "__main__":
    root = tk.Tk()
    app = AssistantGUI(root)
    root.mainloop()
