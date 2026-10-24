# DIGIVAULT MAIN SERVER
# Secure File Vault with Face Authentication + OTP + Encryption

# STANDARD LIBRARIES
import os
import shutil
import tempfile
from datetime import datetime, timedelta

# FLASK IMPORTS
from flask import Flask, render_template, request, redirect, send_file, session, flash

# DATABASE IMPORTS
from database.db import db
from database.models import User

# SECURITY MODULES
from modules.face_auth import capture_face_encoding, verify_face
from modules.anti_spoof import liveness_check
from modules.otp_service import generate_otp, verify_otp
from modules.email_service import send_security_alert, send_otp_email
from modules.vault_crypto import encrypt_file, decrypt_file

# FLASK APPLICATION CONFIGURATION

app = Flask(__name__)

# Session encryption key
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# SQLite database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

db.init_app(app)

# Create database tables on startup
with app.app_context():
    db.create_all()

# HOME ROUTE

@app.route("/")
def home():
    return render_template("home.html")

# USER REGISTRATION

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register new user and capture face encoding."""

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]

        # Prevent duplicate accounts
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please login.", "danger")
            return redirect("/login")

        # Capture biometric face encoding
        face_encoding = capture_face_encoding()

        user = User(
            name=name,
            email=email,
            face_encoding=face_encoding
        )

        db.session.add(user)
        db.session.commit()

        # Create user vault directory
        user_vault = os.path.join("vault_storage", email)
        if not os.path.exists(user_vault):
            os.makedirs(user_vault)

        flash("User registered successfully!", "success")
        return redirect("/login")

    return render_template("auth/register.html")

# LOGIN WITH FACE AUTHENTICATION

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User not found", "danger")
            return redirect("/login")

        # Account lock protection
        if user.locked:

            unlock_time = user.lock_time + timedelta(minutes=1)

            if datetime.now() > unlock_time:
                user.locked = False
                user.failed_attempts = 0
                user.lock_time = None
                db.session.commit()
            else:
                flash("Account locked. Try again later.", "danger")
                return redirect("/login")

        # Store temporary email for next step
        session["temp_email"] = user.email

        return redirect("/face-scan")

    return render_template("auth/login.html")


import cv2
from flask import Response

camera = cv2.VideoCapture(0)

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video-feed')
def video_feed():
    return Response(gen_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame')




# FACE AUTHENTICATION PAGE

@app.route("/face-scan")
def face_scan():

    if "temp_email" not in session:
        return redirect("/login")

    return render_template("auth/face_scan.html")

# PROCESS FACE + LIVENESS CHECK

@app.route("/process-face")
def process_face():

    if "temp_email" not in session:
        return redirect("/login")

    user = User.query.filter_by(email=session["temp_email"]).first()

    # ---------------- FACE VERIFICATION ----------------
    face_valid = verify_face(user.face_encoding)

    if not face_valid:

        user.failed_attempts += 1

        if user.failed_attempts >= 3:
            user.locked = True
            user.lock_time = datetime.now()
            send_security_alert(user.email)

        db.session.commit()

        flash("Face authentication failed", "danger")
        return redirect("/login")

    # ---------------- LIVENESS CHECK ----------------
    live = liveness_check()

    if not live:

        user.failed_attempts += 1

        if user.failed_attempts >= 3:
            user.locked = True
            user.lock_time = datetime.now()
            send_security_alert(user.email)

        db.session.commit()

        flash("Spoof detected", "danger")
        return redirect("/login")

    # Reset failure counter
    user.failed_attempts = 0
    db.session.commit()

    # ---------------- OTP GENERATION ----------------
    otp = generate_otp()

    session["otp"] = otp
    session["otp_expiry"] = (
        datetime.now() + timedelta(minutes=2)
    ).timestamp()

    send_otp_email(user.email, otp)

    return redirect("/otp")

# OTP VERIFICATION

@app.route("/otp", methods=["GET", "POST"])
def otp():
    """Second authentication layer using email OTP."""

    if request.method == "POST":

        user_otp = request.form["otp"]

        if verify_otp(user_otp):

            user = User.query.filter_by(
                email=session["temp_email"]
            ).first()

            user.failed_attempts = 0
            db.session.commit()

            # Start authenticated session
            session["user_email"] = user.email
            session["user_name"] = user.name

            return redirect("/vault")

        flash("Invalid or expired OTP. Please login again.", "danger")
        return redirect("/login")

    return render_template(
        "auth/otp.html",
        otp_expiry=session.get("otp_expiry")
    )

# USER VAULT DASHBOARD

@app.route("/vault")
def vault():
    """Display user vault and calculate storage usage."""

    if "user_email" not in session:
        return redirect("/login")

    user_email = session["user_email"]
    user_vault = os.path.join("vault_storage", user_email)

    if not os.path.exists(user_vault):
        os.makedirs(user_vault)

    files = os.listdir(user_vault)

    total_size = 0
    for file in files:
        filepath = os.path.join(user_vault, file)

        if os.path.isfile(filepath):
            total_size += os.path.getsize(filepath)

    storage_mb = round(total_size / (1024 * 1024), 2)

    return render_template(
        "vault/vault.html",
        files=files,
        storage=storage_mb
    )

# FILE UPLOAD

@app.route("/upload", methods=["POST"])
def upload():
    """Upload and immediately encrypt file."""

    if "user_email" not in session:
        return redirect("/login")

    file = request.files["file"]

    user_email = session["user_email"]
    user_vault = os.path.join("vault_storage", user_email)

    filepath = os.path.join(user_vault, file.filename)

    file.save(filepath)

    # Encrypt stored file
    encrypt_file(filepath)

    return redirect("/vault")

# FILE DOWNLOAD

@app.route("/download/<filename>")
def download(filename):
    """
    Secure download workflow:
    decrypt → temp copy → re-encrypt → send
    """

    if "user_email" not in session:
        return redirect("/login")

    user_email = session["user_email"]

    user_vault = os.path.join("vault_storage", user_email)
    filepath = os.path.join(user_vault, filename)

    if not os.path.exists(filepath):
        return "File not found"

    decrypt_file(filepath)

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_path = temp_file.name
    temp_file.close()

    shutil.copy(filepath, temp_path)

    encrypt_file(filepath)

    response = send_file(
        temp_path,
        as_attachment=True,
        download_name=filename
    )

    # Delete temp file after download
    @response.call_on_close
    def cleanup():
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return response

# FILE UPDATE

@app.route("/update/<filename>", methods=["POST"])
def update_file(filename):
    """Replace existing vault file."""

    if "user_email" not in session:
        return redirect("/login")

    user_email = session["user_email"]
    user_vault = os.path.join("vault_storage", user_email)

    filepath = os.path.join(user_vault, filename)

    file = request.files["file"]

    file.save(filepath)

    encrypt_file(filepath)

    return redirect("/vault")

# FILE DELETE

@app.route("/delete/<filename>")
def delete(filename):
    """Delete file from vault."""

    if "user_email" not in session:
        return redirect("/login")

    user_email = session["user_email"]

    user_vault = os.path.join("vault_storage", user_email)
    filepath = os.path.join(user_vault, filename)

    if os.path.exists(filepath):
        os.remove(filepath)

    return redirect("/vault")

# LOGOUT

@app.route("/logout")
def logout():
    """Clear session and logout user."""
    session.clear()
    return redirect("/login")

# SERVER ENTRY POINT

if __name__ == "__main__":
    app.run(debug=True)