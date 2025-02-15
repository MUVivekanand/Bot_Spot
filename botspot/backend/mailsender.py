from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
from celery import Celery
import os

app = Flask(__name__)
CORS(app)

# Configure Flask Mail
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "tech.services.av40@gmail.com"  # Your email
app.config["MAIL_PASSWORD"] = "jbuq rxul rxdw phrz"  # Your app password
app.config["MAIL_DEFAULT_SENDER"] = "tech.services.av40@gmail.com"  # Set default sender

mail = Mail(app)

# Configure Celery with SQLite as broker
app.config["CELERY_BROKER_URL"] = "sqla+sqlite:///celerydb.sqlite"
app.config["CELERY_RESULT_BACKEND"] = "db+sqlite:///celerydb.sqlite"

celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])
celery.conf.update(app.config)

# Celery task to send email
@celery.task
def send_report_email(username, profile_link):
    msg = Message(
        subject="🚨 Fake Account Report",
        recipients=["vivekanandmu22@gmail.com"],  # Change to your fixed email
        body=f"""
        A fake Instagram account has been detected.

        Profile Link: {profile_link}

        Please review and take necessary action.
        """
    )
    with app.app_context():
        mail.send(msg)
    return f"Report sent for {username}"

@app.route("/report", methods=["POST"])
def report_fake_account():
    data = request.get_json()
    username = data.get("username")

    if not username:
        return jsonify({"error": "Username is required"}), 400

    profile_link = f"https://instagram.com/{username}"
    send_report_email.delay(username, profile_link)  # Run async task

    return jsonify({"message": f"Report submitted for {username}"}), 200

if __name__ == "__main__":
    app.run(debug=True)
