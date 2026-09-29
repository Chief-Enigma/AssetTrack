from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request
)
from flask_login import login_required, current_user
from sqlalchemy import or_

from app import db
from app.models import Device, Category


devices = Blueprint("devices", __name__)


ALLOWED_STATUSES = {
    "available",
    "in_use",
    "maintenance",
    "defective"
}


@devices.route("/")
@login_required
def index():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    category_id = request.args.get("category", "").strip()

    query = Device.query

    if search:
        search_term = f"%{search}%"

        query = query.filter(
            or_(
                Device.name.ilike(search_term),
                Device.serial_number.ilike(search_term),
                Device.location.ilike(search_term)
            )
        )

    if status in ALLOWED_STATUSES:
        query = query.filter(Device.status == status)

    if category_id.isdigit():
        query = query.filter(
            Device.category_id == int(category_id)
        )

    device_list = (
        query
        .order_by(Device.created_at.desc())
        .all()
    )

    categories = (
        Category.query
        .order_by(Category.name.asc())
        .all()
    )

    return render_template(
        "devices/index.html",
        devices=device_list,
        categories=categories,
        search=search,
        selected_status=status,
        selected_category=category_id
    )


@devices.route("/new", methods=["GET", "POST"])
@login_required
def create():
    categories = (
        Category.query
        .order_by(Category.name.asc())
        .all()
    )

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        serial_number = request.form.get(
            "serial_number",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        purchase_date_raw = request.form.get(
            "purchase_date",
            ""
        ).strip()

        status = request.form.get(
            "status",
            "available"
        ).strip()

        category_id = request.form.get(
            "category_id",
            ""
        ).strip()

        if not name or not serial_number or not location:
            flash(
                "Name, Seriennummer und Standort sind Pflichtfelder.",
                "error"
            )

            return render_template(
                "devices/form.html",
                categories=categories,
                device=None
            )

        if status not in ALLOWED_STATUSES:
            flash(
                "Der ausgewählte Status ist ungültig.",
                "error"
            )

            return render_template(
                "devices/form.html",
                categories=categories,
                device=None
            )

        if not category_id.isdigit():
            flash(
                "Bitte eine gültige Kategorie auswählen.",
                "error"
            )

            return render_template(
                "devices/form.html",
                categories=categories,
                device=None
            )

        category = db.session.get(
            Category,
            int(category_id)
        )

        if category is None:
            flash(
                "Die ausgewählte Kategorie existiert nicht.",
                "error"
            )

            return render_template(
                "devices/form.html",
                categories=categories,
                device=None
            )

        existing_device = Device.query.filter_by(
            serial_number=serial_number
        ).first()

        if existing_device:
            flash(
                "Ein Gerät mit dieser Seriennummer existiert bereits.",
                "error"
            )

            return render_template(
                "devices/form.html",
                categories=categories,
                device=None
            )

        purchase_date = None

        if purchase_date_raw:
            try:
                purchase_date = datetime.strptime(
                    purchase_date_raw,
                    "%Y-%m-%d"
                ).date()

            except ValueError:
                flash(
                    "Das Kaufdatum ist ungültig.",
                    "error"
                )

                return render_template(
                    "devices/form.html",
                    categories=categories,
                    device=None
                )

        device = Device(
            name=name,
            serial_number=serial_number,
            location=location,
            purchase_date=purchase_date,
            status=status,
            category_id=category.id,
            created_by=current_user.id
        )

        db.session.add(device)
        db.session.commit()

        flash(
            f"Gerät „{device.name}“ wurde erfolgreich erstellt.",
            "success"
        )

        return redirect(
            url_for("devices.detail", device_id=device.id)
        )

    return render_template(
        "devices/form.html",
        categories=categories,
        device=None
    )


@devices.route("/<int:device_id>")
@login_required
def detail(device_id):
    device = db.get_or_404(Device, device_id)

    return render_template(
        "devices/detail.html",
        device=device
    )


@devices.route("/<int:device_id>/edit", methods=["GET", "POST"])
@login_required
def edit(device_id):
    device = db.get_or_404(Device, device_id)

    categories = (
        Category.query
        .order_by(Category.name.asc())
        .all()
    )

    if request.method == "POST":
        name = request.form.get("name", "").strip()

        serial_number = request.form.get(
            "serial_number",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        purchase_date_raw = request.form.get(
            "purchase_date",
            ""
        ).strip()

        status = request.form.get(
            "status",
            ""
        ).strip()

        category_id = request.form.get(
            "category_id",
            ""
        ).strip()

        if not name or not serial_number or not location:
            flash(
                "Name, Seriennummer und Standort sind Pflichtfelder.",
                "error"
            )

            return render_template(
                "devices/form.html",
                categories=categories,
                device=device
            )

        if status not in ALLOWED_STATUSES:
            flash(
                "Der ausgewählte Status ist ungültig.",
                "error"
            )

            return render_template(
                "devices/form.html",
                categories=categories,
                device=device
            )

        if not category_id.isdigit():
            flash(
                "Bitte eine gültige Kategorie auswählen.",
                "error"
            )

            return render_template(
                "devices/form.html",
                categories=categories,
                device=device
            )

        category = db.session.get(
            Category,
            int(category_id)
        )

        if category is None:
            flash(
                "Die ausgewählte Kategorie existiert nicht.",
                "error"
            )

            return render_template(
                "devices/form.html",
                categories=categories,
                device=device
            )

        duplicate = (
            Device.query
            .filter(
                Device.serial_number == serial_number,
                Device.id != device.id
            )
            .first()
        )

        if duplicate:
            flash(
                "Ein anderes Gerät verwendet bereits diese Seriennummer.",
                "error"
            )

            return render_template(
                "devices/form.html",
                categories=categories,
                device=device
            )

        purchase_date = None

        if purchase_date_raw:
            try:
                purchase_date = datetime.strptime(
                    purchase_date_raw,
                    "%Y-%m-%d"
                ).date()

            except ValueError:
                flash(
                    "Das Kaufdatum ist ungültig.",
                    "error"
                )

                return render_template(
                    "devices/form.html",
                    categories=categories,
                    device=device
                )

        device.name = name
        device.serial_number = serial_number
        device.location = location
        device.purchase_date = purchase_date
        device.status = status
        device.category_id = category.id

        db.session.commit()

        flash(
            "Gerät wurde erfolgreich aktualisiert.",
            "success"
        )

        return redirect(
            url_for(
                "devices.detail",
                device_id=device.id
            )
        )

    return render_template(
        "devices/form.html",
        categories=categories,
        device=device
    )


@devices.route("/<int:device_id>/delete", methods=["POST"])
@login_required
def delete(device_id):
    device = db.get_or_404(Device, device_id)

    name = device.name

    db.session.delete(device)
    db.session.commit()

    flash(
        f"Gerät „{name}“ wurde gelöscht.",
        "success"
    )

    return redirect(url_for("devices.index"))