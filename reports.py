import tkinter as tk
from tkinter import messagebox
from database import get_connection


class ReportsTab:
    def __init__(self, notebook):
        self.frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(self.frame, text="Q7 - Reports")

        tk.Label(self.frame, text="Student ID").pack()
        self.entry = tk.Entry(self.frame, width=25)
        self.entry.pack(pady=5)

        tk.Button(
            self.frame,
            text="Generate Academic Report",
            command=self.generate_report
        ).pack(pady=10)

    def generate_report(self):
        sid = self.entry.get().strip()

        with get_connection() as conn:
            rows = conn.execute("""
                SELECT
                    s.name,
                    s.surname,
                    c.course_name,
                    m.final_mark,
                    m.grade
                FROM marks m
                JOIN students s ON s.student_id = m.student_id
                JOIN courses c ON c.course_id = m.course_id
                WHERE m.student_id = ?
            """, (sid,)).fetchall()

        if not rows:
            messagebox.showerror("Error", "No records found.")
            return

        filename = f"report_{sid}.txt"

        total = 0
        count = 0

        with open(filename, "w") as file:
            file.write("APEX UNIVERSITY ACADEMIC REPORT\n")
            file.write("=" * 35 + "\n\n")

            fullname = rows[0]["name"] + " " + rows[0]["surname"]

            file.write(f"Student ID: {sid}\n")
            file.write(f"Name: {fullname}\n\n")

            for r in rows:
                file.write(
                    f"{r['course_name']} | "
                    f"{r['final_mark']:.2f}% | "
                    f"{r['grade']}\n"
                )
                total += r["final_mark"]
                count += 1

            avg = total / count
            file.write(f"\nAverage: {avg:.2f}%\n")

        messagebox.showinfo("Success", f"{filename} saved.")


class WarningTab:
    def __init__(self, notebook):
        self.frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(self.frame, text="Q8 - Warning Letters")

        tk.Label(self.frame, text="Student ID").pack()
        self.entry = tk.Entry(self.frame, width=25)
        self.entry.pack(pady=5)

        tk.Button(
            self.frame,
            text="Generate Warning Letter",
            command=self.generate_warning
        ).pack(pady=10)

    def generate_warning(self):
        sid = self.entry.get().strip()

        with get_connection() as conn:

            avg_row = conn.execute("""
                SELECT AVG(final_mark) AS avg_mark
                FROM marks
                WHERE student_id = ?
            """, (sid,)).fetchone()

            student = conn.execute("""
                SELECT name, surname
                FROM students
                WHERE student_id = ?
            """, (sid,)).fetchone()

        if not student:
            messagebox.showerror("Error", "Student not found.")
            return

        if avg_row["avg_mark"] is None:
            messagebox.showerror("Error", "No marks available.")
            return

        avg = avg_row["avg_mark"]

        if avg >= 50:
            messagebox.showinfo("Status", "Student is not at risk.")
            return

        filename = f"warning_{sid}.txt"

        with open(filename, "w") as file:
            file.write("ACADEMIC WARNING LETTER\n")
            file.write("=" * 30 + "\n\n")
            file.write(f"Dear {student['name']} {student['surname']},\n\n")
            file.write(f"Your average is {avg:.2f}%.\n")
            file.write("This is below the required pass mark.\n")
            file.write("Please consult your academic advisor immediately.\n\n")
            file.write("Regards\nApex University")

        with get_connection() as conn:
            conn.execute("""
                INSERT INTO warning_letters
                (student_id, reason, file_path)
                VALUES (?, ?, ?)
            """, (
                sid,
                "Average below 50%",
                filename
            ))

        messagebox.showwarning("Created", f"{filename} saved.")