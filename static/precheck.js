// Optional comfort: check a few fields in the browser BEFORE sending.
// The rules MIRROR validators.py, but the server still checks everything.
const RULES = {
  student_id: { test: (v) => /^\d{9}$/.test(v), msg: "Student ID must be exactly 9 digits." },
  // TODO (at home, Part B): add email, phone, gpa and team_size with the SAME rules
  // and messages as validators.py (JavaScript regex syntax is almost identical).
  email: {
    test: (v) => /^[a-z0-9._%+-]+@usek\.edu\.lb$/.test(v.toLowerCase()),
    msg: "Use your university e-mail (…@usek.edu.lb).",
  },
  phone: {
    test: (v) => /^\+961 ?\d{1,2} ?\d{3} ?\d{3}$/.test(v),
    msg: "Phone must be a Lebanese number, e.g. +961 3 123 456.",
  },
  gpa: {
    test: (v) => /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(v) &&
      Number(v) >= 40 && Number(v) <= 100,
    msg: "GPA must be a number between 40 and 100.",
  },
  team_size: {
    test: (v) => /^[+-]?\d+$/.test(v) && Number(v) >= 1 && Number(v) <= 4,
    msg: "Team size must be 1, 2, 3 or 4.",
  },
};

const form = document.querySelector("form.profile");
const summary = document.querySelector(".summary");
const summaryList = summary.querySelector("ul");
const fields = Array.from(form.querySelectorAll("[data-field]"));
let revision = 0;
let checking = false;

function showError(field, message) {
  let span = field.querySelector(".error");
  if (message && !span) {
    span = document.createElement("span");
    span.className = "error";
    field.append(span);
  }
  if (message) span.textContent = message;
  else if (span) span.remove();
  field.classList.toggle("invalid", Boolean(message));
}

function updateSummary() {
  summaryList.replaceChildren();
  for (const field of fields) {
    const error = field.querySelector(".error");
    if (!error) continue;
    const item = document.createElement("li");
    const link = document.createElement("a");
    link.href = "#" + field.dataset.field;
    link.textContent = error.textContent;
    item.append(link);
    summaryList.append(item);
  }
  const count = summaryList.children.length;
  summary.querySelector("strong").textContent = `${count} problem(s) found.`;
  summary.hidden = count === 0;
}

function checkInput(input, rule) {
  const value = input.value.trim();
  let message = "";
  if (input.validity.badInput) message = rule.msg;
  else if (!value && input.required) message = "This field is required.";
  else if (value && !rule.test(value)) message = rule.msg;
  showError(input.closest("[data-field]"), message);
  return message;
}

form.noValidate = true;   // this script replaces the browser bubbles with the SAME messages as the server
const serverOnly = new URLSearchParams(location.search).has("nocheck");   // ?nocheck=1 tests the server alone

form.addEventListener("input", (event) => {
  if (serverOnly) return;
  revision += 1;
  const input = event.target;
  if (!Object.hasOwn(RULES, input.name)) return;
  checkInput(input, RULES[input.name]);
  updateSummary();
});

form.addEventListener("submit", async (event) => {
  if (serverOnly) return;
  event.preventDefault();
  if (checking) return;

  let firstBad = null;
  for (const [name, rule] of Object.entries(RULES)) {
    const input = form.elements[name];
    if (checkInput(input, rule) && !firstBad) firstBad = input;
  }
  updateSummary();
  if (firstBad) { firstBad.focus(); return; }   // stay on the page

  checking = true;
  const submittedRevision = revision;
  try {
    const response = await fetch("/api/validate", { method: "POST", body: new FormData(form) });
    if (response.status !== 200 && response.status !== 400) throw new Error("Validation request failed");
    const errors = await response.json();
    if (submittedRevision !== revision) return;
    if (response.ok) {
      form.submit();
      return;
    }
    for (const field of fields) showError(field, errors[field.dataset.field] || "");
    updateSummary();
    form.querySelector(".invalid input, .invalid select, .invalid textarea")?.focus();
  } catch {
    if (submittedRevision === revision) form.submit();
  } finally {
    checking = false;
  }
});
