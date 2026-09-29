from datetime import datetime, date

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
        index=True
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    devices = db.relationship(
        "Device",
        back_populates="creator",
        lazy=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    devices = db.relationship(
        "Device",
        back_populates="category",
        lazy=True
    )

    def __repr__(self):
        return f"<Category {self.name}>"


class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(120),
        nullable=False
    )

    serial_number = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True
    )

    location = db.Column(
        db.String(120),
        nullable=False
    )

    purchase_date = db.Column(
        db.Date,
        nullable=True
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="available"
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    category = db.relationship(
        "Category",
        back_populates="devices"
    )

    creator = db.relationship(
        "User",
        back_populates="devices"
    )

    maintenance_entries = db.relationship(
        "Maintenance",
        back_populates="device",
        cascade="all, delete-orphan",
        lazy=True
    )

    @property
    def status_label(self):
        labels = {
            "available": "Verfügbar",
            "in_use": "In Benutzung",
            "maintenance": "Wartung",
            "defective": "Defekt"
        }

        return labels.get(self.status, self.status)

    def can_be_used(self):
        return self.status not in ["defective", "maintenance"]

    def __repr__(self):
        return f"<Device {self.name} ({self.serial_number})>"


class Maintenance(db.Model):
    __tablename__ = "maintenance"

    id = db.Column(db.Integer, primary_key=True)

    device_id = db.Column(
        db.Integer,
        db.ForeignKey("devices.id"),
        nullable=False
    )

    maintenance_date = db.Column(
        db.Date,
        default=date.today,
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    cost = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0
    )

    completed = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    device = db.relationship(
        "Device",
        back_populates="maintenance_entries"
    )

    def __repr__(self):
        return f"<Maintenance Device={self.device_id}>"