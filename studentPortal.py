"""
Student Portal — Q3 (partial) + Fee view
Students can:
  - View their profile
  - Browse available courses
  - Enroll in courses (max 6)
  - View their enrolled courses and fees
  - Unenroll from a course
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import get_connection

MAX_COURSES = 6


class StudentPortalTab:
    def __init__(self, notebook, student_id):
        self.student_id = student_id

        # ── Tab 1: My Profile ─────────────────────────────────────
        self.profile_frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(self.profile_frame, text="My Profile")
        self._build_profile()

        # ── Tab 2: Enroll in Courses ──────────────────────────────
        self.enroll_frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(self.enroll_frame, text="Enroll in Courses")
        self._build_enrollment()

        # ── Tab 3: My Courses & Fees ──────────────────────────────
        self.courses_frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(self.courses_frame, text="My Courses & Fees")
        self._build_my_courses()

    # ── Profile tab ───────────────────────────────────────────────

    def _build_profile(self):
        tk.Label(self.profile_frame, text="My Profile",
                 font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 16))

        info_frame = tk.LabelFrame(self.profile_frame,
                                   text="Personal Details",
                                   padx=16, pady=16)
        info_frame.pack(fill="x")

        with get_connection() as conn:
            s = conn.execute(
                "SELECT * FROM students WHERE student_id = ?",
                (self.student_id,)
            ).fetchone()

        if not s:
            tk.Label(info_frame, text="Student not found.",
                     fg="red").pack()
            return

        fields = [
            ("Student ID",     s["student_id"]),
            ("First name",     s["name"]),
            ("Surname",        s["surname"]),
            ("Date of birth",  s["date_of_birth"] or "—"),
            ("Email",          s["email"]),
            ("Phone",          s["phone"] or "—"),
            ("Qualification",  s["qualification"] or "—"),
            ("Year of study",  f"Year {s['year_of_study']}"),
            ("Registered on",  (s["registered_on"] or "")[:10]),
        ]
        for i, (label, value) in enumerate(fields):
            tk.Label(info_frame, text=label + ":",
                     font=("Arial", 10, "bold"),
                     width=16, anchor="w").grid(
                         row=i, column=0, sticky="w", pady=3)
            tk.Label(info_frame, text=value,
                     font=("Arial", 10)).grid(
                         row=i, column=1, sticky="w", pady=3, padx=8)

    # ── Enrollment tab ────────────────────────────────────────────

    def _build_enrollment(self):
        tk.Label(self.enroll_frame,
                 text="Enroll in a Course",
                 font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 4))
        tk.Label(self.enroll_frame,
                 text=f"You may enroll in a maximum of {MAX_COURSES} courses.",
                 fg="gray", font=("Arial", 9)).pack(anchor="w", pady=(0, 12))

        # Enrollment count badge
        self.lbl_count = tk.Label(self.enroll_frame, text="",
                                   font=("Arial", 10), fg="#0C447C")
        self.lbl_count.pack(anchor="w", pady=(0, 8))

        # Search bar
        search_bar = tk.Frame(self.enroll_frame)
        search_bar.pack(fill="x", pady=(0, 6))
        tk.Label(search_bar, text="Search courses:").pack(side="left")
        self.enroll_search = tk.Entry(search_bar, width=28)
        self.enroll_search.pack(side="left", padx=6)
        self.enroll_search.bind("<KeyRelease>",
                                lambda e: self._refresh_available())

        # Available courses table
        avail_frame = tk.LabelFrame(self.enroll_frame,
                                    text="Available Courses",
                                    padx=10, pady=10)
        avail_frame.pack(fill="both", expand=True)

        cols = ("Course ID", "Course Name", "Code",
                "Fee (R)", "Duration", "Semester", "Lecturer")
        self.avail_tree = ttk.Treeview(avail_frame, columns=cols,
                                        show="headings", height=10)
        widths = {"Course ID": 75, "Course Name": 180, "Code": 90,
                  "Fee (R)": 80, "Duration": 90,
                  "Semester": 70, "Lecturer": 130}
        for col in cols:
            self.avail_tree.heading(col, text=col)
            self.avail_tree.column(col, width=widths[col])

        sb = ttk.Scrollbar(avail_frame, orient="vertical",
                           command=self.avail_tree.yview)
        self.avail_tree.configure(yscrollcommand=sb.set)
        self.avail_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        tk.Button(self.enroll_frame,
                  text="Enroll in Selected Course",
                  command=self._enroll,
                  bg="black", fg="white",
                  padx=12, pady=6, relief="flat").pack(pady=(10, 0))

        self._refresh_available()

    def _refresh_available(self):
        self._update_count_label()
        query = self.enroll_search.get().strip().lower()

        # Get courses student is already enrolled in
        with get_connection() as conn:
            enrolled = {
                row["course_id"]
                for row in conn.execute(
                    "SELECT course_id FROM enrollments WHERE student_id = ?",
                    (self.student_id,)
                ).fetchall()
            }
            all_courses = conn.execute(
                "SELECT * FROM courses ORDER BY course_id"
            ).fetchall()

        for row in self.avail_tree.get_children():
            self.avail_tree.delete(row)

        for c in all_courses:
            if c["course_id"] in enrolled:
                continue          # hide already-enrolled courses
            if query and not (
                query in c["course_id"].lower() or
                query in c["course_name"].lower() or
                query in c["course_code"].lower()
            ):
                continue
            self.avail_tree.insert("", tk.END, values=(
                c["course_id"], c["course_name"], c["course_code"],
                f"{c['fee']:,.2f}", c["duration"] or "—",
                c["semester"] or "—", c["lecturer"] or "TBA"
            ))

    def _enroll(self):
        selected = self.avail_tree.selection()
        if not selected:
            messagebox.showwarning("No selection",
                                   "Please click a course to select it first.")
            return

        # Check max courses
        with get_connection() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM enrollments WHERE student_id = ?",
                (self.student_id,)
            ).fetchone()[0]

        if count >= MAX_COURSES:
            messagebox.showerror(
                "Maximum reached",
                f"You are already enrolled in {MAX_COURSES} courses.\n"
                "You must unenroll from a course before adding a new one.")
            return

        course_id   = self.avail_tree.item(selected[0])["values"][0]
        course_name = self.avail_tree.item(selected[0])["values"][1]

        if not messagebox.askyesno("Confirm Enrollment",
                                   f"Enroll in '{course_name}'?"):
            return

        year     = datetime.now().year
        semester = "S1"
        try:
            with get_connection() as conn:
                conn.execute("""
                    INSERT INTO enrollments
                        (student_id, course_id, academic_year, semester)
                    VALUES (?, ?, ?, ?)
                """, (self.student_id, course_id, year, semester))
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        messagebox.showinfo("Enrolled",
                            f"You have been enrolled in '{course_name}'.")
        self._refresh_available()
        self._refresh_my_courses()

    def _update_count_label(self):
        with get_connection() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM enrollments WHERE student_id = ?",
                (self.student_id,)
            ).fetchone()[0]
        remaining = MAX_COURSES - count
        color = "#c0392b" if count >= MAX_COURSES else "#0C447C"
        self.lbl_count.config(
            text=f"Enrolled in {count} of {MAX_COURSES} courses  "
                 f"({remaining} slot(s) remaining)",
            fg=color)

    # ── My Courses & Fees tab ─────────────────────────────────────

    def _build_my_courses(self):
        tk.Label(self.courses_frame,
                 text="My Courses & Fees",
                 font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 12))

        # Summary bar
        self.summary_frame = tk.Frame(self.courses_frame)
        self.summary_frame.pack(fill="x", pady=(0, 10))

        self.lbl_total = tk.Label(self.summary_frame,
                                   text="Total fees: R 0.00",
                                   font=("Arial", 11, "bold"))
        self.lbl_total.pack(side="left")

        # Enrolled courses table
        table_frame = tk.LabelFrame(self.courses_frame,
                                    text="My Enrolled Courses",
                                    padx=10, pady=10)
        table_frame.pack(fill="both", expand=True)

        cols = ("Course ID", "Course Name", "Code",
                "Fee (R)", "Duration", "Semester", "Enrolled On")
        self.my_tree = ttk.Treeview(table_frame, columns=cols,
                                     show="headings", height=10)
        widths = {"Course ID": 75, "Course Name": 180, "Code": 90,
                  "Fee (R)": 80, "Duration": 90,
                  "Semester": 70, "Enrolled On": 100}
        for col in cols:
            self.my_tree.heading(col, text=col)
            self.my_tree.column(col, width=widths[col])

        sb = ttk.Scrollbar(table_frame, orient="vertical",
                           command=self.my_tree.yview)
        self.my_tree.configure(yscrollcommand=sb.set)
        self.my_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        tk.Button(self.courses_frame,
                  text="Unenroll from Selected Course",
                  command=self._unenroll,
                  fg="red", relief="flat",
                  padx=12, pady=6).pack(pady=(10, 0))

        self._refresh_my_courses()

    def _refresh_my_courses(self):
        for row in self.my_tree.get_children():
            self.my_tree.delete(row)

        with get_connection() as conn:
            rows = conn.execute("""
                SELECT c.course_id, c.course_name, c.course_code,
                       c.fee, c.duration, e.semester, e.enrolled_on
                FROM enrollments e
                JOIN courses c ON e.course_id = c.course_id
                WHERE e.student_id = ?
                ORDER BY e.enrolled_on
            """, (self.student_id,)).fetchall()

        total = 0.0
        for r in rows:
            enrolled_date = (r["enrolled_on"] or "")[:10]
            self.my_tree.insert("", tk.END, values=(
                r["course_id"], r["course_name"], r["course_code"],
                f"{r['fee']:,.2f}", r["duration"] or "—",
                r["semester"], enrolled_date
            ))
            total += r["fee"] or 0.0

        self.lbl_total.config(
            text=f"Total fees:  R {total:,.2f}")

    def _unenroll(self):
        selected = self.my_tree.selection()
        if not selected:
            messagebox.showwarning("No selection",
                                   "Please click a course to select it first.")
            return

        course_id   = self.my_tree.item(selected[0])["values"][0]
        course_name = self.my_tree.item(selected[0])["values"][1]

        if not messagebox.askyesno("Confirm Unenroll",
                                   f"Unenroll from '{course_name}'?\n"
                                   "This cannot be undone."):
            return

        with get_connection() as conn:
            conn.execute("""
                DELETE FROM enrollments
                WHERE student_id = ? AND course_id = ?
            """, (self.student_id, course_id))

        messagebox.showinfo("Unenrolled",
                            f"You have been unenrolled from '{course_name}'.")
        self._refresh_my_courses()
        self._refresh_available()
        self._update_count_label()