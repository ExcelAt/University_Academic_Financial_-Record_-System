import tkinter as tk
from tkinter import ttk, messagebox

#imp
from database import init_database
from auth import LoginWindow, get_current_user
from signUp import SignUpWindow
from students import StudentRegistrationTab
from courses import CourseManagementTab
from studentPortal import StudentPortalTab
from studentPortal import StudentPortalTab
from reports import ReportsTab, WarningTab

#creating admin dashboard for differnet access levels
class AdminDashboard:
    """Full access dashboard — only shown to admins."""

    def __init__(self, root, name):
        self.root = root
        self.name = name
        self.root.title("Apex University — Admin Dashboard")
        self.root.geometry("960x680")
        self.root.resizable(True, True)
        self._build_ui()

    def _build_ui(self):
        # Top bar
        top = tk.Frame(self.root, bg="#0C447C", pady=10, padx=16)
        top.pack(fill="x")
        tk.Label(top, text="Apex University — Admin Panel",
                 bg="#0C447C", fg="white",
                 font=("Arial", 13, "bold")).pack(side="left")
        info = tk.Frame(top, bg="#0C447C")
        info.pack(side="right")
        tk.Label(info, text=f"{self.name}  |  Admin",
                 bg="#0C447C", fg="#B5D4F4",
                 font=("Arial", 10)).pack(side="left", padx=(0, 12))
        tk.Button(info, text="Logout", command=self._logout,
                  bg="#1a5fa8", fg="white", relief="flat",
                  padx=10, pady=2).pack(side="left")

        # Tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        StudentRegistrationTab(notebook)   # Q1
        CourseManagementTab(notebook)      # Q2

        # Placeholder tabs for Q3–Q8
        for label in ["Q3 - Enrollment", "Q4 - Marks",
                      "Q5 - Fee Payment", "Q6 - Academic Risk",
                      "Q7 - Reports", "Q8 - Warning Letters"]:
            f = tk.Frame(notebook, padx=20, pady=20)
            notebook.add(f, text=label)
            tk.Label(f, text=f"{label}\n\nComing soon...",
                     fg="gray", font=("Arial", 11),
                     justify="center").pack(pady=60)

        tk.Label(self.root,
                 text="Data auto-saved to data/apex.db",
                 fg="gray", font=("Arial", 8)).pack(pady=(0, 4))

        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            _start_app()


class StudentDashboard:
    """Limited dashboard — only shown to students."""

    def __init__(self, root, name, student_id):
        self.root       = root
        self.name       = name
        self.student_id = student_id
        self.root.title("Apex University — Student Portal")
        self.root.geometry("860x620")
        self.root.resizable(True, True)
        self._build_ui()

    def _build_ui(self):
        # Top bar
        top = tk.Frame(self.root, bg="#1B5E20", pady=10, padx=16)
        top.pack(fill="x")
        tk.Label(top, text="Apex University — Student Portal",
                 bg="#1B5E20", fg="white",
                 font=("Arial", 13, "bold")).pack(side="left")
        info = tk.Frame(top, bg="#1B5E20")
        info.pack(side="right")
        tk.Label(info, text=f"{self.name}  |  Student  |  {self.student_id}",
                 bg="#1B5E20", fg="#C8E6C9",
                 font=("Arial", 10)).pack(side="left", padx=(0, 12))
        tk.Button(info, text="Logout", command=self._logout,
                  bg="#2e7d32", fg="white", relief="flat",
                  padx=10, pady=2).pack(side="left")

        # Tabs — students only see their own portal
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        StudentPortalTab(notebook, self.student_id)

        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            _start_app()


def _start_app():
    root = tk.Tk()
    root.title("Apex University — Login")

    init_database()

    def on_login_success(role, name):
        sid = get_current_user()
        for widget in root.winfo_children():
            widget.destroy()
        if role == "admin":
            AdminDashboard(root, name=name)
        else:
            StudentDashboard(root, name=name, student_id=sid)

    def on_signup():
        SignUpWindow(root, on_complete=lambda: None)

    LoginWindow(root, on_success=on_login_success, on_signup=on_signup)
    root.mainloop()


if __name__ == "__main__":
    _start_app()