import tkinter as tk
from tkinter import messagebox
from database import get_connection, generate_student_id
from utils import (hash_password, validate_email,
                   validate_dob, validate_password)


class SignUpWindow:
    """
    Self-registration window opened from the login screen.
    Inserts a new student directly into the SQLite database.
    """

    def __init__(self, parent, on_complete):
        self.on_complete = on_complete

        self.win = tk.Toplevel(parent)
        self.win.title("Apex University — Student Registration")
        self.win.geometry("500x520")
        self.win.resizable(False, False)
        self.win.grab_set()
        self._build_ui()

    def _build_ui(self):
        outer = tk.Frame(self.win, padx=38, pady=24)
        outer.pack(fill="both", expand=True)

        tk.Label(outer, text="Create your student account",
                 font=("Arial", 13, "bold")).grid(row=0, columnspan=2, pady=(0, 4))
        tk.Label(outer,
                 text="Your Student ID will be assigned automatically on submission.",
                 fg="gray", font=("Arial", 9),
                 wraplength=400).grid(row=1, columnspan=2, pady=(0, 16))

        # Student ID preview
        tk.Label(outer, text="Student ID").grid(row=2, column=0, sticky="w", pady=5)
        id_row = tk.Frame(outer)
        id_row.grid(row=2, column=1, sticky="w", pady=5)
        self.lbl_id = tk.Label(id_row, text=generate_student_id(),
                                bg="#dce8f7", fg="#0C447C",
                                font=("Courier", 11, "bold"), padx=8, pady=2)
        self.lbl_id.pack(side="left")
        tk.Label(id_row, text="  assigned on submit",
                 fg="gray", font=("Arial", 9)).pack(side="left")

        # First name
        tk.Label(outer, text="First name").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_fname = tk.Entry(outer, width=30)
        self.entry_fname.grid(row=3, column=1, sticky="w", pady=5)

        # Surname
        tk.Label(outer, text="Surname").grid(row=4, column=0, sticky="w", pady=5)
        self.entry_surname = tk.Entry(outer, width=30)
        self.entry_surname.grid(row=4, column=1, sticky="w", pady=5)

        # Date of birth
        tk.Label(outer, text="Date of birth").grid(row=5, column=0, sticky="w", pady=5)
        dob_row = tk.Frame(outer)
        dob_row.grid(row=5, column=1, sticky="w", pady=5)
        self.entry_dob = tk.Entry(dob_row, width=14)
        self.entry_dob.pack(side="left")
        tk.Label(dob_row, text="  DD/MM/YYYY",
                 fg="gray", font=("Arial", 9)).pack(side="left")

        # Email
        tk.Label(outer, text="Email").grid(row=6, column=0, sticky="w", pady=5)
        self.entry_email = tk.Entry(outer, width=30)
        self.entry_email.grid(row=6, column=1, sticky="w", pady=5)

        # Phone
        tk.Label(outer, text="Phone").grid(row=7, column=0, sticky="w", pady=5)
        self.entry_phone = tk.Entry(outer, width=20)
        self.entry_phone.grid(row=7, column=1, sticky="w", pady=5)

        # Password
        tk.Label(outer, text="Password").grid(row=8, column=0, sticky="w", pady=5)
        pw_row = tk.Frame(outer)
        pw_row.grid(row=8, column=1, sticky="w", pady=5)
        self.entry_pw = tk.Entry(pw_row, show="*", width=22)
        self.entry_pw.pack(side="left")
        self.btn_t1 = tk.Button(pw_row, text="Show", relief="flat",
                                 fg="gray", command=self._toggle_pw)
        self.btn_t1.pack(side="left", padx=5)

        # Confirm password
        tk.Label(outer, text="Confirm password").grid(row=9, column=0, sticky="w", pady=5)
        pw2_row = tk.Frame(outer)
        pw2_row.grid(row=9, column=1, sticky="w", pady=5)
        self.entry_pw2 = tk.Entry(pw2_row, show="*", width=22)
        self.entry_pw2.pack(side="left")
        self.btn_t2 = tk.Button(pw2_row, text="Show", relief="flat",
                                  fg="gray", command=self._toggle_pw2)
        self.btn_t2.pack(side="left", padx=5)

        tk.Label(outer, text="8+ characters, 1 uppercase letter, 1 number",
                 fg="gray", font=("Arial", 8)).grid(row=10, columnspan=2, pady=(2, 0))

        # Buttons
        btn_row = tk.Frame(outer)
        btn_row.grid(row=11, columnspan=2, pady=(16, 0))
        tk.Button(btn_row, text="Create Account",
                  command=self._submit,
                  bg="black", fg="white",
                  padx=14, pady=6, relief="flat").pack(side="left", padx=(0, 10))
        tk.Button(btn_row, text="Cancel",
                  command=self.win.destroy,
                  relief="flat", padx=10, pady=6).pack(side="left")

    def _toggle_pw(self):
        show = "" if self.entry_pw.cget("show") == "*" else "*"
        self.entry_pw.config(show=show)
        self.btn_t1.config(text="Hide" if show == "" else "Show")

    def _toggle_pw2(self):
        show = "" if self.entry_pw2.cget("show") == "*" else "*"
        self.entry_pw2.config(show=show)
        self.btn_t2.config(text="Hide" if show == "" else "Show")

    def _submit(self):
        fname   = self.entry_fname.get().strip()
        surname = self.entry_surname.get().strip()
        dob_s   = self.entry_dob.get().strip()
        email   = self.entry_email.get().strip().lower()
        phone   = self.entry_phone.get().strip()
        pw      = self.entry_pw.get()
        pw2     = self.entry_pw2.get()

        if not all([fname, surname, dob_s, email, pw, pw2]):
            messagebox.showerror("Error", "All fields except phone are required.",
                                 parent=self.win)
            return
        if not fname.replace(" ", "").isalpha():
            messagebox.showerror("Error", "First name must contain letters only.",
                                 parent=self.win)
            return
        if not surname.replace(" ", "").isalpha():
            messagebox.showerror("Error", "Surname must contain letters only.",
                                 parent=self.win)
            return

        dob_ok, dob_val = validate_dob(dob_s)
        if not dob_ok:
            messagebox.showerror("Error", dob_val, parent=self.win)
            return
        if not validate_email(email):
            messagebox.showerror("Error", "Please enter a valid email address.",
                                 parent=self.win)
            return

        pw_ok, pw_err = validate_password(pw)
        if not pw_ok:
            messagebox.showerror("Error", pw_err, parent=self.win)
            return
        if pw != pw2:
            messagebox.showerror("Error", "Passwords do not match.",
                                 parent=self.win)
            return

        sid = generate_student_id()
        try:
            with get_connection() as conn:
                conn.execute("""
                    INSERT INTO students
                        (student_id, name, surname, date_of_birth,
                         email, phone, password)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (sid, fname, surname, dob_val,
                      email, phone, hash_password(pw)))
        except Exception as e:
            if "UNIQUE" in str(e):
                messagebox.showerror("Error",
                    "That email address is already registered.",
                    parent=self.win)
            else:
                messagebox.showerror("Database Error", str(e), parent=self.win)
            return

        messagebox.showinfo(
            "Account Created",
            f"Welcome, {fname} {surname}!\n\n"
            f"Your Student ID:  {sid}\n\n"
            f"Please save your Student ID.\n"
            f"You can now log in with your email and password.",
            parent=self.win)

        self.win.destroy()
        self.on_complete()