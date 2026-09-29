from datetime import date, timedelta
from decimal import Decimal

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request
)
from flask_login import login_required, current_user

from app import db
from app.models import (
    Category,
    Device,
    Maintenance
)


system = Blueprint("system", __name__)


@system.route("/")
@login_required
def index():
    statistics = {
        "categories": Category.query.count(),
        "devices": Device.query.count(),
        "maintenance": Maintenance.query.count()
    }

    return render_template(
        "system/index.html",
        statistics=statistics
    )


@system.route("/seed", methods=["POST"])
@login_required
def seed():
    existing_devices = Device.query.count()
    existing_categories = Category.query.count()
    existing_maintenance = Maintenance.query.count()

    if (
        existing_devices > 0
        or existing_categories > 0
        or existing_maintenance > 0
    ):
        flash(
            "Die Datenbank enthält bereits Daten. "
            "Bitte zuerst die Demo-Daten zurücksetzen.",
            "warning"
        )

        return redirect(
            url_for("system.index")
        )

    #
    # Kategorien
    #

    category_notebook = Category(
        name="Notebook"
    )

    category_server = Category(
        name="Server"
    )

    category_network = Category(
        name="Netzwerk"
    )

    category_measurement = Category(
        name="Messgerät"
    )

    category_tool = Category(
        name="Werkzeug"
    )

    category_other = Category(
        name="Sonstiges"
    )

    categories = [
        category_notebook,
        category_server,
        category_network,
        category_measurement,
        category_tool,
        category_other
    ]

    db.session.add_all(categories)

    # IDs werden erzeugt, ohne die Transaktion
    # bereits vollständig zu committen.
    db.session.flush()

    #
    # Geräte
    #

    devices = [
        Device(
            name="MacBook Pro 14",
            serial_number="AT-NB-001",
            location="Büro Zürich",
            purchase_date=date.today() - timedelta(days=420),
            status="available",
            category_id=category_notebook.id,
            created_by=current_user.id
        ),

        Device(
            name="Dell Latitude 7440",
            serial_number="AT-NB-002",
            location="Büro Zürich",
            purchase_date=date.today() - timedelta(days=310),
            status="in_use",
            category_id=category_notebook.id,
            created_by=current_user.id
        ),

        Device(
            name="Lenovo ThinkPad T14",
            serial_number="AT-NB-003",
            location="Werkstatt",
            purchase_date=date.today() - timedelta(days=610),
            status="maintenance",
            category_id=category_notebook.id,
            created_by=current_user.id
        ),

        Device(
            name="Proxmox Node 01",
            serial_number="AT-SRV-001",
            location="Serverraum",
            purchase_date=date.today() - timedelta(days=900),
            status="available",
            category_id=category_server.id,
            created_by=current_user.id
        ),

        Device(
            name="Backup Server",
            serial_number="AT-SRV-002",
            location="Serverraum",
            purchase_date=date.today() - timedelta(days=720),
            status="available",
            category_id=category_server.id,
            created_by=current_user.id
        ),

        Device(
            name="UniFi Switch 24",
            serial_number="AT-NET-001",
            location="Serverraum",
            purchase_date=date.today() - timedelta(days=540),
            status="in_use",
            category_id=category_network.id,
            created_by=current_user.id
        ),

        Device(
            name="UniFi Access Point",
            serial_number="AT-NET-002",
            location="Büro Zürich",
            purchase_date=date.today() - timedelta(days=280),
            status="in_use",
            category_id=category_network.id,
            created_by=current_user.id
        ),

        Device(
            name="Fluke 117 Multimeter",
            serial_number="AT-MES-001",
            location="Werkstatt",
            purchase_date=date.today() - timedelta(days=800),
            status="available",
            category_id=category_measurement.id,
            created_by=current_user.id
        ),

        Device(
            name="Rigol Oszilloskop",
            serial_number="AT-MES-002",
            location="Elektroniklabor",
            purchase_date=date.today() - timedelta(days=460),
            status="defective",
            category_id=category_measurement.id,
            created_by=current_user.id
        ),

        Device(
            name="Bosch Akkuschrauber",
            serial_number="AT-TOOL-001",
            location="Werkstatt",
            purchase_date=date.today() - timedelta(days=380),
            status="available",
            category_id=category_tool.id,
            created_by=current_user.id
        ),

        Device(
            name="Wera Werkzeugkoffer",
            serial_number="AT-TOOL-002",
            location="Werkstatt",
            purchase_date=date.today() - timedelta(days=260),
            status="available",
            category_id=category_tool.id,
            created_by=current_user.id
        ),

        Device(
            name="Ersatzmonitor 27 Zoll",
            serial_number="AT-OTH-001",
            location="Lager",
            purchase_date=date.today() - timedelta(days=190),
            status="available",
            category_id=category_other.id,
            created_by=current_user.id
        )
    ]

    db.session.add_all(devices)
    db.session.flush()

    #
    # Wartungen
    #

    maintenance_entries = [
        Maintenance(
            device_id=devices[0].id,
            maintenance_date=date.today() - timedelta(days=45),
            description=(
                "Gerät gereinigt, Software aktualisiert "
                "und allgemeiner Funktionstest durchgeführt."
            ),
            cost=Decimal("85.00"),
            completed=True
        ),

        Maintenance(
            device_id=devices[2].id,
            maintenance_date=date.today() - timedelta(days=2),
            description=(
                "Akku zeigt stark reduzierte Kapazität. "
                "Ersatzakku wurde bestellt."
            ),
            cost=Decimal("149.90"),
            completed=False
        ),

        Maintenance(
            device_id=devices[3].id,
            maintenance_date=date.today() - timedelta(days=90),
            description=(
                "Lüfter und Kühlkörper gereinigt. "
                "System und Datenträger geprüft."
            ),
            cost=Decimal("120.00"),
            completed=True
        ),

        Maintenance(
            device_id=devices[5].id,
            maintenance_date=date.today() - timedelta(days=120),
            description=(
                "Firmware aktualisiert und alle Netzwerkports "
                "auf Funktion geprüft."
            ),
            cost=Decimal("60.00"),
            completed=True
        ),

        Maintenance(
            device_id=devices[7].id,
            maintenance_date=date.today() - timedelta(days=180),
            description=(
                "Messleitungen ersetzt und Funktionstest "
                "durchgeführt."
            ),
            cost=Decimal("45.50"),
            completed=True
        ),

        Maintenance(
            device_id=devices[8].id,
            maintenance_date=date.today() - timedelta(days=1),
            description=(
                "Gerät zeigt sporadische Ausfälle am Eingangskanal. "
                "Fehleranalyse erforderlich."
            ),
            cost=Decimal("0.00"),
            completed=False
        ),

        Maintenance(
            device_id=devices[9].id,
            maintenance_date=date.today() - timedelta(days=75),
            description=(
                "Bohrfutter geprüft und Gerät gereinigt."
            ),
            cost=Decimal("35.00"),
            completed=True
        )
    ]

    db.session.add_all(
        maintenance_entries
    )

    db.session.commit()

    flash(
        "Demo-Daten wurden erfolgreich erstellt: "
        "6 Kategorien, 12 Geräte und 7 Wartungen.",
        "success"
    )

    return redirect(
        url_for("system.index")
    )


@system.route("/reset", methods=["POST"])
@login_required
def reset():
    confirmation = request.form.get(
        "confirmation",
        ""
    ).strip()

    if confirmation != "RESET":
        flash(
            "Zur Bestätigung muss RESET eingegeben werden.",
            "error"
        )

        return redirect(
            url_for("system.index")
        )

    #
    # Reihenfolge beachten:
    #
    # Wartungen hängen von Geräten ab.
    # Geräte hängen von Kategorien und Benutzern ab.
    #

    Maintenance.query.delete()
    Device.query.delete()
    Category.query.delete()

    db.session.commit()

    flash(
        "Alle Geräte, Wartungen und Kategorien "
        "wurden gelöscht. Benutzerkonten bleiben bestehen.",
        "success"
    )

    return redirect(
        url_for("system.index")
    )