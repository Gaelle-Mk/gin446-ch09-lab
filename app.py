"""GIN446 – Chapter 9 lab: server-side validation of the Engineering Student Profile.

Run (inside the activated .venv):   flask --app app run --debug
Then open http://127.0.0.1:5000/
"""
from flask import Flask, jsonify, render_template, request
from validators import validate_profile

app = Flask(__name__)

# labels shown in the form; the keys are the values the server accepts (see validators.py)
CHOICES = {
    "majors": {"computer": "Computer", "communication": "Communication", "electrical": "Electrical",
               "mechanical": "Mechanical", "civil": "Civil", "chemical": "Chemical"},
    "terms": {"spring": "Spring", "summer": "Summer", "fall": "Fall"},
    "skills": {"html": "HTML", "css": "CSS", "javascript": "JavaScript", "python": "Python", "git": "Git"},
    "software": {"vscode": "VS Code", "github": "GitHub", "figma": "Figma", "matlab": "MATLAB", "autocad": "AutoCAD"},
}


@app.route("/")
def home():
    weekly_work = [
        {"week": 4, "title": "Engineering Student Profile (HTML form)", "done": True},
        {"week": 7, "title": "Live Quiz with fetch()", "done": True},
        {"week": 8, "title": "Server-side validation (this lab)", "done": True},
    ]
    return render_template("index.html", weekly_work=weekly_work)


# ---------- the OLD version: no validation at all ----------
@app.route("/profile")
def profile_form():
    return render_template("profile-form.html", **CHOICES)


@app.route("/submit-profile", methods=["POST"])
def submit_profile():
    data = request.form.to_dict()
    data["skills"] = request.form.getlist("skills")
    data["software"] = request.form.getlist("software")
    return render_template("profile.html", data=data, validated=False)


# ---------- the NEW version: validated on the server ----------
@app.route("/profile-validated", methods=["GET", "POST"])
def profile_validated():
    if request.method == "GET":
        return render_template("profile-form-validated.html", errors={}, values={}, **CHOICES)

    # TODO 3 (Task 3):
    #   1. errors, cleaned = validate_profile(request.form)
    #   2. if there are errors: return the SAME template with errors=errors, values=cleaned
    #      and **CHOICES, and the status code 400
    #   3. otherwise: return render_template("profile.html", data=cleaned, validated=True)
    errors, cleaned = validate_profile(request.form)
    if errors:
        return render_template("profile-form-validated.html", errors=errors, values=cleaned, **CHOICES), 400
    return render_template("profile.html", data=cleaned, validated=True)


@app.post("/api/validate")
def api_validate():
    errors, _ = validate_profile(request.form)
    return jsonify(errors), 400 if errors else 200


if __name__ == "__main__":
    app.run(debug=True)
