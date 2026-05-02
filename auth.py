import tkinter as tk
from tkinter import messagebox
from database import get_connection
from utils import hash_password

MAX_ATTEMPTS = 3
current_user = None


def get_current_user():
    return current_user


def set_current_user(uid):
    global current_user
    current_user = uid


def logout():
    global current_user
    current_user = None


class LoginWindow:
    def __init__(self, root, on_success, on_signup):
        self.root            = root
        self.on_success      = on_success
        self.on_signup       = on_signup
        self.failed_attempts = 0

        self.root.title("Apex University — Login")
        self.root.geometry("420x400")
        self.root.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        outer = tk.Frame(self.root, padx=44, pady=30)
        outer.pack(expand=True)

        tk.Label(outer, text="Apex University",
                 font=("Arial", 15, "bold")).grid(row=0, columnspan=2, pady=(0, 4))
        tk.Label(outer, text="Sign in to your account",
                 fg="gray", font=("Arial", 10)).grid(row=1, columnspan=2, pady=(0, 20))

        # Role
        role_frame = tk.Frame(outer)
        role_frame.grid(row=2, columnspan=2, pady=(0, 14))
        self.role_var = tk.StringVar(value="student")
        tk.Radiobutton(role_frame, text="Student", variable=self.role_var,
                       value="student", command=self._on_role_change).pack(side="left", padx=12)
        tk.Radiobutton(role_frame, text="Admin", variable=self.role_var,
                       value="admin", command=self._on_role_change).pack(side="left", padx=12)

        # Email block
        self.email_label = tk.Label(outer, text="Email address")
        self.email_label.grid(row=3, column=0, sticky="w", pady=5)
        self.entry_email = tk.Entry(outer, width=28)
        self.entry_email.grid(row=3, column=1, pady=5)

        # Password block
        tk.Label(outer, text="Password").grid(row=4, column=0, sticky="w", pady=5)
        self.entry_pw = tk.Entry(outer, show="*", width=28)
        self.entry_pw.grid(row=4, column=1, pady=5)

        self.btn_toggle = tk.Button(outer, text="Show", relief="flat",
                                    fg="gray", command=self._toggle_pw)
        self.btn_toggle.grid(row=5, column=1, sticky="e")

        self.btn_login = tk.Button(outer, text="Sign in",
                                   command=self._do_login,
                                   bg="black", fg="white",
                                   padx=14, pady=6, relief="flat", width=22)
        self.btn_login.grid(row=6, columnspan=2, pady=(16, 0))

        self.lbl_attempts = tk.Label(outer, text="", fg="red", font=("Arial", 9))
        self.lbl_attempts.grid(row=7, columnspan=2, pady=(6, 0))

        tk.Frame(outer, height=1, bg="#cccccc").grid(
            row=8, columnspan=2, sticky="ew", pady=(18, 0))

        signup_frame = tk.Frame(outer)
        signup_frame.grid(row=9, columnspan=2, pady=(10, 0))
        tk.Label(signup_frame, text="New student?",
                 fg="gray", font=("Arial", 9)).pack(side="left")
        tk.Button(signup_frame, text="Register here",
                  relief="flat", fg="#0C447C",
                  font=("Arial", 9, "underline"),
                  cursor="hand2", bd=0,
                  command=self.on_signup).pack(side="left", padx=4)

        self.root.bind("<Return>", lambda e: self._do_login())

    def _on_role_change(self):
        role = self.role_var.get()
        self.email_label.config(
            text="Email address" if role == "student" else "Admin email")
        self.entry_email.delete(0, tk.END)
        self.entry_pw.delete(0, tk.END)
        self.lbl_attempts.config(text="")

    def _toggle_pw(self):
        if self.entry_pw.cget("show") == "*":
            self.entry_pw.config(show="")
            self.btn_toggle.config(text="Hide")
        else:
            self.entry_pw.config(show="*")
            self.btn_toggle.config(text="Show")

    def _do_login(self):
        if self.failed_attempts >= MAX_ATTEMPTS:
            messagebox.showerror("Locked",
                "Too many failed attempts. Please restart.")
            return

        email = self.entry_email.get().strip().lower()
        pw    = self.entry_pw.get()

        if not email or not pw:
            messagebox.showwarning("Missing", "Please enter your email and password.")
            return

        role = self.role_var.get()

        # Admin login (hardcoded — not in DB)
        if role == "admin":
            if (email == "admin@apex.ac.za" and
                    hash_password(pw) == hash_password("Admin123")):
                set_current_user("ADMIN01")
                self.on_success(role="admin", name="Administrator")
            else:
                self._fail_login()
            return

        # Student login — query DB by email
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM students WHERE LOWER(email) = ?",
                (email,)
            ).fetchone()

        if row and row["password"] == hash_password(pw):
            self.failed_attempts = 0
            set_current_user(row["student_id"])
            self.on_success(role="student",
                            name=f"{row['name']} {row['surname']}")
        else:
            self._fail_login()

    def _fail_login(self):
        self.failed_attempts += 1
        remaining = MAX_ATTEMPTS - self.failed_attempts
        if remaining > 0:
            self.lbl_attempts.config(
                text=f"Incorrect email or password. {remaining} attempt(s) left.")
        else:
            self.lbl_attempts.config(text="Account locked.")
            self.btn_login.config(state="disabled")
            self.entry_email.config(state="disabled")
            self.entry_pw.config(state="disabled")