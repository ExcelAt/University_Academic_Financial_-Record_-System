import streamlit as st
import pandas as pd
from database import get_connection


# =========================================================
# GRADE CALCULATION
# =========================================================
def calculate_grade(final_mark):

    if final_mark >= 75:
        return "A"

    elif final_mark >= 65:
        return "B"

    elif final_mark >= 50:
        return "C"

    else:
        return "F"


# =========================================================
# CAPTURE MARKS
# =========================================================
def capture_marks():

    st.subheader("📝 Capture Student Marks")

    with get_connection() as conn:

        records = conn.execute("""
            SELECT
                e.student_id,
                s.name || ' ' || s.surname AS student_name,
                e.course_id,
                c.course_name
            FROM enrollments e
            JOIN students s
                ON e.student_id = s.student_id
            JOIN courses c
                ON e.course_id = c.course_id
        """).fetchall()

    if not records:
        st.warning("No enrollments found.")
        return

    options = {
        f"{r['student_name']} - {r['course_name']}":
        (r['student_id'], r['course_id'])
        for r in records
    }

    selected = st.selectbox(
        "Select Student & Course",
        list(options.keys())
    )

    student_id, course_id = options[selected]

    assignment1 = st.number_input(
        "Assignment 1",
        0.0, 100.0
    )

    assignment2 = st.number_input(
        "Assignment 2",
        0.0, 100.0
    )

    exam = st.number_input(
        "Exam Mark",
        0.0, 100.0
    )

    # -----------------------------------------------------
    # FINAL MARK CALCULATION
    # -----------------------------------------------------
    final_mark = (
        (assignment1 * 0.2) +
        (assignment2 * 0.3) +
        (exam * 0.5)
    )

    grade = calculate_grade(final_mark)

    st.info(f"Final Mark: {final_mark:.2f}")
    st.info(f"Grade: {grade}")

    # -----------------------------------------------------
    # SAVE BUTTON
    # -----------------------------------------------------
    if st.button("Save Marks"):

        with get_connection() as conn:

            existing = conn.execute("""
                SELECT *
                FROM marks
                WHERE student_id = ?
                AND course_id = ?
            """, (student_id, course_id)).fetchone()

            if existing:

                conn.execute("""
                    UPDATE marks
                    SET assignment1 = ?,
                        assignment2 = ?,
                        exam = ?,
                        final_mark = ?,
                        grade = ?
                    WHERE student_id = ?
                    AND course_id = ?
                """, (
                    assignment1,
                    assignment2,
                    exam,
                    final_mark,
                    grade,
                    student_id,
                    course_id
                ))

            else:

                conn.execute("""
                    INSERT INTO marks (
                        student_id,
                        course_id,
                        assignment1,
                        assignment2,
                        exam,
                        final_mark,
                        grade
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    student_id,
                    course_id,
                    assignment1,
                    assignment2,
                    exam,
                    final_mark,
                    grade
                ))

        st.success("Marks saved successfully!")


# =========================================================
# DISPLAY RESULTS
# =========================================================
def display_results():

    st.subheader("📊 Student Results")

    with get_connection() as conn:

        results = conn.execute("""
            SELECT
                s.student_id,
                s.name || ' ' || s.surname AS student_name,
                c.course_name,
                m.assignment1,
                m.assignment2,
                m.exam,
                m.final_mark,
                m.grade
            FROM marks m
            JOIN students s
                ON m.student_id = s.student_id
            JOIN courses c
                ON m.course_id = c.course_id
        """).fetchall()

    if results:

        df = pd.DataFrame(results)

        st.dataframe(df, use_container_width=True)

    else:
        st.info("No marks captured yet.")