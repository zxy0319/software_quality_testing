import tkinter as tk
from personal_assistant import PersonalAssistant


class AssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#f5f5f5")

        self.backend = PersonalAssistant()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)











    def handle_transaction(self):
        try:
        is_safe = self.backend.check_transaction(amount)
        if is_safe:
        else:



    def handle_diary(self):
        content = self.text_diary.get("1.0", tk.END)
        is_valid = self.backend.validate_diary(content)
        if is_valid:
        else:



    def handle_water(self):
        try:
        except ValueError:
            messagebox.showerror("格式错误", "请输入合法的整数毫升数！")

    def handle_bmi(self):
        try:
        except ValueError:


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    app = AssistantGUI(root)
    root.mainloop()