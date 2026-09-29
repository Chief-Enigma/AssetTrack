from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request
)
from flask_login import login_required

from app import db
from app.models import Device, Maintenance


maintenance = Blueprint("maintenance", __name__)


@maintenance.route("/")
@login_required
def index():
    status = request.args.get("status", "").strip()

    query = Maintenance.query

    if status == "open":
        query = query.filter_by(completed=False)

    elif status == "completed":
        query = query.filter_by(completed=True)

    maintenance_entries = (
        query
        .order_by(
            Maintenance.completed.asc(),
            Maintenance.maintenance_date.desc(),
            Maintenance.created_at.desc()
        )
        .all()
    )

    return render_template(
        "maintenance/index.html",
        maintenance_entries=maintenance_entries,
        selected_status=status
    )


@maintenance.route(
    "/device/<int:device_id>/new",
    methods=["GET", "POST"]
)
@login_required
def create(device_id):
    device = db.get_or_404(Device, device_id)

    if request.method == "POST":
        maintenance_date_raw = request.form.get(
            "maintenance_date",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        cost_raw = request.form.get(
            "cost",
            "0"
        ).strip()

        if not maintenance_date_raw:
            flash(
                "Bitte ein Wartungsdatum angeben.",
                "error"
            )

            return render_template(
                "maintenance/form.html",
                device=device,
                maintenance_entry=None
            )

        if not description:
            flash(
                "Bitte eine Beschreibung eingeben.",
                "error"
            )

            return render_template(
                "maintenance/form.html",
                device=device,
                maintenance_entry=None
            )

        try:
            maintenance_date = datetime.strptime(
                maintenance_date_raw,
                "%Y-%m-%d"
            ).date()

        except ValueError:
            flash(
                "Das Wartungsdatum ist ungültig.",
                "error"
            )

            return render_template(
                "maintenance/form.html",
                device=device,
                maintenance_entry=None
            )

        try:
            cost = Decimal(
                cost_raw.replace(",", ".")
            )

            if cost < 0:
                raise InvalidOperation

        except (InvalidOperation, ValueError):
            flash(
                "Bitte gültige Kosten eingeben.",
                "error"
            )

            return render_template(
                "maintenance/form.html",
                device=device,
                maintenance_entry=None
            )

        entry = Maintenance(
            device_id=device.id,
            maintenance_date=maintenance_date,
            description=description,
            cost=cost,
            completed=False
        )

        # Business-Logik:
        # Sobald eine Wartung eröffnet wird,
        # befindet sich das Gerät in Wartung.
        device.status = "maintenance"

        db.session.add(entry)
        db.session.commit()

        flash(
            f"Wartung für „{device.name}“ wurde eröffnet.",
            "success"
        )

        return redirect(
            url_for(
                "devices.detail",
                device_id=device.id
            )
        )

    return render_template(
        "maintenance/form.html",
        device=device,
        maintenance_entry=None
    )


@maintenance.route(
    "/<int:maintenance_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit(maintenance_id):
    entry = db.get_or_404(
        Maintenance,
        maintenance_id
    )

    if entry.completed:
        flash(
            "Eine abgeschlossene Wartung kann nicht mehr bearbeitet werden.",
            "error"
        )

        return redirect(
            url_for(
                "devices.detail",
                device_id=entry.device_id
            )
        )

    if request.method == "POST":
        maintenance_date_raw = request.form.get(
            "maintenance_date",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        cost_raw = request.form.get(
            "cost",
            "0"
        ).strip()

        if not maintenance_date_raw or not description:
            flash(
                "Datum und Beschreibung sind Pflichtfelder.",
                "error"
            )

            return render_template(
                "maintenance/form.html",
                device=entry.device,
                maintenance_entry=entry
            )

        try:
            maintenance_date = datetime.strptime(
                maintenance_date_raw,
                "%Y-%m-%d"
            ).date()

        except ValueError:
            flash(
                "Das Wartungsdatum ist ungültig.",
                "error"
            )

            return render_template(
                "maintenance/form.html",
                device=entry.device,
                maintenance_entry=entry
            )

        try:
            cost = Decimal(
                cost_raw.replace(",", ".")
            )

            if cost < 0:
                raise InvalidOperation

        except (InvalidOperation, ValueError):
            flash(
                "Bitte gültige Kosten eingeben.",
                "error"
            )

            return render_template(
                "maintenance/form.html",
                device=entry.device,
                maintenance_entry=entry
            )

        entry.maintenance_date = maintenance_date
        entry.description = description
        entry.cost = cost

        db.session.commit()

        flash(
            "Wartung wurde aktualisiert.",
            "success"
        )

        return redirect(
            url_for(
                "devices.detail",
                device_id=entry.device_id
            )
        )

    return render_template(
        "maintenance/form.html",
        device=entry.device,
        maintenance_entry=entry
    )


@maintenance.route(
    "/<int:maintenance_id>/complete",
    methods=["POST"]
)
@login_required
def complete(maintenance_id):
    entry = db.get_or_404(
        Maintenance,
        maintenance_id
    )

    if entry.completed:
        flash(
            "Diese Wartung wurde bereits abgeschlossen.",
            "warning"
        )

        return redirect(
            url_for(
                "devices.detail",
                device_id=entry.device_id
            )
        )

    entry.completed = True

    # Prüfen, ob das Gerät noch weitere
    # offene Wartungen besitzt.
    other_open_maintenance = (
        Maintenance.query
        .filter(
            Maintenance.device_id == entry.device_id,
            Maintenance.completed.is_(False),
            Maintenance.id != entry.id
        )
        .first()
    )

    # Nur wenn keine weitere Wartung offen ist,
    # wird das Gerät wieder verfügbar.
    if other_open_maintenance is None:
        entry.device.status = "available"

    db.session.commit()

    flash(
        f"Wartung für „{entry.device.name}“ wurde abgeschlossen.",
        "success"
    )

    return redirect(
        url_for(
            "devices.detail",
            device_id=entry.device_id
        )
    )


@maintenance.route(
    "/<int:maintenance_id>/delete",
    methods=["POST"]
)
@login_required
def delete(maintenance_id):
    entry = db.get_or_404(
        Maintenance,
        maintenance_id
    )

    device = entry.device
    was_open = not entry.completed

    db.session.delete(entry)
    db.session.flush()

    if was_open:
        other_open_maintenance = (
            Maintenance.query
            .filter(
                Maintenance.device_id == device.id,
                Maintenance.completed.is_(False)
            )
            .first()
        )

        if other_open_maintenance is None:
            device.status = "available"

    db.session.commit()

    flash(
        "Wartungseintrag wurde gelöscht.",
        "success"
    )

    return redirect(
        url_for(
            "devices.detail",
            device_id=device.id
        )
    )
    