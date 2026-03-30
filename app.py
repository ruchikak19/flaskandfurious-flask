# Refactored: Use CRUD naming (read, create) in InfoModel
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restful import Api, Resource
import sqlite3
import os

app = Flask(__name__)
CORS(app, supports_credentials=True, origins='*')

api = Api(app)

# --- Model class for InfoDb with CRUD naming ---
class InfoModel:
    def __init__(self):
        self.data = [
            {
                "FirstName": "John",
                "LastName": "Mortensen",
                "DOB": "October 21",
                "Residence": "San Diego",
                "Email": "jmortensen@powayusd.com",
                "Owns_Cars": ["2015-Fusion", "2011-Ranger", "2003-Excursion", "1997-F350", "1969-Cadillac", "2015-Kuboto-3301"]
            },
            {
                "FirstName": "Shane",
                "LastName": "Lopez",
                "DOB": "February 27",
                "Residence": "San Diego",
                "Email": "slopez@powayusd.com",
                "Owns_Cars": ["2021-Insight"]
            }
        ]

    def read(self):
        return self.data

    def create(self, entry):
        self.data.append(entry)

# Instantiate the model
info_model = InfoModel()

# --- API Resource ---
class DataAPI(Resource):
    def get(self):
        return jsonify(info_model.read())

    def post(self):
        entry = request.get_json()
        if not entry:
            return {"error": "No data provided"}, 400
        info_model.create(entry)
        return {"message": "Entry added successfully", "entry": entry}, 201

api.add_resource(DataAPI, '/api/data')

@app.route('/')
def say_hello():
    html_content = """
    <html>
    <head>
        <title>Hello</title>
    </head>
    <body>
        <h2>Hello, World!</h2>
    </body>
    </html>
    """
    return html_content


