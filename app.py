from flask import Flask, request, redirect, render_template_string
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB = Path(__file__).with_name("campus.db")
def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS complaints(
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, category TEXT NOT NULL,
        location TEXT NOT NULL, priority TEXT NOT NULL, description TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'New', created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

HTML = """
<!doctype html><html><head><title>Campus Helpdesk</title><style>
body{font:16px Arial;background:#f4f6fa;max-width:950px;margin:30px auto;padding:0 15px;color:#20283a}
section{background:white;padding:18px;border-radius:12px;margin:14px 0}
input,select,textarea,button{padding:10px;margin:5px;border:1px solid #ccd2df;border-radius:6px}
button{background:#2457d6;color:white;border:0}table{width:100%;border-collapse:collapse}
td,th{padding:10px;border-bottom:1px solid #e5e8ef;text-align:left}
</style></head><body><h1>Smart Campus Helpdesk</h1>
<section><h2>Report an issue</h2><form method="post" action="/new">
<input name="title" placeholder="Issue title" required>
<select name="category">{% for x in ['Infrastructure','IT Support','Cleanliness','Safety','Other'] %}<option>{{x}}</option>{% endfor %}</select>
<input name="location" placeholder="Building / location" required>
<select name="priority"><option>Low</option><option selected>Medium</option><option>High</option></select>
<textarea name="description" placeholder="Describe the issue" required></textarea><button>Submit complaint</button></form></section>
<section><h2>Reported issues ({{items|length}})</h2><table><tr><th>Issue</th><th>Category</th><th>Location</th><th>Priority</th><th>Status</th><th>Update</th></tr>
{% for x in items %}<tr><td>{{x.title}}<br><small>{{x.description}}</small></td><td>{{x.category}}</td><td>{{x.location}}</td><td>{{x.priority}}</td><td>{{x.status}}</td>
<td><form method="post" action="/update/{{x.id}}"><select name="status" onchange="this.form.submit()">{% for s in ['New','In Progress','Resolved'] %}<option {% if x.status==s %}selected{% endif %}>{{s}}</option>{% endfor %}</select></form></td></tr>{% endfor %}
</table></section></body></html>
"""
@app.get("/")
def home():
    with db() as c: items=c.execute("SELECT * FROM complaints ORDER BY id DESC").fetchall()
    return render_template_string(HTML,items=items)
@app.post("/new")
def new():
    f=request.form
    with db() as c:
        c.execute("INSERT INTO complaints(title,category,location,priority,description) VALUES(?,?,?,?,?)",
        (f["title"],f["category"],f["location"],f["priority"],f["description"]))
    return redirect("/")
@app.post("/update/<int:i>")
def update(i):
    with db() as c: c.execute("UPDATE complaints SET status=? WHERE id=?",(request.form["status"],i))
    return redirect("/")
if __name__=="__main__":
    init(); app.run(debug=True)
