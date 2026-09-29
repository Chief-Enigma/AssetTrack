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
from app.models import Category


categories = Blueprint("categories", __name__)


@categories.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()

        if not name:
            flash(
                "Bitte einen Kategorienamen eingeben.",
                "error"
            )

            return redirect(
                url_for("categories.index")
            )

        existing = Category.query.filter(
            db.func.lower(Category.name) == name.lower()
        ).first()

        if existing:
            flash(
                "Diese Kategorie existiert bereits.",
                "error"
            )

            return redirect(
                url_for("categories.index")
            )

        category = Category(name=name)

        db.session.add(category)
        db.session.commit()

        flash(
            f"Kategorie „{category.name}“ wurde erstellt.",
            "success"
        )

        return redirect(
            url_for("categories.index")
        )

    category_list = (
        Category.query
        .order_by(Category.name.asc())
        .all()
    )

    return render_template(
        "categories/index.html",
        categories=category_list
    )


@categories.route("/<int:category_id>/delete", methods=["POST"])
@login_required
def delete(category_id):
    category = db.get_or_404(
        Category,
        category_id
    )

    if category.devices:
        flash(
            "Die Kategorie kann nicht gelöscht werden, "
            "solange ihr Geräte zugeordnet sind.",
            "error"
        )

        return redirect(
            url_for("categories.index")
        )

    name = category.name

    db.session.delete(category)
    db.session.commit()

    flash(
        f"Kategorie „{name}“ wurde gelöscht.",
        "success"
    )

    return redirect(
        url_for("categories.index")
    )