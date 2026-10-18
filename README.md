# Job Application Tracker

#### Video Demo: https://youtu.be/X0p89euodEk

#### Description:

Job Application Tracker is a web application that helps job seekers keep track of every job they apply to, see which applications need a follow-up, and understand how their search is going through simple statistics. I built it with Python, Flask, SQLite, HTML, CSS, and Bootstrap.

I built this project because I am actively searching for remote data analyst and business analyst roles. Keeping track of applications in my head or in scattered notes made it easy to forget which companies I had applied to and when I should follow up. I already had an automated tool that finds job postings, so I wanted something that handles what comes after: tracking each application through to an answer.

## Features

- **Home page:** lists every application, newest first, with a coloured badge for its status. If an application has a job link, the company name links to the posting.
- **Add:** a form to record a new application with company, role, link, location, date applied, status, and notes.
- **Edit and delete:** any application can be updated, for example when it moves from Applied to Interview, or deleted.
- **Follow-ups:** shows applications that are still at "Applied" with no update for 7 or more days, along with how many days they have been waiting. A "Followed up" button resets the 7-day clock after I send a follow-up message.
- **Stats:** shows the total number of applications, the response rate, the interview rate, and a count for each status.
- **Export to CSV:** downloads every application as a CSV file that can be opened in Excel or loaded into Power BI for deeper analysis.

## Files

**app.py** is the main Flask application. It connects to the database and defines every route. The `/` route shows all applications. The `/add` and `/edit/<id>` routes show forms and save data with INSERT and UPDATE queries, after checking that the required fields are filled in and that the status is one of the allowed values. The `/delete/<id>` route removes an application. The `/followups` route uses SQLite date functions to find applications not updated in at least 7 days and to calculate how many days each has been waiting. The `/followed_up/<id>` route resets an application's last-updated time. The `/stats` route counts applications by status with GROUP BY and calculates the rates. The `/export` route builds a CSV file in memory with Python's csv module and sends it as a download. A small helper function, `form_value`, reads form fields and strips extra spaces so that stray spaces are not saved.

**schema.sql** creates the SQLite database, tracker.db. It has one table, `applications`, with columns for id, company, role, link, location, date applied, status, notes, and last updated. The status column defaults to "Applied" and the last-updated column defaults to the current time.

**templates/layout.html** is the shared page layout. It loads Bootstrap, shows the navigation bar, highlights the current page, and displays success messages after actions like adding or deleting an application.

**templates/index.html** shows the table of applications and the Export CSV button, or a friendly message with an "Add" button when there are no applications yet.

**templates/add.html** and **templates/edit.html** contain the forms for adding and editing applications. The edit form opens pre-filled with the current details and includes a delete button that asks for confirmation first.

**templates/followups.html** lists applications that need a follow-up, or shows an "all caught up" message.

**templates/stats.html** shows the statistics using Bootstrap cards and a table.

**static/styles.css** holds a few custom styles, such as the size of the numbers on the Stats page and the width of the forms.

## Design Choices

**One table instead of several.** Each application is a single record, so one table keeps the queries simple. I considered a separate table for status history, but for this version I only needed the current status and when it last changed.

**A fixed list of statuses.** The statuses are stored in one Python list, which is used both to build the dropdown and to check submitted data. This keeps the data consistent, so the Stats page can count reliably, and it means a user cannot submit an invalid status by changing the form.

**Seven days for follow-ups.** One week felt like a fair amount of time to give a company before politely checking in, without seeming impatient. I only include applications at "Applied", because there is no need to follow up on offers or rejections.

**Updating last_updated on changes.** Every edit and every "Followed up" click sets the last-updated time to now. This is what makes the Follow-ups page work, since it measures how long it has been since anything happened with each application.

**Response rate and interview rate.** I defined the response rate as the share of applications that received any reply (Interview, Offer, or Rejected), and the interview rate as the share that reached Interview or Offer. These are the two numbers I most wanted to know about my own search.

**CSV export.** As someone working toward a data analyst role, I wanted my data to be easy to analyse outside the app. CSV opens directly in Excel and can be imported into Power BI.

**Flask.** I chose Flask because I learned it in CS50's Week 9 and it let me combine Python, SQL, and HTML in one project.
## How to Run

1. Install Flask: `pip install -r requirements.txt`
2. Create the database: `sqlite3 tracker.db < schema.sql`
3. Start the app: `flask run`
4. Open the link shown in the terminal (usually http://127.0.0.1:5000)


## Future Improvements

In the future, I would like to add user accounts so several people can use the tracker, keep a full history of status changes for each application, and connect it to my job finder so new postings can be saved directly.

## Acknowledgements
Some of the code and this README were written with help from Claude (Anthropic), as permitted by CS50's final project guidelines. I designed the project, decided on the features, tested it, and reviewed and adapted all of the code.
