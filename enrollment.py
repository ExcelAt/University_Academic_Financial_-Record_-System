import streamlit as st
import pandas as pd
from database import get_connection


# =========================================================
# ENROLL STUDENT
# =========================================================
def enroll_student():

    st.subheader("📘 Student Enrollment")

    with get_connection() as conn:

        # -------------------------------------------------
        # LOAD STUDENTS
        # -------------------------------------------------
        students = conn.execute("""
            SELECT student_id, name, surname
            FROM students
        """).fetchall()

        # -------------------------------------------------
        # LOAD COURSES
        # -------------------------------------------------
        courses = conn.execute("""
            SELECT course_id, course_name, course_code
            FROM courses
        """).fetchall()

    # Student dropdown
    student_options = {
        f"{s['student_id']} - {s['name']} {s['surname']}": s['student_id']
        for s in students
    }

    selected_student = st.selectbox(
        "Select Student",
        list(student_options.keys())
    )

    student_id = student_options[selected_student]

    # Course dropdown
    course_options = {
        f"{c['course_code']} - {c['course_name']}": c['course_id']
        for c in courses
    }

    selected_course = st.selectbox(
        "Select Course",
        list(course_options.keys())
    )

    course_id = course_options[selected_course]

    academic_year = st.number_input(
        "Academic Year",
        min_value=2024,
        max_value=2035,
        value=2026
    )

    semester = st.selectbox(
        "Semester",
        ["S1", "S2"]
    )

    # -----------------------------------------------------
    # ENROLL BUTTON
    # -----------------------------------------------------
    if st.button("Enroll Student"):

        with get_connection() as conn:

            # -------------------------------------------------
            # CHECK MAXIMUM 6 COURSES
            # -------------------------------------------------
            row = conn.execute("""
                SELECT COUNT(*) as total
                FROM enrollments
                WHERE student_id = ?
            """, (student_id,)).fetchone()

            if row["total"] >= 6:
                st.error("Student already has 6 courses.")
                return

            # -------------------------------------------------
            # CHECK DUPLICATES
            # -------------------------------------------------
            existing = conn.execute("""
                SELECT *
                FROM enrollments
                WHERE student_id = ?
                AND course_id = ?
                AND academic_year = ?
                AND semester = ?
            """, (
                student_id,
                course_id,
                academic_year,
                semester
            )).fetchone()

            if existing:
                st.warning("Student already enrolled in this course.")
                return

            # -------------------------------------------------
            # INSERT ENROLLMENT
            # -------------------------------------------------
            conn.execute("""
                INSERT INTO enrollments (
                    student_id,
                    course_id,
                    academic_year,
                    semester
                )
                VALUES (?, ?, ?, ?)
            """, (
                student_id,
                course_id,
                academic_year,
                semester
            ))

            st.success("Student enrolled successfully!")


# =========================================================
# DISPLAY ENROLLMENTS
# =========================================================
def display_enrollments():

    st.subheader("📚 Enrollment Records")

    with get_connection() as conn:

        data = conn.execute("""
            SELECT
                s.student_id,
                s.name || ' ' || s.surname AS student_name,
                c.course_code,
                c.course_name,
                e.academic_year,
                e.semester
            FROM enrollments e
            JOIN students s
                ON e.student_id = s.student_id
            JOIN courses c
                ON e.course_id = c.course_id
            ORDER BY student_name
        """).fetchall()

    if data:

        df = pd.DataFrame(data)

        st.dataframe(df, use_container_width=True)

    else:
        st.info("No enrollments found.")