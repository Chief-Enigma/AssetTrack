from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app
)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from app import db
from app.models import User


auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if not username or not password:
            flash(
                "Bitte Benutzername und Passwort eingeben.",
                "error"
            )

            return render_template(
                "auth/login.html"
            )

        user = User.query.filter_by(
            username=username
        ).first()

        if user is None or not user.check_password(password):
            flash(
                "Benutzername oder Passwort ist falsch.",
                "error"
            )

            return render_template(
                "auth/login.html"
            )

        login_user(user)

        flash(
            f"Willkommen zurück, {user.username}.",
            "success"
        )

        return redirect(
            url_for("main.dashboard")
        )

    return render_template(
        "auth/login.html"
    )


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(
            url_for("main.dashboard")
        )

    if request.method == "POST":
        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        password_confirm = request.form.get(
            "password_confirm",
            ""
        )

        registration_code = request.form.get(
            "registration_code",
            ""
        ).strip()

        if (
            not username
            or not email
            or not password
            or not password_confirm
            or not registration_code
        ):
            flash(
                "Bitte alle Felder ausfüllen.",
                "error"
            )

            return render_template(
                "auth/register.html"
            )

        if registration_code != current_app.config["REGISTRATION_CODE"]:
            flash(
                "Der Registrierungscode ist ungültig.",
                "error"
            )

            return render_template(
                "auth/register.html"
            )

        if len(username) < 3:
            flash(
                "Der Benutzername muss mindestens 3 Zeichen lang sein.",
                "error"
            )

            return render_template(
                "auth/register.html"
            )

        if "@" not in email or "." not in email:
            flash(
                "Bitte eine gültige E-Mail-Adresse eingeben.",
                "error"
            )

            return render_template(
                "auth/register.html"
            )

        if len(password) < 8:
            flash(
                "Das Passwort muss mindestens 8 Zeichen lang sein.",
                "error"
            )

            return render_template(
                "auth/register.html"
            )

        if password != password_confirm:
            flash(
                "Die Passwörter stimmen nicht überein.",
                "error"
            )

            return render_template(
                "auth/register.html"
            )

        existing_username = User.query.filter_by(
            username=username
        ).first()

        if existing_username:
            flash(
                "Dieser Benutzername ist bereits vergeben.",
                "error"
            )

            return render_template(
                "auth/register.html"
            )

        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:
            flash(
                "Diese E-Mail-Adresse ist bereits registriert.",
                "error"
            )

            return render_template(
                "auth/register.html"
            )

        user = User(
            username=username,
            email=email
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash(
            "Account erfolgreich erstellt. "
            "Du kannst dich jetzt anmelden.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/register.html"
    )


@auth.route("/logout")
@login_required
def logout():
    logout_user()

    flash(
        "Du wurdest erfolgreich abgemeldet.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )