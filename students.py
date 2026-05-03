import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection, generate_student_id, init_database
from utils import (hash_password, validate_email,
                   validate_dob, validate_password)


# ── Public helpers used by other modules ──────────────────────────────────────

def get_all_students():
    """Returns all students as a list of sqlite3.Row objects."""
    with get_connection() as conn:
        return conn.execute("SELECT * FROM students ORDER BY student_id").fetchall()


def get_student_by_email(email):
    """Returns a single student row matched by email, or None."""
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM students WHERE LOWER(email) = ?",
            (email.lower(),)
        ).fetchone()


# ── Q1 Tab ────────────────────────────────────────────────────────────────────

class StudentRegistrationTab:
    def __init__(self, notebook):
        self.frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(self.frame, text="Q1 - Student Registration")
        self._build_ui()
        self._refresh_table()          # load existing students 

    def _build_ui(self):
        # ── Form ──────────────────────────────────────────────────
        form = tk.LabelFrame(self.frame, text="Register New Student",
                             padx=14, pady=14)
        form.pack(fill="x", pady=(0, 14))

        # Student ID preview (read-only)
        tk.Label(form, text="Student ID").grid(row=0, column=0, sticky="w", pady=5)
        id_row = tk.Frame(form)
        id_row.grid(row=0, column=1, sticky="w", pady=5)
        self.lbl_id = tk.Label(id_row, text=generate_student_id(),
                                bg="#dce8f7", fg="#0C447C",
                                font=("Courier", 11, "bold"), padx=8, pady=2)
        self.lbl_id.pack(side="left")
        tk.Label(id_row, text="  auto-assigned",
                 fg="gray", font=("Arial", 9)).pack(side="left")

        # Fields
        fields = [
            ("First name",    "entry_fname",   1),
            ("Surname",       "entry_surname",  2),
            ("Email",         "entry_email",    3),
            ("Phone",         "entry_phone",    4),
            ("Qualification", "entry_qual",     5),
        ]
        for label, attr, row in fields:
            tk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=5)
            entry = tk.Entry(form, width=30)
            entry.grid(row=row, column=1, sticky="w", pady=5)
            setattr(self, attr, entry)

        # Date of birth
        tk.Label(form, text="Date of birth").grid(row=6, column=0, sticky="w", pady=5)
        dob_row = tk.Frame(form)
        dob_row.grid(row=6, column=1, sticky="w", pady=5)
        self.entry_dob = tk.Entry(dob_row, width=14)
        self.entry_dob.pack(side="left")
        tk.Label(dob_row, text="  DD/MM/YYYY",
                 fg="gray", font=("Arial", 9)).pack(side="left")

        # Gender
        tk.Label(form, text="Gender").grid(row=7, column=0, sticky="w", pady=5)
        self.gender_var = tk.StringVar(value="")
        gender_frame = tk.Frame(form)
        gender_frame.grid(row=7, column=1, sticky="w")
        for g in ("Male", "Female", "Other", "Prefer not to say"):
            tk.Radiobutton(gender_frame, text=g, variable=self.gender_var,
                           value=g).pack(side="left", padx=4)

        # Year of study
        tk.Label(form, text="Year of study").grid(row=8, column=0, sticky="w", pady=5)
        self.year_var = tk.StringVar(value="1")
        year_frame = tk.Frame(form)
        year_frame.grid(row=8, column=1, sticky="w")
        for y in ("1", "2", "3", "4"):
            tk.Radiobutton(year_frame, text=f"Year {y}", variable=self.year_var,
                           value=y).pack(side="left", padx=4)

        # Password
        tk.Label(form, text="Password").grid(row=9, column=0, sticky="w", pady=5)
        pw_row = tk.Frame(form)
        pw_row.grid(row=9, column=1, sticky="w", pady=5)
        self.entry_pw = tk.Entry(pw_row, show="*", width=22)
        self.entry_pw.pack(side="left")
        self.btn_toggle_pw = tk.Button(pw_row, text="Show", relief="flat",
                                       fg="gray", command=self._toggle_pw)
        self.btn_toggle_pw.pack(side="left", padx=5)
        tk.Label(pw_row, text="  8+ chars, 1 uppercase, 1 number",
                 fg="gray", font=("Arial", 9)).pack(side="left")

        # Confirm password
        tk.Label(form, text="Confirm password").grid(row=10, column=0, sticky="w", pady=5)
        pw2_row = tk.Frame(form)
        pw2_row.grid(row=10, column=1, sticky="w", pady=5)
        self.entry_pw2 = tk.Entry(pw2_row, show="*", width=22)
        self.entry_pw2.pack(side="left")
        self.btn_toggle_pw2 = tk.Button(pw2_row, text="Show", relief="flat",
                                        fg="gray", command=self._toggle_pw2)
        self.btn_toggle_pw2.pack(side="left", padx=5)

        # Register button
        tk.Button(form, text="Register Student", command=self._register,
                  bg="black", fg="white", padx=12, pady=5,
                  relief="flat").grid(row=11, columnspan=2, pady=(14, 0), sticky="w")

        # ── Table ─────────────────────────────────────────────────
        table_frame = tk.LabelFrame(self.frame, text="All Students",
                                    padx=14, pady=14)
        table_frame.pack(fill="both", expand=True)

        search_bar = tk.Frame(table_frame)
        search_bar.pack(fill="x", pady=(0, 8))
        tk.Label(search_bar, text="Search:").pack(side="left")
        self.entry_search = tk.Entry(search_bar, width=26)
        self.entry_search.pack(side="left", padx=6)
        self.entry_search.bind("<KeyRelease>", lambda e: self._refresh_table())
        tk.Button(search_bar, text="Delete Selected", fg="red",
                  relief="flat", command=self._delete_student).pack(side="right")

        cols = ("ID", "Name", "Surname", "DOB", "Email", "Phone", "Year")
        self.tree = ttk.Treeview(table_frame, columns=cols,
                                  show="headings", height=7)
        widths = {"ID": 80, "Name": 100, "Surname": 100,
                  "DOB": 90, "Email": 170, "Phone": 100, "Year": 50}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths[col])

        sb = ttk.Scrollbar(table_frame, orient="vertical",
                           command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    # ── Helpers ───────────────────────────────────────────────────

    def _toggle_pw(self):
        show = "" if self.entry_pw.cget("show") == "*" else "*"
        self.entry_pw.config(show=show)
        self.btn_toggle_pw.config(text="Hide" if show == "" else "Show")

    def _toggle_pw2(self):
        show = "" if self.entry_pw2.cget("show") == "*" else "*"
        self.entry_pw2.config(show=show)
        self.btn_toggle_pw2.config(text="Hide" if show == "" else "Show")

    def _register(self):
        fname   = self.entry_fname.get().strip()
        surname = self.entry_surname.get().strip()
        dob_s   = self.entry_dob.get().strip()
        email   = self.entry_email.get().strip().lower()
        phone   = self.entry_phone.get().strip()
        qual    = self.entry_qual.get().strip()
        gender  = self.gender_var.get()
        year    = int(self.year_var.get())
        pw      = self.entry_pw.get()
        pw2     = self.entry_pw2.get()

        # Validation
        if not all([fname, surname, dob_s, email, pw, pw2]):
            messagebox.showerror("Error", "All required fields must be filled in.")
            return
        if not fname.replace(" ", "").isalpha():
            messagebox.showerror("Error", "First name must contain letters only.")
            return
        if not surname.replace(" ", "").isalpha():
            messagebox.showerror("Error", "Surname must contain letters only.")
            return

        dob_ok, dob_val = validate_dob(dob_s)
        if not dob_ok:
            messagebox.showerror("Error", dob_val)
            return
        if not validate_email(email):
            messagebox.showerror("Error", "Please enter a valid email address.")
            return

        pw_ok, pw_err = validate_password(pw)
        if not pw_ok:
            messagebox.showerror("Error", pw_err)
            return
        if pw != pw2:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        # Save to database
        sid = generate_student_id()
        try:
            with get_connection() as conn:
                conn.execute("""
                    INSERT INTO students
                        (student_id, name, surname, date_of_birth, gender,
                         email, phone, password, qualification, year_of_study)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (sid, fname, surname, dob_val, gender,
                      email, phone, hash_password(pw), qual, year))
        except Exception as e:
            if "UNIQUE" in str(e):
                messagebox.showerror("Error",
                    "That email address is already registered.")
            else:
                messagebox.showerror("Database Error", str(e))
            return

        # Clear form and refresh
        for entry in [self.entry_fname, self.entry_surname, self.entry_dob,
                      self.entry_email, self.entry_phone, self.entry_qual,
                      self.entry_pw, self.entry_pw2]:
            entry.delete(0, tk.END)
        self.gender_var.set("")
        self.year_var.set("1")
        self.lbl_id.config(text=generate_student_id())
        self._refresh_table()
        messagebox.showinfo("Success",
                            f"Student registered!\nID: {sid}\nName: {fname} {surname}")

    def _delete_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please click a student row first.")
            return
        sid = self.tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirm Delete",
                               f"Permanently delete student {sid}?\n"
                               "This will also remove their enrollments and marks."):
            with get_connection() as conn:
                conn.execute("DELETE FROM students WHERE student_id = ?", (sid,))
            self._refresh_table()

    def _refresh_table(self):
        query = self.entry_search.get().strip().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT student_id, name, surname, date_of_birth, email, phone, year_of_study
                FROM students
                ORDER BY student_id
            """).fetchall()
        for r in rows:
            sid, name, surname, dob, email, phone, year = (
                r["student_id"], r["name"], r["surname"],
                r["date_of_birth"], r["email"], r["phone"], r["year_of_study"]
            )
            if (query in (sid or "").lower() or
                    query in (name or "").lower() or
                    query in (surname or "").lower() or
                    query in (email or "").lower()):
                self.tree.insert("", tk.END,
                                 values=(sid, name, surname, dob,
                                         email, phone or "—", year))