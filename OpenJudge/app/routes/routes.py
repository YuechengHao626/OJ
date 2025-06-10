# app/routes/routes.py
from flask import Blueprint, jsonify, request
from app.models.analysis_task import AnalysisTask  
from app.views import api
from app.utils.lab_validator import VALID_LABS, is_valid_lab
from datetime import datetime,timezone
from app.models import db
from app.models.analysis_task import AnalysisTask
from app.utils.time_convert import to_rfc3339_seconds_zulu
from .problems import problems



@api.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@api.route("/problems", methods=["GET"])
def get_all_problems():
    return jsonify([
        {
            "id": pid,
            "title": p["title"],
            "description": p["description"],
            "input": p["input"],
            "expected_output": p["expected_output"]
        }
        for pid, p in problems.items()
    ])