DATABASE = "events.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_blog_db():
    """Create the blog_posts table if it doesn't exist."""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS blog_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            title TEXT NOT NULL,
            author TEXT,
            date TEXT,
            read_time TEXT,
            body TEXT,
            image BLOB,
            image_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def init_events_db():
    """Create the events table if it doesn't exist."""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            event_date TEXT NOT NULL,
            event_time TEXT NOT NULL,
            location TEXT,
            flyer TEXT,
            writeup TEXT,
            registration_link TEXT
        )
    """)
    conn.commit()
    conn.close()


# Initialize tables on startup
init_blog_db()
init_events_db()


def get_events():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events")
    rows = cursor.fetchall()
    events = []
    for row in rows:
        event = {
            "title": row["name"],
            "start": f"{row['event_date']}T{row['event_time']}",
            "location": row["location"],
            "flyer": row["flyer"],
            "writeup": row["writeup"],
            "registration": row["registration_link"]
        }
        events.append(event)
    conn.close()
    return events


@app.route("/api/events")
def events():
    return jsonify(get_events())


# ── EVENTS API ────────────────────────────────────────────

@app.route("/api/events", methods=["POST"])
def create_event():
    """Create a new event."""
    name              = request.form.get("name", "")
    event_date        = request.form.get("event_date", "")
    event_time        = request.form.get("event_time", "")
    location          = request.form.get("location", "")
    flyer             = request.form.get("flyer", "")
    writeup           = request.form.get("writeup", "")
    registration_link = request.form.get("registration_link", "")

    if not name or not event_date or not event_time:
        return {"error": "name, event_date, and event_time are required"}, 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO events (name, event_date, event_time, location, flyer, writeup, registration_link)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, event_date, event_time, location, flyer, writeup, registration_link))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"message": "Event created", "id": new_id}), 201


@app.route("/api/events/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    """Update an existing event."""
    name              = request.form.get("name")
    event_date        = request.form.get("event_date")
    event_time        = request.form.get("event_time")
    location          = request.form.get("location")
    flyer             = request.form.get("flyer")
    writeup           = request.form.get("writeup")
    registration_link = request.form.get("registration_link")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE events
        SET name=?, event_date=?, event_time=?, location=?, flyer=?, writeup=?, registration_link=?
        WHERE id=?
    """, (name, event_date, event_time, location, flyer, writeup, registration_link, event_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Event updated"}), 200


@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    """Delete an event."""
    conn = get_db()
    conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Event deleted"}), 200


# ── BLOG API ──────────────────────────────────────────────

@app.route("/api/blog", methods=["GET"])
def get_blog_posts():
    """Return all blog posts (without image binary)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, category, title, author, date, read_time, body, image_type, created_at
        FROM blog_posts
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    posts = []
    for row in rows:
        post = dict(row)
        post["image_url"] = f"/api/blog/{row['id']}/image" if row["image_type"] else None
        posts.append(post)
    return jsonify(posts)


@app.route("/api/blog/<int:post_id>", methods=["GET"])
def get_blog_post(post_id):
    """Return a single blog post by ID."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, category, title, author, date, read_time, body, image_type, created_at
        FROM blog_posts WHERE id = ?
    """, (post_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"error": "Post not found"}, 404
    post = dict(row)
    post["image_url"] = f"/api/blog/{post_id}/image" if row["image_type"] else None
    return jsonify(post)


@app.route("/api/blog/<int:post_id>/image", methods=["GET"])
def get_blog_image(post_id):
    """Serve the image for a blog post."""
    from flask import Response
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT image, image_type FROM blog_posts WHERE id = ?", (post_id,))
    row = cursor.fetchone()
    conn.close()
    if not row or not row["image"]:
        return {"error": "Image not found"}, 404
    return Response(row["image"], mimetype=row["image_type"])


@app.route("/api/blog", methods=["POST"])
def create_blog_post():
    """Create a new blog post. Accepts multipart/form-data so image can be uploaded."""
    from flask import request
    category  = request.form.get("category", "")
    title     = request.form.get("title", "")
    author    = request.form.get("author", "")
    date      = request.form.get("date", "")
    read_time = request.form.get("read_time", "")
    body      = request.form.get("body", "")

    image_data = None
    image_type = None
    if "image" in request.files:
        f = request.files["image"]
        image_data = f.read()
        image_type = f.mimetype

    if not title:
        return {"error": "Title is required"}, 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO blog_posts (category, title, author, date, read_time, body, image, image_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (category, title, author, date, read_time, body, image_data, image_type))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({"message": "Post created", "id": new_id}), 201


@app.route("/api/blog/<int:post_id>", methods=["PUT"])
def update_blog_post(post_id):
    """Update an existing blog post."""
    category  = request.form.get("category")
    title     = request.form.get("title")
    author    = request.form.get("author")
    date      = request.form.get("date")
    read_time = request.form.get("read_time")
    body      = request.form.get("body")

    image_data = None
    image_type = None
    if "image" in request.files:
        f = request.files["image"]
        image_data = f.read()
        image_type = f.mimetype

    conn = get_db()
    cursor = conn.cursor()

    if image_data:
        cursor.execute("""
            UPDATE blog_posts
            SET category=?, title=?, author=?, date=?, read_time=?, body=?, image=?, image_type=?
            WHERE id=?
        """, (category, title, author, date, read_time, body, image_data, image_type, post_id))
    else:
        cursor.execute("""
            UPDATE blog_posts
            SET category=?, title=?, author=?, date=?, read_time=?, body=?
            WHERE id=?
        """, (category, title, author, date, read_time, body, post_id))

    conn.commit()
    conn.close()
    return jsonify({"message": "Post updated"}), 200


@app.route("/api/blog/<int:post_id>", methods=["DELETE"])
def delete_blog_post(post_id):
    """Delete a blog post."""
    conn = get_db()
    conn.execute("DELETE FROM blog_posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Post deleted"}), 200


if __name__ == '__main__':
    app.run(port=8421)