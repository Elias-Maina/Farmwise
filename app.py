# app.py
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import MySQLdb.cursors
import re

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# MySQL Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "120590eliasmaina"
app.config["MYSQL_DB"] = "farm_management"

mysql = MySQL(app)


@app.route("/")
def index():
    if "loggedin" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        account = cursor.fetchone()

        if account and check_password_hash(account["password"], password):
            session["loggedin"] = True
            session["id"] = account["id"]
            session["username"] = account["username"]
            return redirect(url_for("dashboard"))
        else:
            flash("Incorrect username/password!")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        account = cursor.fetchone()

        if account:
            flash("Account already exists!")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email address!")
        elif not username or not password or not email:
            flash("Please fill out the form!")
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users VALUES (NULL, %s, %s, %s)",
                (username, email, hashed_password),
            )
            mysql.connection.commit()
            flash("You have successfully registered!")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "loggedin" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("SELECT COUNT(*) as total FROM animals")
        total_animals = cursor.fetchone()["total"]

        cursor.execute(
            'SELECT COUNT(*) as sick FROM animals WHERE health_status = "Sick"'
        )
        sick_animals = cursor.fetchone()["sick"]

        cursor.execute(
            "SELECT COUNT(*) as fed_today FROM feeding WHERE DATE(feeding_date) = CURDATE()"
        )
        fed_today = cursor.fetchone()["fed_today"]

        cursor.execute(
            "SELECT COUNT(*) as health_checks FROM health_records WHERE DATE(check_date) = CURDATE()"
        )
        health_checks_today = cursor.fetchone()["health_checks"]

        return render_template(
            "dashboard.html",
            total_animals=total_animals,
            sick_animals=sick_animals,
            fed_today=fed_today,
            health_checks_today=health_checks_today,
        )
    return redirect(url_for("login"))


@app.route("/animals")
def animals():
    if "loggedin" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM animals ORDER BY id DESC")
        animals = cursor.fetchall()
        return render_template("animals.html", animals=animals)
    return redirect(url_for("login"))


@app.route("/add_animal", methods=["POST"])
def add_animal():
    if "loggedin" in session:
        tag_number = request.form["tag_number"]
        animal_type = request.form["animal_type"]
        breed = request.form["breed"]
        birth_date = request.form["birth_date"]
        weight = request.form["weight"]
        health_status = request.form["health_status"]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO animals (tag_number, animal_type, breed, birth_date, weight, health_status) VALUES (%s, %s, %s, %s, %s, %s)",
            (tag_number, animal_type, breed, birth_date, weight, health_status),
        )
        mysql.connection.commit()
        flash("Animal added successfully!")
        return redirect(url_for("animals"))
    return redirect(url_for("login"))


@app.route("/feeding")
def feeding():
    if "loggedin" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            """SELECT f.*, a.tag_number, a.animal_type 
                         FROM feeding f 
                         JOIN animals a ON f.animal_id = a.id 
                         ORDER BY f.feeding_date DESC"""
        )
        feeding_records = cursor.fetchall()

        cursor.execute("SELECT id, tag_number, animal_type FROM animals")
        animals = cursor.fetchall()

        return render_template(
            "feeding.html", feeding_records=feeding_records, animals=animals
        )
    return redirect(url_for("login"))


@app.route("/add_feeding", methods=["POST"])
def add_feeding():
    if "loggedin" in session:
        animal_id = request.form["animal_id"]
        feed_type = request.form["feed_type"]
        quantity = request.form["quantity"]
        feeding_date = request.form["feeding_date"]
        notes = request.form["notes"]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO feeding (animal_id, feed_type, quantity, feeding_date, notes) VALUES (%s, %s, %s, %s, %s)",
            (animal_id, feed_type, quantity, feeding_date, notes),
        )
        mysql.connection.commit()
        flash("Feeding record added successfully!")
        return redirect(url_for("feeding"))
    return redirect(url_for("login"))


@app.route("/health")
def health():
    if "loggedin" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            """SELECT h.*, a.tag_number, a.animal_type 
                         FROM health_records h 
                         JOIN animals a ON h.animal_id = a.id 
                         ORDER BY h.check_date DESC"""
        )
        health_records = cursor.fetchall()

        cursor.execute("SELECT id, tag_number, animal_type FROM animals")
        animals = cursor.fetchall()

        return render_template(
            "health.html", health_records=health_records, animals=animals
        )
    return redirect(url_for("login"))


@app.route("/add_health_record", methods=["POST"])
def add_health_record():
    if "loggedin" in session:
        animal_id = request.form["animal_id"]
        check_date = request.form["check_date"]
        temperature = request.form["temperature"]
        weight = request.form["weight"]
        symptoms = request.form["symptoms"]
        treatment = request.form["treatment"]
        vet_notes = request.form["vet_notes"]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            """INSERT INTO health_records 
                         (animal_id, check_date, temperature, weight, symptoms, treatment, vet_notes) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                animal_id,
                check_date,
                temperature,
                weight,
                symptoms,
                treatment,
                vet_notes,
            ),
        )
        mysql.connection.commit()

        if treatment:
            cursor.execute(
                "UPDATE animals SET health_status = %s WHERE id = %s",
                ("Under Treatment", animal_id),
            )
            mysql.connection.commit()

        flash("Health record added successfully!")
        return redirect(url_for("health"))
    return redirect(url_for("login"))


@app.route("/reports")
def reports():
    if "loggedin" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute(
            "SELECT animal_type, COUNT(*) as count FROM animals GROUP BY animal_type"
        )
        animal_types = cursor.fetchall()

        cursor.execute(
            "SELECT health_status, COUNT(*) as count FROM animals GROUP BY health_status"
        )
        health_status = cursor.fetchall()

        cursor.execute(
            """SELECT MONTH(feeding_date) as month, 
                         SUM(quantity * 2.5) as total_cost 
                         FROM feeding 
                         WHERE YEAR(feeding_date) = YEAR(CURDATE()) 
                         GROUP BY MONTH(feeding_date)"""
        )
        monthly_costs = cursor.fetchall()

        cursor.execute(
            """SELECT a.tag_number, a.animal_type, h.symptoms, h.check_date 
                         FROM health_records h 
                         JOIN animals a ON h.animal_id = a.id 
                         WHERE h.symptoms IS NOT NULL AND h.symptoms != ""
                         ORDER BY h.check_date DESC LIMIT 10"""
        )
        health_issues = cursor.fetchall()

        return render_template(
            "reports.html",
            animal_types=animal_types,
            health_status=health_status,
            monthly_costs=monthly_costs,
            health_issues=health_issues,
        )
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
