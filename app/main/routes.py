from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from app.models import Device, Maintenance


main = Blueprint("main", __name__)


@main.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    return redirect(url_for("auth.login"))


@main.route("/dashboard")
@login_required
def dashboard():
    total_devices = Device.query.count()

    available_devices = Device.query.filter_by(
        status="available"
    ).count()

    maintenance_devices = Device.query.filter_by(
        status="maintenance"
    ).count()

    defective_devices = Device.query.filter_by(
        status="defective"
    ).count()

    recent_maintenance = (
        Maintenance.query
        .order_by(Maintenance.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard.html",
        total_devices=total_devices,
        available_devices=available_devices,
        maintenance_devices=maintenance_devices,
        defective_devices=defective_devices,
        recent_maintenance=recent_maintenance
    )