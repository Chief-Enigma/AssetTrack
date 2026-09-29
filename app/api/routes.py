from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from app.models import User, Device, Category


api = Blueprint("api", __name__)


def device_to_dict(device):
    return {
        "id": device.id,
        "name": device.name,
        "serial_number": device.serial_number,
        "location": device.location,
        "purchase_date": (
            device.purchase_date.isoformat()
            if device.purchase_date
            else None
        ),
        "status": device.status,
        "status_label": device.status_label,
        "category": {
            "id": device.category.id,
            "name": device.category.name
        },
        "created_by": {
            "id": device.creator.id,
            "username": device.creator.username
        },
        "created_at": device.created_at.isoformat()
    }


def maintenance_to_dict(entry):
    return {
        "id": entry.id,
        "device_id": entry.device_id,
        "maintenance_date": entry.maintenance_date.isoformat(),
        "description": entry.description,
        "cost": float(entry.cost),
        "completed": entry.completed,
        "created_at": entry.created_at.isoformat()
    }


@api.route("/status")
def status():
    return jsonify({
        "status": "ok",
        "application": "AssetTrack",
        "api": "v1"
    })


@api.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON body required"
        }), 400

    username = str(
        data.get("username", "")
    ).strip()

    password = str(
        data.get("password", "")
    )

    if not username or not password:
        return jsonify({
            "error": "Username and password are required"
        }), 400

    user = User.query.filter_by(
        username=username
    ).first()

    if user is None or not user.check_password(password):
        return jsonify({
            "error": "Invalid username or password"
        }), 401

    access_token = create_access_token(
        identity=str(user.id)
    )

    return jsonify({
        "access_token": access_token,
        "token_type": "Bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 200


@api.route("/devices", methods=["GET"])
@jwt_required()
def devices():
    current_user_id = get_jwt_identity()

    device_list = (
        Device.query
        .order_by(Device.name.asc())
        .all()
    )

    return jsonify({
        "authenticated_user_id": current_user_id,
        "count": len(device_list),
        "devices": [
            device_to_dict(device)
            for device in device_list
        ]
    }), 200


@api.route("/devices/<int:device_id>", methods=["GET"])
@jwt_required()
def device_detail(device_id):
    device = Device.query.get(device_id)

    if device is None:
        return jsonify({
            "error": "Device not found"
        }), 404

    return jsonify(
        device_to_dict(device)
    ), 200


@api.route("/categories", methods=["GET"])
@jwt_required()
def categories():
    category_list = (
        Category.query
        .order_by(Category.name.asc())
        .all()
    )

    return jsonify({
        "count": len(category_list),
        "categories": [
            {
                "id": category.id,
                "name": category.name,
                "device_count": len(category.devices)
            }
            for category in category_list
        ]
    }), 200


@api.route(
    "/devices/<int:device_id>/maintenance",
    methods=["GET"]
)
@jwt_required()
def device_maintenance(device_id):
    device = Device.query.get(device_id)

    if device is None:
        return jsonify({
            "error": "Device not found"
        }), 404

    entries = sorted(
        device.maintenance_entries,
        key=lambda entry: entry.maintenance_date,
        reverse=True
    )

    return jsonify({
        "device": {
            "id": device.id,
            "name": device.name,
            "serial_number": device.serial_number
        },
        "count": len(entries),
        "maintenance": [
            maintenance_to_dict(entry)
            for entry in entries
        ]
    }), 200