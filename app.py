from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
import os
from werkzeug.utils import secure_filename
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "rewear_secret_key"
app.config["UPLOAD_FOLDER"] = "uploads"

app.secret_key = "rewear_secret_key"
app.config["UPLOAD_FOLDER"] = "uploads"

@app.route("/")
def home():
    return """
    <h1>Welcome to ReWear 👕♻️</h1>
    <p>Give your clothes a second life.</p>

    <a href="/signup">Sign Up</a>
    <br><br>
    <a href="/login">Login</a>
    """


# ---------------- SIGNUP ----------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match!"

        hashed_password = generate_password_hash(password)

        connection = get_db_connection()
        cursor = connection.cursor()

        try:

            query = """
                INSERT INTO users
                (name, email, password)
                VALUES (%s, %s, %s)
            """

            cursor.execute(
                query,
                (name, email, hashed_password)
            )

            connection.commit()

        except Exception as e:

            connection.rollback()

            return f"Signup failed: {e}"

        finally:

            cursor.close()
            connection.close()

        return redirect(url_for("login"))

    return render_template("signup.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT * FROM users
            WHERE email = %s
        """

        cursor.execute(query, (email,))

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]

            return redirect(url_for("dashboard"))

        else:

            return "Invalid email or password!"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Get user information
    cursor.execute(
        "SELECT * FROM users WHERE id = %s",
        (session["user_id"],)
    )

    user = cursor.fetchone()

    # Get user's items
    cursor.execute(
        """
        SELECT *
        FROM items
        WHERE user_id = %s
        ORDER BY id DESC
        """,
        (session["user_id"],)
    )

    items = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",
        user_name=user["name"],
        points=user["points"],
        items=items,
        item_count=len(items)
    )


# ---------------- BROWSE ITEMS ----------------

@app.route("/browse")
def browse():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM items
        ORDER BY id DESC
        """
    )

    items = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "browse.html",
        items=items
    )

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

# ---------------- ADD ITEM ----------------

@app.route("/add-item", methods=["GET", "POST"])
def add_item():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        category = request.form["category"]
        clothing_type = request.form["clothing_type"]
        size = request.form["size"]
        condition_type = request.form["condition_type"]
        tags = request.form["tags"]
        points = request.form["points"]

        image = request.files["image"]

        filename = None

        if image and image.filename:

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO items
            (
                user_id,
                title,
                description,
                category,
                clothing_type,
                size,
                condition_type,
                tags,
                image,
                points
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (
                session["user_id"],
                title,
                description,
                category,
                clothing_type,
                size,
                condition_type,
                tags,
                filename,
                points
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("dashboard"))

    return render_template("add_item.html")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )

# ---------------- ITEM DETAILS ----------------

@app.route("/item/<int:item_id>")
def item_details(item_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT items.*, users.name AS seller_name
        FROM items
        JOIN users ON items.user_id = users.id
        WHERE items.id = %s
        """,
        (item_id,)
    )

    item = cursor.fetchone()

    cursor.close()
    connection.close()

    if not item:
        return "Item not found!"

    return render_template(
        "item_details.html",
        item=item
    )

# ---------------- REQUEST SWAP ----------------

@app.route("/request-swap/<int:item_id>", methods=["POST"])
def request_swap(item_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    requester_id = session["user_id"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT user_id FROM items WHERE id = %s",
            (item_id,)
        )

        item = cursor.fetchone()

        if not item:
            return "Item not found!"

        owner_id = item["user_id"]

        if owner_id == requester_id:
            return "You cannot request your own item!"

        cursor.execute(
            """
            INSERT INTO swap_requests
            (item_id, requester_id, owner_id, status)
            VALUES (%s, %s, %s, %s)
            """,
            (
                item_id,
                requester_id,
                owner_id,
                "pending"
            )
        )

        connection.commit()

    except Exception as e:
        connection.rollback()
        return f"Swap request failed: {e}"

    finally:
        cursor.close()
        connection.close()

    return render_template("swap_success.html")

# ---------------- MY SWAPS ----------------

@app.route("/swaps")
def swaps():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            swap_requests.id,
            swap_requests.status,
            swap_requests.request_date,

            items.title,
            items.image,
            items.points,

            users.name AS requester_name

        FROM swap_requests

        JOIN items
            ON swap_requests.item_id = items.id

        JOIN users
            ON swap_requests.requester_id = users.id

        WHERE swap_requests.owner_id = %s

        ORDER BY swap_requests.id DESC
        """,
        (session["user_id"],)
    )

    requests = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "swaps.html",
        requests=requests
    )

if __name__ == "__main__":
    app.run(debug=True)