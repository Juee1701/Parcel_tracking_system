from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "parcel-project-demo-key"
DATABASE = "parcels.db"

STATUSES = ["Booked", "In Transit", "Out for Delivery", "Delivered"]

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS parcels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_id TEXT UNIQUE NOT NULL,
            sender_name TEXT NOT NULL,
            receiver_name TEXT NOT NULL,
            destination TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'Booked',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    conn = get_db_connection()
    total = conn.execute("SELECT COUNT(*) FROM parcels").fetchone()[0]
    delivered = conn.execute(
        "SELECT COUNT(*) FROM parcels WHERE status = 'Delivered'"
    ).fetchone()[0]
    in_transit = conn.execute(
        "SELECT COUNT(*) FROM parcels WHERE status IN ('In Transit', 'Out for Delivery')"
    ).fetchone()[0]
    recent = conn.execute(
        "SELECT * FROM parcels ORDER BY id DESC LIMIT 5"
    ).fetchall()
    conn.close()
    return render_template("index.html", total=total, delivered=delivered,
                           in_transit=in_transit, recent=recent)

@app.route("/add", methods=["GET", "POST"])
def add_parcel():
    if request.method == "POST":
        sender = request.form.get("sender_name", "").strip()
        receiver = request.form.get("receiver_name", "").strip()
        destination = request.form.get("destination", "").strip()
        description = request.form.get("description", "").strip()

        if not sender or not receiver or not destination:
            flash("Please fill in sender, receiver, and destination.", "error")
            return render_template("add_parcel.html")

        tracking_id = "PKG-" + uuid.uuid4().hex[:8].upper()
        created_at = datetime.now().strftime("%d-%m-%Y %I:%M %p")

        conn = get_db_connection()
        try:
            conn.execute("""
                INSERT INTO parcels
                (tracking_id, sender_name, receiver_name, destination,
                 description, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tracking_id, sender, receiver, destination,
                  description, "Booked", created_at))
            conn.commit()
        except sqlite3.Error as error:
            flash(f"Could not save parcel: {error}", "error")
            conn.close()
            return render_template("add_parcel.html")
        conn.close()
        flash(f"Parcel added successfully. Tracking ID: {tracking_id}", "success")
        return redirect(url_for("track_parcel", tracking_id=tracking_id))

    return render_template("add_parcel.html")

@app.route("/track", methods=["GET", "POST"])
def track_parcel():
    tracking_id = request.args.get("tracking_id", "").strip()
    parcel = None
    searched = bool(tracking_id)

    if request.method == "POST":
        tracking_id = request.form.get("tracking_id", "").strip()
        return redirect(url_for("track_parcel", tracking_id=tracking_id))

    if tracking_id:
        conn = get_db_connection()
        parcel = conn.execute(
            "SELECT * FROM parcels WHERE tracking_id = ?",
            (tracking_id.upper(),)
        ).fetchone()
        conn.close()
    return render_template("track.html", parcel=parcel, searched=searched,
                           tracking_id=tracking_id)

@app.route("/parcels")
def all_parcels():
    conn = get_db_connection()
    parcels = conn.execute("SELECT * FROM parcels ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("parcels.html", parcels=parcels)

@app.route("/update/<int:parcel_id>", methods=["GET", "POST"])
def update_status(parcel_id):
    conn = get_db_connection()
    parcel = conn.execute("SELECT * FROM parcels WHERE id = ?", (parcel_id,)).fetchone()

    if parcel is None:
        conn.close()
        flash("Parcel not found.", "error")
        return redirect(url_for("all_parcels"))

    if request.method == "POST":
        status = request.form.get("status", "")
        if status not in STATUSES:
            conn.close()
            flash("Please select a valid status.", "error")
            return redirect(url_for("all_parcels"))

        conn.execute("UPDATE parcels SET status = ? WHERE id = ?", (status, parcel_id))
        conn.commit()
        conn.close()
        flash("Parcel status updated successfully.", "success")
        return redirect(url_for("all_parcels"))

    conn.close()
    return render_template("update_status.html", parcel=parcel, statuses=STATUSES)

@app.route("/delete/<int:parcel_id>", methods=["POST"])
def delete_parcel(parcel_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM parcels WHERE id = ?", (parcel_id,))
    conn.commit()
    conn.close()
    flash("Parcel record deleted.", "success")
    return redirect(url_for("all_parcels"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
