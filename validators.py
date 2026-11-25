"""Server-side validation of the Engineering Student Profile form (GIN446 – Chapter 9 lab).

validate_profile(form) receives request.form and returns (errors, cleaned):
  errors  – dict  {field_name: "message"}   (empty dict = the form is valid)
  cleaned – dict  {field_name: clean value} (stripped, converted, normalised)
"""
import re
from datetime import date, datetime

# ---------- 1. Patterns (regular expressions) ----------
STUDENT_ID_RE = re.compile(r"^[0-9]{9}$")                          # exactly 9 digits
NAME_RE = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]{3,60}$")                 # letters, space, ' and -
EMAIL_RE = re.compile(r"^[a-z0-9._%+-]+@usek\.edu\.lb$")         # university e-mail only
PHONE_RE = re.compile(r"^\+961 ?[0-9]{1,2} ?[0-9]{3} ?[0-9]{3}$")         # +961 3 123 456 / +96171123456
COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")                      # #336699
TIME_RE = re.compile(r"^[0-9]{2}:[0-9]{2}$")                           # 14:30

# ---------- 2. Allow-lists ----------
MAJORS = {"computer", "communication", "electrical", "mechanical", "civil", "chemical"}
GRADUATION_TERMS = {"spring", "summer", "fall"}
SKILLS = {"html", "css", "javascript", "python", "git"}
SOFTWARE = {"vscode", "github", "figma", "matlab", "autocad"}

REQUIRED = ["student_id", "fullname", "email", "major", "gpa", "credits",
            "graduation", "project_title", "team_size", "confirmation"]

MAX_TITLE = 120
MAX_DESCRIPTION = 1000


# ---------- 3. Helpers ----------
def to_number(text):
    """'85.5' -> 85.5 ; 'abc' or '' -> None"""
    try:
        if not re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", text):
            return None
        return float(text)
    except (TypeError, ValueError):
        return None


def to_int(text):
    """'12' -> 12 ; '12.5', 'abc' or '' -> None"""
    try:
        return int(text) if re.fullmatch(r"[+-]?[0-9]+", text) else None
    except (TypeError, ValueError):
        return None


def parse_date(text):
    """'2004-05-17' -> date(2004, 5, 17) ; anything else -> None"""
    try:
        parsed = datetime.strptime(text, "%Y-%m-%d").date()
        return parsed if parsed.isoformat() == text else None
    except (TypeError, ValueError):
        return None


def age_on(birth, today):
    """Age in full years on the given day."""
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


