# Job Application Tracker - CS50x Final Project
# Some code in this project was written with help from Claude (Anthropic).

import csv
import io

from cs50 import SQL
from flask import Flask, Response, flash, redirect, render_template, request

# Configure application
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Secret key is needed for flash messages
app.config["SECRET_KEY"] = "change-this-to-something-random"

# Connect to the database
db = SQL("sqlite:///tracker.db")

# The allowed statuses for an application
STATUSES = ["Applied", "Interview", "Offer", "Rejected"]

# Bootstrap colour for each status badge
STATUS_COLORS = {
    "Applied": "secondary",
    "Interview": "primary",
    "Offer": "success",
    "Rejected": "danger"
}


@app.context_processor
def inject_status_colors():
    """Make STATUS_COLORS available in every template"""
    return {"status_colors": STATUS_COLORS}


def form_value(name):
    """Get a form field with extra spaces removed (empty string if missing)"""
    return (request.form.get(name) or "").strip()


@app.route("/")
def index():
    """Show all applications, newest first"""
    applications = db.execute("SELECT * FROM applications ORDER BY date_applied DESC")
    return render_template("index.html", applications=applications)


@app.route("/add", methods=["GET", "POST"])
def add():
    """Add a new application"""
    if request.method == "POST":
        company = form_value("company")
        role = form_value("role")
        link = form_value("link")
        location = form_value("location")
        date_applied = form_value("date_applied")
        status = form_value("status")
        notes = form_value("notes")

        # Check the required fields
        if not company or not role or not date_applied:
            return render_template("add.html", statuses=STATUSES, error="Company, role, and date applied are required.")
        if status not in STATUSES:
            return render_template("add.html", statuses=STATUSES, error="Please choose a valid status.")

        # Save the new application
        db.execute(
            "INSERT INTO applications (company, role, link, location, date_applied, status, notes) VALUES(?, ?, ?, ?, ?, ?, ?)",
            company, role, link, location, date_applied, status, notes
        )
        flash(f"Added {company}.")
        return redirect("/")

    else:
        return render_template("add.html", statuses=STATUSES)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    """Edit an existing application"""
    rows = db.execute("SELECT * FROM applications WHERE id = ?", id)
    if not rows:
        return redirect("/")
    application = rows[0]

    if request.method == "POST":
        company = form_value("company")
        role = form_value("role")
        link = form_value("link")
        location = form_value("location")
        date_applied = form_value("date_applied")
        status = form_value("status")
        notes = form_value("notes")

        # Check the required fields
        if not company or not role or not date_applied:
            return render_template("edit.html", application=application, statuses=STATUSES, error="Company, role, and date applied are required.")
        if status not in STATUSES:
            return render_template("edit.html", application=application, statuses=STATUSES, error="Please choose a valid status.")

        # Save the changes and record when it was updated
        db.execute(
            "UPDATE applications SET company = ?, role = ?, link = ?, location = ?, date_applied = ?, status = ?, notes = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?",
            company, role, link, location, date_applied, status, notes, id
        )
        flash(f"Updated {company}.")
        return redirect("/")

    else:
        return render_template("edit.html", application=application, statuses=STATUSES)


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    """Delete an application"""
    db.execute("DELETE FROM applications WHERE id = ?", id)
    flash("Application deleted.")
    return redirect("/")


@app.route("/followups")
def followups():
    """Show applications still waiting on a reply after 7+ days"""
    applications = db.execute(
        """SELECT *, CAST(julianday('now') - julianday(last_updated) AS INTEGER) AS days_waiting
           FROM applications
           WHERE status = 'Applied' AND last_updated <= datetime('now', '-7 days')
           ORDER BY last_updated"""
    )
    return render_template("followups.html", applications=applications)


@app.route("/followed_up/<int:id>", methods=["POST"])
def followed_up(id):
    """Mark an application as followed up, restarting the 7-day clock"""
    db.execute("UPDATE applications SET last_updated = CURRENT_TIMESTAMP WHERE id = ?", id)
    flash("Marked as followed up. It will reappear here in 7 days if there's still no reply.")
    return redirect("/followups")


@app.route("/stats")
def stats():
    """Show summary numbers for the job search"""
    # Count applications per status
    rows = db.execute("SELECT status, COUNT(*) AS count FROM applications GROUP BY status")

    # Start every status at 0, then fill in the real counts
    counts = {status: 0 for status in STATUSES}
    for row in rows:
        counts[row["status"]] = row["count"]

    total = sum(counts.values())

    # Response rate: got any reply (anything other than still "Applied")
    # Interview rate: reached the interview stage or further
    if total > 0:
        response_rate = round((total - counts["Applied"]) / total * 100, 1)
        interview_rate = round((counts["Interview"] + counts["Offer"]) / total * 100, 1)
    else:
        response_rate = 0
        interview_rate = 0

    return render_template(
        "stats.html",
        total=total,
        counts=counts,
        response_rate=response_rate,
        interview_rate=interview_rate
    )


@app.route("/export")
def export():
    """Download all applications as a CSV file"""
    applications = db.execute("SELECT * FROM applications ORDER BY date_applied DESC")

    # Build the CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow(["Company", "Role", "Link", "Location", "Date Applied", "Status", "Notes", "Last Updated"])

    # One row per application
    for app_row in applications:
        writer.writerow([
            app_row["company"],
            app_row["role"],
            app_row["link"],
            app_row["location"],
            app_row["date_applied"],
            app_row["status"],
            app_row["notes"],
            app_row["last_updated"]
        ])

    # Send it to the browser as a file download
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=applications.csv"}
    )
