import re
import hashlib
from datetime import datetime

# password hashing for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# password validation for students registration 
def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number."
    return True, None

# email validation 
def validate_email(email):
    return re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email) is not None

# date of birth validation for students registration
def validate_dob(dob_str):
    try:
        dob = datetime.strptime(dob_str.strip(), "%d/%m/%Y")
    except ValueError:
        return False, "Date of birth must be in DD/MM/YYYY format."
    today = datetime.today()
    age = (today - dob).days // 365
    if dob > today:
        return False, "Date of birth cannot be in the future."
    if age < 15:
        return False, "Student must be at least 15 years old."
    if age > 100:
        return False, "Please enter a valid date of birth."
    return True, dob_str.strip()


# fee validation for courses creation
def validate_fee(fee_str):
    try:
        fee = float(fee_str.strip())
    except ValueError:
        return False, "Course fee must be a number (e.g. 5000 or 4999.99)."
    if fee <= 0:
        return False, "Course fee must be greater than zero."
    return True, round(fee, 2)

#course duration validation 
def validate_duration(duration_str):
    val = duration_str.strip()
    if not val:
        return False, "Course duration is required (e.g. 6 Months, 1 Year)."
    return True, val