# ---------- 4. The validator ----------
def validate_profile(form, today=None):
    today = today or date.today()
    errors, cleaned = {}, {}

    def text(name):
        return (form.get(name) or "").strip()

    # 4.1 required fields
    for name in REQUIRED:
        if not text(name):
            errors[name] = "This field is required."

    # 4.2 student ID  (done for you as an example)
    student_id = text("student_id")
    if student_id and not STUDENT_ID_RE.match(student_id):
        errors["student_id"] = "Student ID must be exactly 9 digits."
    cleaned["student_id"] = student_id

    # ===== IN CLASS (Task 4) =====
    # TODO 4.3 full name: collapse the inner spaces (" ".join(text("fullname").split())),
    #          then check NAME_RE -> "Name: 3 to 60 letters, spaces, ' or - only."
    # TODO 4.4 e-mail: text("email").lower(), then check EMAIL_RE
    #          -> "Use your university e-mail (…@usek.edu.lb)."
    # TODO 4.7 major: must be in MAJORS -> "Choose a major from the list."
    # TODO 4.8 GPA: gpa = to_number(...); a number between 40 and 100
    #          -> "GPA must be a number between 40 and 100."
    #          store the float in cleaned["gpa"]
    # Pattern for every field (copy the student ID block above):
    #     value = text("name")
    #     if value and <not valid>:
    #         errors["name"] = "message"
    #     cleaned["name"] = value

    fullname = " ".join(text("fullname").split())
    if fullname and not NAME_RE.fullmatch(fullname):
        errors["fullname"] = "Name: 3 to 60 letters, spaces, ' or - only."
    cleaned["fullname"] = fullname

    email = text("email").lower()
    if email and not EMAIL_RE.fullmatch(email):
        errors["email"] = "Use your university e-mail (…@usek.edu.lb)."
    cleaned["email"] = email

    major = text("major")
    if major and major not in MAJORS:
        errors["major"] = "Choose a major from the list."
    cleaned["major"] = major

    gpa_text = text("gpa")
    gpa = to_number(gpa_text)
    if gpa_text and (gpa is None or not 40 <= gpa <= 100):
        errors["gpa"] = "GPA must be a number between 40 and 100."
    cleaned["gpa"] = gpa_text if "gpa" in errors else gpa

    # ===== AT HOME (groups) – see the lab guide, Part B =====
    # TODO 4.5  phone (optional)        PHONE_RE
    # TODO 4.6  birthdate (optional)    parse_date(), not in the future, age_on() between 15 and 100
    # TODO 4.9  credits                 to_int(), 0 to 148
    # TODO 4.10 graduation              in GRADUATION_TERMS
    # TODO 4.11 skills / software       form.getlist(name); every value in SKILLS / SOFTWARE
    # TODO 4.12 project_title <= MAX_TITLE characters, description <= MAX_DESCRIPTION
    # TODO 4.13 team_size               to_int(), 1 to 4
    # TODO 4.14 project_color           default "#336699", COLOR_RE, store in lower case
    # TODO 4.15 meeting_time (optional) TIME_RE, minutes < 60, between "08:00" and "18:00"
    # TODO 4.16 confirmation            cleaned["confirmation"] = (text("confirmation") == "yes")

    phone = text("phone")
    if phone and not PHONE_RE.fullmatch(phone):
        errors["phone"] = "Phone must be a Lebanese number, e.g. +961 3 123 456."
    cleaned["phone"] = phone

    birthdate = text("birthdate")
    if birthdate:
        birth = parse_date(birthdate)
        if birth is None:
            errors["birthdate"] = "Birth date must be a valid date (YYYY-MM-DD)."
        elif birth > today:
            errors["birthdate"] = "Birth date cannot be in the future."
        elif not 15 <= age_on(birth, today) <= 100:
            errors["birthdate"] = "Age must be between 15 and 100."
    cleaned["birthdate"] = birthdate

    credits_text = text("credits")
    credits = to_int(credits_text)
    if credits_text and (credits is None or not 0 <= credits <= 148):
        errors["credits"] = "Credits must be a whole number between 0 and 148."
    cleaned["credits"] = credits_text if "credits" in errors else credits

    graduation = text("graduation")
    if graduation and graduation not in GRADUATION_TERMS:
        errors["graduation"] = "Choose spring, summer or fall."
    cleaned["graduation"] = graduation

    for name, allowed in (("skills", SKILLS), ("software", SOFTWARE)):
        selected = form.getlist(name)
        if any(value not in allowed for value in selected):
            errors[name] = "Unknown value selected."
        cleaned[name] = selected

    project_title = text("project_title")
    if len(project_title) > MAX_TITLE:
        errors["project_title"] = "Title: at most 120 characters."
    cleaned["project_title"] = project_title

    description = text("description")
    if len(description) > MAX_DESCRIPTION:
        errors["description"] = "Description: at most 1000 characters."
    cleaned["description"] = description

    team_size_text = text("team_size")
    team_size = to_int(team_size_text)
    if team_size_text and (team_size is None or not 1 <= team_size <= 4):
        errors["team_size"] = "Team size must be 1, 2, 3 or 4."
    cleaned["team_size"] = team_size_text if "team_size" in errors else team_size

    project_color = text("project_color").lower() or "#336699"
    if not COLOR_RE.fullmatch(project_color):
        errors["project_color"] = "Colour must look like #336699."
    cleaned["project_color"] = project_color

    meeting_time = text("meeting_time")
    if meeting_time and (
        not TIME_RE.fullmatch(meeting_time)
        or int(meeting_time[3:]) >= 60
        or not "08:00" <= meeting_time <= "18:00"
    ):
        errors["meeting_time"] = "Meeting time must be between 08:00 and 18:00."
    cleaned["meeting_time"] = meeting_time

    confirmation = text("confirmation")
    if confirmation and confirmation != "yes":
        errors["confirmation"] = "Please confirm that this information is correct."
    cleaned["confirmation"] = confirmation == "yes"

    # keep the raw text of any field not cleaned above, so the form can be refilled
    for name in form:
        if name not in cleaned:
            cleaned[name] = form.getlist(name) if name in ("skills", "software") else text(name)

    return errors, cleaned
