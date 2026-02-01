import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import requests

class PenguinBusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("企鵝打卡系統 - 企鵝客運科技公司")
        self.root.geometry("1100x750")
        
        # --- 核心資料 ---
        self.VERSION = "V1.0.1"
        self.DISCORD_URL = "https://discord.com/api/webhooks/1465931295434477681/tP6bnoFmyfJRXuHUquz9WtmnGzz7GjZTUiChPa8xPBXeUNhwzY1wx_VCeg7oFM6os1gA" # 記得填入網址
        
        self.employees = {"10001": {"name": "企鵝", "branch": "企鵝總部"}}
        self.branches = ["企鵝總部", "白雲分站", "白雲總站", "企鵝大車隊"]
        self.admin_user = "admin"
        self.admin_pass = "admin"

        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True)
        
        self.show_attendance_page()

    # --- 頁面 1：打卡介面 ---
    def show_attendance_page(self):
        self.clear_window()
        header = tk.Frame(self.main_container, bg="#0066FF", height=80, bd=2, relief="raised")
        header.pack(fill="x")
        tk.Label(header, text="企鵝科技股份有限公司", font=("微軟正黑體", 36, "bold"), fg="white", bg="#0066FF").pack(side="left", padx=20)
        
        time_frame = tk.Frame(header, bg="#FF99CC", bd=2, relief="sunken")
        time_frame.pack(side="right", padx=10, pady=5)
        self.date_label = tk.Label(time_frame, text="", font=("Courier New", 14, "bold"), bg="#FF99CC")
        self.date_label.pack()
        self.clock_label = tk.Label(time_frame, text="", font=("Courier New", 24, "bold"), fg="#00FF00", bg="black")
        self.clock_label.pack(padx=10)

        body = tk.Frame(self.main_container, bg="#FFB399")
        body.pack(fill="both", expand=True)

        table_frame = tk.Frame(body, bg="white", bd=2, relief="sunken")
        table_frame.place(relx=0.02, rely=0.05, relwidth=0.7, relheight=0.85)
        
        columns = ("time", "id", "name", "status", "branch")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text={"time":"時間","id":"編號","name":"名稱","status":"狀態","branch":"分行"}[col])
        self.tree.pack(fill="both", expand=True)

        ctrl = tk.Frame(body, bg="#FFB399")
        ctrl.place(relx=0.74, rely=0.05, relwidth=0.24, relheight=0.9)

        tk.Button(ctrl, text="上 班", bg="#2E8B57", fg="white", font=("微軟正黑體", 24, "bold"), 
                  height=2, command=lambda: self.check_action("上班")).pack(fill="x", pady=10)
        tk.Button(ctrl, text="下 班", bg="#0000FF", fg="white", font=("微軟正黑體", 24, "bold"), 
                  height=2, command=lambda: self.check_action("下班")).pack(fill="x", pady=10)

        tk.Label(ctrl, text="員工編號:", bg="#FFB399", fg="red", font=("bold", 14)).pack(pady=(20, 0))
        self.id_entry = tk.Entry(ctrl, font=("Arial", 22), bg="#FFCCE6", justify="center")
        self.id_entry.pack(fill="x", pady=5)

        tk.Button(ctrl, text="管理員登入", bg="#666666", fg="white", font=("微軟正黑體", 12),
                  command=self.admin_login_ui).pack(side="bottom", pady=20)
        
        tk.Label(body, text=self.VERSION, font=("Arial", 10), bg="#FFB399", fg="#555555").place(relx=0.94, rely=0.96)
        self.update_clock()

    # --- 頁面 2：管理後台 (含開除與新增分區) ---
    def show_admin_dashboard(self):
        self.clear_window()
        admin_header = tk.Frame(self.main_container, bg="#333333", height=60)
        admin_header.pack(fill="x")
        tk.Label(admin_header, text="企鵝客運 - 高級管理後台", font=("微軟正黑體", 20, "bold"), fg="white", bg="#333333").pack(side="left", padx=20, pady=10)
        tk.Button(admin_header, text="退出管理系統", bg="#f44336", fg="white", font=("bold", 12),
                  command=self.show_attendance_page).pack(side="right", padx=20)

        notebook = ttk.Notebook(self.main_container)
        notebook.pack(fill="both", expand=True, padx=20, pady=20)

        # 頁籤 1：員工人事 (新增 + 開除)
        emp_tab = tk.Frame(notebook)
        notebook.add(emp_tab, text=" 員工人事管理 ")
        
        # 新增區
        add_f = tk.LabelFrame(emp_tab, text="新增員工入職", padx=20, pady=10)
        add_f.pack(pady=10, padx=20, fill="x")
        tk.Label(add_f, text="編號:").grid(row=0, column=0); ni = tk.Entry(add_f); ni.grid(row=0, column=1, padx=10)
        tk.Label(add_f, text="姓名:").grid(row=0, column=2); nn = tk.Entry(add_f); nn.grid(row=0, column=3, padx=10)
        tk.Label(add_f, text="分行:").grid(row=0, column=4); self.nb = ttk.Combobox(add_f, values=self.branches); self.nb.grid(row=0, column=5, padx=10)
        
        def save():
            if ni.get() and nn.get() and self.nb.get():
                self.employees[ni.get()] = {"name": nn.get(), "branch": self.nb.get()}
                messagebox.showinfo("成功", f"員工 {nn.get()} 已加入企鵝團")
            else: messagebox.showwarning("警告", "請填寫完整資訊!!!!感謝配合")
        tk.Button(add_f, text="確認入職", bg="#4CAF50", fg="white", command=save).grid(row=0, column=6, padx=10)

        # 開除區
        fire_f = tk.LabelFrame(emp_tab, text="離職/開除處理", padx=20, pady=20, fg="red")
        fire_f.pack(pady=20, padx=20, fill="x")
        tk.Label(fire_f, text="請輸入要開除的員工編號，例:10001").pack(side="left")
        fi = tk.Entry(fire_f); fi.pack(side="left", padx=10)
        
        def fire():
            eid = fi.get()
            if eid in self.employees:
                name = self.employees[eid]['name']
                if messagebox.askyesno("確認", f"確定要開除此員工 {name} 嗎？"):
                    del self.employees[eid]
                    messagebox.showwarning("完成", f"員工 {name} 已從企鵝團除名")
                    fi.delete(0, tk.END)
            else: messagebox.showerror("錯誤", "找不到該員工")
        tk.Button(fire_f, text="執行開除", bg="#f44336", fg="white", command=fire).pack(side="left")

        # 頁籤 2：分區管理 (新增 + 修改)
        branch_tab = tk.Frame(notebook)
        notebook.add(branch_tab, text=" 分區管理 ")
        
        self.branch_listbox = tk.Listbox(branch_tab, height=6, font=("Arial", 12))
        self.branch_listbox.pack(fill="x", padx=50, pady=10)
        self.refresh_branches()

        # 修改區
        edit_f = tk.Frame(branch_tab)
        edit_f.pack(pady=5)
        tk.Label(edit_f, text="選取分區後輸入新名稱:").pack(side="left")
        re_e = tk.Entry(edit_f); re_e.pack(side="left", padx=10)
        def rename():
            sel = self.branch_listbox.curselection()
            if sel and re_e.get():
                idx = sel[0]; old = self.branches[idx]
                self.branches[idx] = re_e.get()
                for e in self.employees.values():
                    if e['branch'] == old: e['branch'] = re_e.get()
                self.refresh_branches(); re_e.delete(0, tk.END)
                messagebox.showinfo("成功", "名稱已更新")
        tk.Button(edit_f, text="修改名稱", bg="#FF9800", command=rename).pack(side="left")

        # 新增分區區
        new_f = tk.Frame(branch_tab, pady=20)
        new_f.pack()
        tk.Label(new_f, text="新增分區名稱:").pack(side="left")
        new_e = tk.Entry(new_f); new_e.pack(side="left", padx=10)
        def add_b():
            if new_e.get():
                self.branches.append(new_e.get())
                self.refresh_branches(); new_e.delete(0, tk.END)
                messagebox.showinfo("成功", "新分區已建立")
        tk.Button(new_f, text="增加分區", bg="#2196F3", fg="white", command=add_b).pack(side="left")

    # --- 邏輯功能 ---
    def clear_window(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def update_clock(self):
        if hasattr(self, 'clock_label') and self.clock_label.winfo_exists():
            now = datetime.now()
            self.date_label.config(text=now.strftime("%Y年 %m月 %d日"))
            self.clock_label.config(text=now.strftime("%H:%M:%S"))
            self.root.after(1000, self.update_clock)

    def send_to_discord(self, name, eid, status):
        if "你的" in self.DISCORD_URL: return
        data = {"embeds": [{"title": "🐧 企鵝客運報告", "color": 3066993 if status == "上班" else 15158332,
                "fields": [{"name": "員工", "value": f"{name} ({eid})", "inline": True},
                           {"name": "狀態", "value": status, "inline": True},
                           {"name": "時間", "value": datetime.now().strftime("%H:%M:%S")}]}]}
        try: requests.post(self.DISCORD_URL, json=data, timeout=5)
        except: print("Discord 通知發送失敗")

    def check_action(self, status):
        eid = self.id_entry.get()
        if eid in self.employees:
            emp = self.employees[eid]
            self.tree.insert("", 0, values=(datetime.now().strftime("%H:%M:%S"), eid, emp['name'], status, emp['branch']))
            self.send_to_discord(emp['name'], eid, status)
            self.id_entry.delete(0, tk.END)
        else: messagebox.showerror("錯誤", "找不到編號")

    def admin_login_ui(self):
        login_win = tk.Toplevel(self.root)
        login_win.title("管理員登入")
        tk.Label(login_win, text="輸入管理密碼:").pack(pady=5)
        pw = tk.Entry(login_win, show="*"); pw.pack(pady=5)
        def auth():
            if pw.get() == self.admin_pass:
                login_win.destroy(); self.show_admin_dashboard()
            else: messagebox.showerror("錯誤", "密碼不正確")
        tk.Button(login_win, text="進入系統", command=auth).pack(pady=10)

    def refresh_branches(self):
        self.branch_listbox.delete(0, tk.END)
        for b in self.branches: self.branch_listbox.insert(tk.END, b)
        if hasattr(self, 'nb'): self.nb['values'] = self.branches

if __name__ == "__main__":
    root = tk.Tk()
    app = PenguinBusApp(root)
    root.mainloop()