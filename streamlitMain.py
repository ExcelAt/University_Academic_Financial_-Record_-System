# Question 1 & 2 
# Covers login, signup
import streamlit as st
import pandas as pd 
from datetime import datetime
from database import get_connection, init_database
from utils import (hash_password, validate_email,
                   validate_dob, validate_password)
from reports import ReportsTab, WarningTab

# Page setup 
st.set_page_config(
    page_title="Apex University",
    page_icon="",
    layout="wide"
)

#initalizing database connection
init_database()  

#tracking who is logged in
#using sessions to remember the user across pages

defaults ={
    "logged_in":  False,
    "role":       None,
    "student_id": None,
    "name":       None,
    "page":       "login",
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

################################
# Logout Function
################################

def logout():
    # returns to the login screen 
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

################################
# Creating Login Page
################################

def page_login():
    # Centre the login form using columns
    col_l, col_mid, col_r = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("##  Apex University")
        st.markdown("#### Sign in to your account")
        st.divider()

        # Access selection - Student or Admin
        role = st.radio("Login as", ["Student", "Admin"],
                        horizontal=True, key="login_role")

        email    = st.text_input(
            "Email address" if role == "Student" else "Admin email",
            key="login_email")
        password = st.text_input("Password",
                                  type="password", key="login_pw")

        st.markdown("")
        sign_in = st.button("Sign in", use_container_width=True,
                             type="primary")

        # Button to navigate to the sign up page
        st.markdown("")
        if st.button("New student? Create an account",
                     use_container_width=True, key="go_signup"):
            st.session_state.page = "signup"
            st.rerun()

        if sign_in:
            if not email or not password:
                st.error("Please enter your email and password.")
                return
    
            #  Admin login 
            # Admin credentials are hardcoded — not stored in the DB
            if role == "Admin":
                if (email.lower() == "admin@apex.ac.za" and
                        hash_password(password) == hash_password("Admin123")):
                    st.session_state.logged_in  = True
                    st.session_state.role       = "admin"
                    st.session_state.name       = "Administrator"
                    st.session_state.student_id = "ADMIN01"
                    st.rerun()
                else:
                    st.error("Incorrect email or password.")
                return

            #  Student login — search DB by email 
            with get_connection() as conn:
                row = conn.execute(
                    "SELECT * FROM students WHERE LOWER(email) = ?",
                    (email.lower(),)
                ).fetchone()

            if row and row["password"] == hash_password(password):
                st.session_state.logged_in  = True
                st.session_state.role       = "student"
                st.session_state.student_id = row["student_id"]
                st.session_state.name       = (f"{row['name']} "
                                                f"{row['surname']}")
                st.rerun()
            else:
                st.error("Incorrect email or password.")


# #############################################
# PAGE: SIGN UP
# #############################################
def page_signup():
    col_l, col_mid, col_r = st.columns([1, 1.4, 1])
    with col_mid:
        st.markdown("## Create your student account")
        st.caption(
            "Your Student ID will be assigned automatically on submission.")
 
        if st.button("← Back to login"):
            st.session_state.page = "login"
            st.rerun()
 
        st.divider()
 
        with get_connection() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM students").fetchone()[0]
        next_id = f"STU{count + 1:05d}"
        st.info(f"Your Student ID will be: **{next_id}**")
 
        col1, col2 = st.columns(2)
        with col1:
            fname     = st.text_input("First name *")
            dob       = st.text_input("Date of birth * (DD/MM/YYYY)")
            email     = st.text_input("Email address *")
        with col2:
            surname   = st.text_input("Surname *")
            phone     = st.text_input("Phone (optional)")
            password  = st.text_input("Password *", type="password")
            password2 = st.text_input("Confirm password *",
                                       type="password")
 
        st.caption("Password: 8+ characters, 1 uppercase letter, 1 number.")
 
        st.markdown("")
        if st.button("Create Account", type="primary",
                     use_container_width=True):
 
            if not all([fname, surname, dob, email, password, password2]):
                st.error("All fields marked * are required.")
                return
 
            if not fname.replace(" ", "").isalpha():
                st.error("First name must contain letters only.")
                return
 
            if not surname.replace(" ", "").isalpha():
                st.error("Surname must contain letters only.")
                return
 
            dob_ok, dob_val = validate_dob(dob)
            if not dob_ok:
                st.error(dob_val)
                return
 
            if not validate_email(email):
                st.error("Please enter a valid email address.")
                return
 
            pw_ok, pw_err = validate_password(password)
            if not pw_ok:
                st.error(pw_err)
                return
 
            if password != password2:
                st.error("Passwords do not match.")
                return
 
            with get_connection() as conn:
                count = conn.execute(
                    "SELECT COUNT(*) FROM students").fetchone()[0]
                sid = f"STU{count + 1:05d}"
                try:
                    conn.execute("""
                        INSERT INTO students
                            (student_id, name, surname, date_of_birth,
                             email, phone, password)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (sid, fname, surname, dob_val,
                          email.lower(), phone,
                          hash_password(password)))
 
                    st.success(
                        f"Account created successfully!\n\n"
                        f"**Your Student ID is: {sid}**\n\n"
                        f"Please save this ID. "
                        f"You can now log in with your email and password.")
                    st.balloons()
 
                except Exception as e:
                    if "UNIQUE" in str(e):
                        st.error("That email address is already registered.")
                    else:
                        st.error(f"Database error: {e}")
 
 
# #############################################
# ADMIN DASHBOARD
# #############################################
def page_admin():
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("## Apex University — Admin Panel")
        st.caption("Logged in as **Administrator**")
    with col2:
        st.markdown("")
        if st.button("Logout", use_container_width=True):
            logout()
 
    st.divider()
 
    tab_q1, tab_q2 = st.tabs([
        "Q1 — Student Registration",
        "Q2 — Course Management",
    ])
 
    with tab_q1:
        admin_q1_students()
 
    with tab_q2:
        admin_q2_courses()
 
 
# #############################################
# Q1 — STUDENT REGISTRATION - By Admin 
# #############################################
def admin_q1_students():
    st.subheader("Student Registration")
 
    with st.expander("Register New Student", expanded=False):
 
        with get_connection() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM students").fetchone()[0]
        next_id = f"STU{count + 1:05d}"
        st.info(f"Student ID to be assigned: **{next_id}**")
 
        col1, col2 = st.columns(2)
        with col1:
            fname   = st.text_input("First name *",                key="a_fname")
            dob     = st.text_input("Date of birth * (DD/MM/YYYY)", key="a_dob")
            email   = st.text_input("Email *",                     key="a_email")
            qual    = st.text_input("Qualification",               key="a_qual")
            year    = st.selectbox("Year of study", [1, 2, 3, 4], key="a_year")
        with col2:
            surname  = st.text_input("Surname *",                  key="a_surname")
            phone    = st.text_input("Phone",                      key="a_phone")
            gender   = st.selectbox("Gender",
                                    ["", "Male", "Female",
                                     "Other", "Prefer not to say"],
                                    key="a_gender")
            password  = st.text_input("Password *",
                                       type="password",            key="a_pw")
            password2 = st.text_input("Confirm password *",
                                       type="password",            key="a_pw2")
 
        st.caption("Password: 8+ characters, 1 uppercase letter, 1 number.")
 
        if st.button("Register Student", type="primary", key="a_reg_btn"):
            if not all([fname, surname, dob, email, password, password2]):
                st.error("All fields marked * are required.")
            elif not fname.replace(" ", "").isalpha():
                st.error("First name must contain letters only.")
            elif not surname.replace(" ", "").isalpha():
                st.error("Surname must contain letters only.")
            else:
                dob_ok, dob_val = validate_dob(dob)
                if not dob_ok:
                    st.error(dob_val)
                elif not validate_email(email):
                    st.error("Please enter a valid email address.")
                else:
                    pw_ok, pw_err = validate_password(password)
                    if not pw_ok:
                        st.error(pw_err)
                    elif password != password2:
                        st.error("Passwords do not match.")
                    else:
                        with get_connection() as conn:
                            count = conn.execute(
                                "SELECT COUNT(*) FROM students"
                            ).fetchone()[0]
                            sid = f"STU{count + 1:05d}"
                            try:
                                conn.execute("""
                                    INSERT INTO students
                                        (student_id, name, surname,
                                         date_of_birth, gender, email,
                                         phone, password, qualification,
                                         year_of_study)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (sid, fname, surname, dob_val,
                                      gender, email.lower(), phone,
                                      hash_password(password), qual, year))
                                st.success(
                                    f"Student registered! "
                                    f"ID: **{sid}** | "
                                    f"Name: {fname} {surname}")
                            except Exception as e:
                                if "UNIQUE" in str(e):
                                    st.error(
                                        "That email is already registered.")
                                else:
                                    st.error(str(e))
 
    st.divider()
 
    st.subheader("All Students")
 
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("Search by ID, name or email",
                                key="q1_search")
    with col2:
        st.markdown("")
        st.caption(f"Total: **{_count_students()}** students")
 
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT student_id, name, surname, date_of_birth,
                   gender, email, phone, qualification,
                   year_of_study, registered_on
            FROM students
            ORDER BY student_id
        """).fetchall()
 
    df = pd.DataFrame([dict(r) for r in rows])
 
    if df.empty:
        st.info("No students registered yet.")
        return
 
    df.columns = ["Student ID", "First Name", "Surname", "Date of Birth",
                  "Gender", "Email", "Phone", "Qualification",
                  "Year", "Registered On"]
    df["Registered On"] = df["Registered On"].str[:10]
 
    if search:
        mask = (
            df["Student ID"].str.contains(search, case=False, na=False) |
            df["First Name"].str.contains(search, case=False, na=False) |
            df["Surname"].str.contains(search, case=False, na=False) |
            df["Email"].str.contains(search, case=False, na=False)
        )
        df = df[mask]
 
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"{len(df)} result(s) shown")
 
    with st.expander("Delete a Student", expanded=False):
        st.warning("Deleting a student also removes their enrollments "
                   "and marks. This cannot be undone.")
 
        with get_connection() as conn:
            all_students = conn.execute(
                "SELECT student_id, name, surname FROM students "
                "ORDER BY student_id"
            ).fetchall()
 
        if not all_students:
            st.info("No students to delete.")
        else:
            del_options = {
                f"{s['student_id']} — {s['name']} {s['surname']}":
                s["student_id"]
                for s in all_students
            }
            del_select = st.selectbox("Select student to delete",
                                       list(del_options.keys()),
                                       key="del_stu")
            if st.button("Delete Student", type="primary",
                         key="del_stu_btn"):
                sid = del_options[del_select]
                with get_connection() as conn:
                    conn.execute(
                        "DELETE FROM students WHERE student_id = ?",
                        (sid,))
                st.success(f"Student {sid} deleted.")
                st.rerun()
 
 
# #############################################
# Q2 — COURSE MANAGEMENT - by admin
# #############################################
def admin_q2_courses():
    st.subheader("Course Management")
 
    with st.expander("Add New Course", expanded=False):
 
        with get_connection() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM courses").fetchone()[0]
        next_id = f"CRS{count + 1:03d}"
        st.info(f"Course ID to be assigned: **{next_id}**")
 
        col1, col2 = st.columns(2)
        with col1:
            cname    = st.text_input("Course name *",              key="c_name")
            ccode    = st.text_input("Course code * (e.g. CMPN201)", key="c_code")
            fee      = st.number_input("Course fee (R) *",
                                        min_value=0.0,
                                        step=100.0,                key="c_fee")
        with col2:
            duration = st.text_input("Duration * (e.g. 6 Months)", key="c_dur")
            semester = st.selectbox("Semester",
                                    ["S1", "S2", "Year"],          key="c_sem")
            credits  = st.number_input("Credits",
                                        min_value=1, max_value=30,
                                        value=12,                  key="c_cred")
        lecturer = st.text_input("Lecturer (optional)",            key="c_lec")
 
        if st.button("Add Course", type="primary", key="add_course_btn"):
            if not all([cname, ccode, duration]) or fee <= 0:
                st.error(
                    "Course name, code, fee and duration are required.")
            elif not ccode.replace(" ", "").isalnum():
                st.error(
                    "Course code must be letters and numbers only "
                    "(e.g. CMPN201).")
            else:
                with get_connection() as conn:
                    count = conn.execute(
                        "SELECT COUNT(*) FROM courses").fetchone()[0]
                    cid = f"CRS{count + 1:03d}"
                    try:
                        conn.execute("""
                            INSERT INTO courses
                                (course_id, course_name, course_code,
                                 duration, credits, semester,
                                 fee, lecturer)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (cid, cname, ccode.upper(), duration,
                              credits, semester, fee,
                              lecturer or "TBA"))
                        st.success(
                            f"Course added! "
                            f"ID: **{cid}** | {cname}")
                    except Exception as e:
                        if "UNIQUE" in str(e):
                            st.error(
                                f"Course code '{ccode.upper()}' "
                                "is already in use.")
                        else:
                            st.error(str(e))
 
    st.divider()
 
    st.subheader("Course Catalogue")
 
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("Search by ID, name or code",
                                key="q2_search")
    with col2:
        st.markdown("")
        st.caption(f"Total: **{_count_courses()}** courses")
 
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT course_id, course_name, course_code,
                   fee, duration, credits, semester, lecturer
            FROM courses ORDER BY course_id
        """).fetchall()
 
    df = pd.DataFrame([dict(r) for r in rows])
 
    if df.empty:
        st.info("No courses added yet.")
        return
 
    df.columns = ["Course ID", "Course Name", "Code", "Fee (R)",
                  "Duration", "Credits", "Semester", "Lecturer"]
    df["Fee (R)"] = df["Fee (R)"].apply(lambda x: f"R {x:,.2f}")
 
    if search:
        mask = (
            df["Course ID"].str.contains(search, case=False, na=False) |
            df["Course Name"].str.contains(search, case=False, na=False) |
            df["Code"].str.contains(search, case=False, na=False)
        )
        df = df[mask]
 
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"{len(df)} result(s) shown")
 
    with st.expander("Delete a Course", expanded=False):
        st.warning("Deleting a course also removes all related "
                   "enrollments and marks. This cannot be undone.")
 
        with get_connection() as conn:
            all_courses = conn.execute(
                "SELECT course_id, course_name FROM courses "
                "ORDER BY course_id"
            ).fetchall()
 
        if not all_courses:
            st.info("No courses to delete.")
        else:
            del_options = {
                f"{c['course_id']} — {c['course_name']}": c["course_id"]
                for c in all_courses
            }
            del_select = st.selectbox("Select course to delete",
                                       list(del_options.keys()),
                                       key="del_crs")
            if st.button("Delete Course", type="primary",
                         key="del_crs_btn"):
                cid = del_options[del_select]
                with get_connection() as conn:
                    conn.execute(
                        "DELETE FROM courses WHERE course_id = ?",
                        (cid,))
                st.success(f"Course {cid} deleted.")
                st.rerun()
 
 
# #############################################
# STUDENT PORTAL
# #############################################
def page_student():
    sid  = st.session_state.student_id
    name = st.session_state.name
 
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("## 🎓 Apex University — Student Portal")
        st.markdown(f"Welcome, **{name}** | `{sid}`")
    with col2:
        st.markdown("")
        if st.button("Logout", use_container_width=True):
            logout()
 
    st.divider()
 
    # Student sees only their profile — enrollment handled separately
    student_profile(sid)
 
 
# ─────────────────────────────────────────────────────────
# STUDENT — Their Profile
# ─────────────────────────────────────────────────────────
def student_profile(sid):
    st.subheader("My Profile")
 
    with get_connection() as conn:
        s = conn.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (sid,)
        ).fetchone()
 
    if not s:
        st.error("Student record not found.")
        return
 
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Student ID",    s["student_id"])
        st.metric("First Name",    s["name"])
        st.metric("Date of Birth", s["date_of_birth"] or "—")
        st.metric("Phone",         s["phone"] or "—")
        st.metric("Qualification", s["qualification"] or "—")
    with col2:
        st.metric("Surname",       s["surname"])
        st.metric("Email",         s["email"])
        st.metric("Gender",        s["gender"] or "—")
        st.metric("Year of Study", f"Year {s['year_of_study']}")
        st.metric("Registered On", (s["registered_on"] or "")[:10])
 
 
# #############################################
# UTILITY HELPERS
# #############################################
def _count_students():
    with get_connection() as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM students").fetchone()[0]
 
 
def _count_courses():
    with get_connection() as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM courses").fetchone()[0]
 
 
# #############################################
# MAIN ROUTER
# ############################################# 
if not st.session_state.logged_in:
    if st.session_state.page == "signup":
        page_signup()
    else:
        page_login()
elif st.session_state.role == "admin":
    page_admin()
else:
    page_student()


 