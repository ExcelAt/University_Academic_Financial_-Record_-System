import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection, generate_course_id
from utils import validate_fee, validate_duration


# ── Public helpers used by other modules ──────────────────────────────────────

def get_all_courses():
    """Returns all courses as a list of sqlite3.Row objects."""
    with get_connection() as conn:
        return conn.execute("SELECT * FROM courses ORDER BY course_id").fetchall()


# ── Q2 Tab ────────────────────────────────────────────────────────────────────

class CourseManagementTab:
    def __init__(self, notebook):
        self.frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(self.frame, text="Q2 - Course Management")
        self._build_ui()
        self._refresh_table()          # load existing courses on startup

    def _build_ui(self):
        # ── Form ──────────────────────────────────────────────────
        form = tk.LabelFrame(self.frame, text="Add New Course",
                             padx=14, pady=14)
        form.pack(fill="x", pady=(0, 14))

        # Course ID preview (read-only)
        tk.Label(form, text="Course ID").grid(row=0, column=0, sticky="w", pady=5)
        id_row = tk.Frame(form)
        id_row.grid(row=0, column=1, sticky="w", pady=5)
        self.lbl_course_id = tk.Label(id_row, text=generate_course_id(),
                                       bg="#e8f5e9", fg="#1B5E20",
                                       font=("Courier", 11, "bold"), padx=8, pady=2)
        self.lbl_course_id.pack(side="left")
        tk.Label(id_row, text="  auto-assigned",
                 fg="gray", font=("Arial", 9)).pack(side="left")

        # Course name
        tk.Label(form, text="Course name").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_name = tk.Entry(form, width=34)
        self.entry_name.grid(row=1, column=1, sticky="w", pady=5)

        # Course code
        tk.Label(form, text="Course code").grid(row=2, column=0, sticky="w", pady=5)
        code_row = tk.Frame(form)
        code_row.grid(row=2, column=1, sticky="w", pady=5)
        self.entry_code = tk.Entry(code_row, width=16)
        self.entry_code.pack(side="left")
        tk.Label(code_row, text="  e.g. CMPN201",
                 fg="gray", font=("Arial", 9)).pack(side="left")

        # Course fee
        tk.Label(form, text="Course fee (R)").grid(row=3, column=0, sticky="w", pady=5)
        fee_row = tk.Frame(form)
        fee_row.grid(row=3, column=1, sticky="w", pady=5)
        tk.Label(fee_row, text="R ").pack(side="left")
        self.entry_fee = tk.Entry(fee_row, width=14)
        self.entry_fee.pack(side="left")

        # Duration
        tk.Label(form, text="Duration").grid(row=4, column=0, sticky="w", pady=5)
        dur_row = tk.Frame(form)
        dur_row.grid(row=4, column=1, sticky="w", pady=5)
        self.entry_duration = tk.Entry(dur_row, width=20)
        self.entry_duration.pack(side="left")
        tk.Label(dur_row, text="  e.g. 6 Months, 1 Year",
                 fg="gray", font=("Arial", 9)).pack(side="left")

        # Credits
        tk.Label(form, text="Credits").grid(row=5, column=0, sticky="w", pady=5)
        self.entry_credits = tk.Entry(form, width=8)
        self.entry_credits.insert(0, "12")
        self.entry_credits.grid(row=5, column=1, sticky="w", pady=5)

        # Semester
        tk.Label(form, text="Semester").grid(row=6, column=0, sticky="w", pady=5)
        self.sem_var = tk.StringVar(value="S1")
        sem_frame = tk.Frame(form)
        sem_frame.grid(row=6, column=1, sticky="w")
        for s in ("S1", "S2", "Year"):
            tk.Radiobutton(sem_frame, text=s, variable=self.sem_var,
                           value=s).pack(side="left", padx=6)

        # Lecturer
        tk.Label(form, text="Lecturer").grid(row=7, column=0, sticky="w", pady=5)
        self.entry_lecturer = tk.Entry(form, width=30)
        self.entry_lecturer.grid(row=7, column=1, sticky="w", pady=5)

        # Buttons
        btn_row = tk.Frame(form)
        btn_row.grid(row=8, columnspan=2, sticky="w", pady=(14, 0))
        tk.Button(btn_row, text="Add Course", command=self._add_course,
                  bg="black", fg="white", padx=12, pady=5,
                  relief="flat").pack(side="left", padx=(0, 8))
        tk.Button(btn_row, text="Clear", command=self._clear_form,
                  relief="flat", padx=10, pady=5).pack(side="left")

        # ── Search + Table ─────────────────────────────────────────
        search_bar = tk.Frame(self.frame)
        search_bar.pack(fill="x", pady=(8, 4))
        tk.Label(search_bar, text="Search:").pack(side="left")
        self.entry_search = tk.Entry(search_bar, width=26)
        self.entry_search.pack(side="left", padx=6)
        self.entry_search.bind("<KeyRelease>", lambda e: self._refresh_table())
        tk.Button(search_bar, text="Delete Selected", fg="red",
                  relief="flat", command=self._delete_course).pack(side="right")

        table_frame = tk.LabelFrame(self.frame, text="Course Catalogue",
                                    padx=14, pady=14)
        table_frame.pack(fill="both", expand=True)

        cols = ("Course ID", "Course Name", "Code", "Fee (R)",
                "Duration", "Credits", "Semester", "Lecturer")
        self.tree = ttk.Treeview(table_frame, columns=cols,
                                  show="headings", height=7)
        widths = {"Course ID": 75, "Course Name": 180, "Code": 90,
                  "Fee (R)": 80, "Duration": 90,
                  "Credits": 60, "Semester": 70, "Lecturer": 130}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths[col])

        sb = ttk.Scrollbar(table_frame, orient="vertical",
                           command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", self._on_double_click)

    # ── Helpers ───────────────────────────────────────────────────

    def _add_course(self):
        name     = self.entry_name.get().strip()
        code     = self.entry_code.get().strip().upper()
        fee_s    = self.entry_fee.get().strip()
        dur_s    = self.entry_duration.get().strip()
        cred_s   = self.entry_credits.get().strip()
        semester = self.sem_var.get()
        lecturer = self.entry_lecturer.get().strip() or "TBA"

        if not all([name, code, fee_s, dur_s]):
            messagebox.showerror("Error",
                "Course name, code, fee, and duration are required.")
            return
        if not code.isalnum():
            messagebox.showerror("Error",
                "Course code must be letters and numbers only (e.g. CMPN201).")
            return

        fee_ok, fee_val = validate_fee(fee_s)
        if not fee_ok:
            messagebox.showerror("Error", fee_val)
            return

        dur_ok, dur_val = validate_duration(dur_s)
        if not dur_ok:
            messagebox.showerror("Error", dur_val)
            return

        credits = int(cred_s) if cred_s.isdigit() else 12

        cid = generate_course_id()
        try:
            with get_connection() as conn:
                conn.execute("""
                    INSERT INTO courses
                        (course_id, course_name, course_code, duration,
                         credits, semester, fee, lecturer)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (cid, name, code, dur_val,
                      credits, semester, fee_val, lecturer))
        except Exception as e:
            if "UNIQUE" in str(e):
                messagebox.showerror("Error",
                    f"Course code '{code}' is already in use.")
            else:
                messagebox.showerror("Database Error", str(e))
            return

        self.lbl_course_id.config(text=generate_course_id())
        self._clear_form()
        self._refresh_table()
        messagebox.showinfo("Success",
                            f"Course added!\nID: {cid}\nName: {name}")

    def _delete_course(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please click a course row first.")
            return
        cid = self.tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirm Delete",
                               f"Delete course '{cid}'?\n"
                               "This will also remove related enrollments and marks."):
            with get_connection() as conn:
                conn.execute("DELETE FROM courses WHERE course_id = ?", (cid,))
            self._refresh_table()

    def _clear_form(self):
        for entry in [self.entry_name, self.entry_code,
                      self.entry_fee, self.entry_duration, self.entry_lecturer]:
            entry.delete(0, tk.END)
        self.entry_credits.delete(0, tk.END)
        self.entry_credits.insert(0, "12")
        self.sem_var.set("S1")

    def _on_double_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        vals = self.tree.item(selected[0])["values"]
        self._clear_form()
        self.entry_name.insert(0, vals[1])
        self.entry_code.insert(0, vals[2])
        self.entry_fee.insert(0, str(vals[3]))
        self.entry_duration.insert(0, vals[4])
        self.entry_credits.delete(0, tk.END)
        self.entry_credits.insert(0, str(vals[5]))
        self.sem_var.set(vals[6])
        self.entry_lecturer.insert(0, vals[7])

    def _refresh_table(self):
        query = self.entry_search.get().strip().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT course_id, course_name, course_code, fee,
                       duration, credits, semester, lecturer
                FROM courses ORDER BY course_id
            """).fetchall()
        for r in rows:
            if (query in r["course_id"].lower() or
                    query in r["course_name"].lower() or
                    query in r["course_code"].lower()):
                self.tree.insert("", tk.END, values=(
                    r["course_id"], r["course_name"], r["course_code"],
                    f"{r['fee']:,.2f}", r["duration"],
                    r["credits"], r["semester"], r["lecturer"] or "TBA"
                ))