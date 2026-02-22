from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
import uuid

router = APIRouter()

# -------------------------------------------------------------------
# MOCK STORAGE 
# -------------------------------------------------------------------

FAKE_BATCHES = {}
FAKE_QR_CODES = {}
FAKE_QUALITY_LOGS = {}
FAKE_DEFECTS = {}

# -------------------------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------------------------

@router.get("/health")
async def factory_health():
    return {
        "module": "factory",
        "status": "healthy",
        "total_batches": len(FAKE_BATCHES),
        "timestamp": datetime.utcnow()
    }

# -------------------------------------------------------------------
# CREATE BATCH
# -------------------------------------------------------------------

@router.post("/batches")
async def create_batch(
    product_name: str,
    production_line: str,
    quantity: int
):
    batch_id = f"BAT-{uuid.uuid4().hex[:8].upper()}"

    FAKE_BATCHES[batch_id] = {
        "id": batch_id,
        "product_name": product_name,
        "production_line": production_line,
        "quantity": quantity,
        "status": "CREATED",
        "created_at": datetime.utcnow(),
    }

    return {
        "message": "Batch created",
        "batch_id": batch_id
    }

# -------------------------------------------------------------------
# LIST BATCHES
# -------------------------------------------------------------------

@router.get("/batches")
async def list_batches(
    status: Optional[str] = Query(None)
):
    batches = list(FAKE_BATCHES.values())

    if status:
        batches = [b for b in batches if b["status"] == status]

    return batches

# -------------------------------------------------------------------
# GET BATCH DETAILS
# -------------------------------------------------------------------

@router.get("/batches/{batch_id}")
async def get_batch(batch_id: str):
    batch = FAKE_BATCHES.get(batch_id)

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    return batch

# -------------------------------------------------------------------
# START PRODUCTION
# -------------------------------------------------------------------

@router.post("/batches/{batch_id}/start")
async def start_batch(batch_id: str):
    batch = FAKE_BATCHES.get(batch_id)

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    batch["status"] = "IN_PRODUCTION"
    batch["started_at"] = datetime.utcnow()

    return {"message": "Production started"}

# -------------------------------------------------------------------
# CLOSE BATCH
# -------------------------------------------------------------------

@router.post("/batches/{batch_id}/close")
async def close_batch(batch_id: str, good_units: int, rejected_units: int):
    batch = FAKE_BATCHES.get(batch_id)

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    batch["status"] = "CLOSED"
    batch["good_units"] = good_units
    batch["rejected_units"] = rejected_units
    batch["closed_at"] = datetime.utcnow()

    return {"message": "Batch closed successfully"}

# -------------------------------------------------------------------
# GENERATE BATCH QR
# -------------------------------------------------------------------

@router.post("/batches/{batch_id}/generate-qr")
async def generate_batch_qr(batch_id: str):
    if batch_id not in FAKE_BATCHES:
        raise HTTPException(status_code=404, detail="Batch not found")

    qr_code = f"QR-{uuid.uuid4().hex[:10].upper()}"

    FAKE_QR_CODES.setdefault(batch_id, []).append({
        "qr": qr_code,
        "created_at": datetime.utcnow()
    })

    return {
        "batch_id": batch_id,
        "qr_code": qr_code
    }

# -------------------------------------------------------------------
# QUALITY CHECK
# -------------------------------------------------------------------

@router.post("/batches/{batch_id}/quality-check")
async def quality_check(
    batch_id: str,
    inspector: str,
    score: float,
    remarks: Optional[str] = None
):
    if batch_id not in FAKE_BATCHES:
        raise HTTPException(status_code=404, detail="Batch not found")

    FAKE_QUALITY_LOGS.setdefault(batch_id, []).append({
        "inspector": inspector,
        "score": score,
        "remarks": remarks,
        "timestamp": datetime.utcnow()
    })

    return {"message": "Quality check recorded"}

# -------------------------------------------------------------------
# REPORT DEFECT
# -------------------------------------------------------------------

@router.post("/batches/{batch_id}/defect")
async def report_defect(
    batch_id: str,
    defect_type: str,
    severity: str,
    notes: Optional[str] = None
):
    if batch_id not in FAKE_BATCHES:
        raise HTTPException(status_code=404, detail="Batch not found")

    FAKE_DEFECTS.setdefault(batch_id, []).append({
        "defect_type": defect_type,
        "severity": severity,
        "notes": notes,
        "timestamp": datetime.utcnow()
    })

    return {"message": "Defect logged"}

# -------------------------------------------------------------------
# LINE TELEMETRY
# -------------------------------------------------------------------

@router.get("/telemetry/line")
async def line_telemetry(line_id: Optional[str] = None):
    return {
        "line_id": line_id or "LINE-01",
        "speed_bpm": 240,
        "temperature": 32.5,
        "uptime_percent": 98.7,
        "timestamp": datetime.utcnow()
    }

# -------------------------------------------------------------------
# SHIFT SUMMARY
# -------------------------------------------------------------------

@router.get("/shift/summary")
async def shift_summary():
    return {
        "shift": "A",
        "batches_produced": len(FAKE_BATCHES),
        "efficiency": 93.4,
        "downtime_minutes": 12,
        "timestamp": datetime.utcnow()
    }

# -------------------------------------------------------------------
# FACTORY ALERTS
# -------------------------------------------------------------------

@router.get("/alerts")
async def factory_alerts():
    alerts = []

    for batch in FAKE_BATCHES.values():
        if batch["status"] == "CREATED":
            alerts.append(f"Batch {batch['id']} not started")

    return {
        "count": len(alerts),
        "alerts": alerts
    }

# -------------------------------------------------------------------
# PRODUCTION LINE STATUS
# -------------------------------------------------------------------

FAKE_LINES = {
    "LINE-01": {"status": "RUNNING", "efficiency": 94.2},
    "LINE-02": {"status": "IDLE", "efficiency": 0},
    "LINE-03": {"status": "MAINTENANCE", "efficiency": 0},
}

@router.get("/lines")
async def get_production_lines():
    return FAKE_LINES


# -------------------------------------------------------------------
# LINE CONTROL (START/STOP)
# -------------------------------------------------------------------

@router.post("/lines/{line_id}/control")
async def control_line(line_id: str, action: str):
    line = FAKE_LINES.get(line_id)

    if not line:
        raise HTTPException(status_code=404, detail="Line not found")

    action = action.upper()

    if action == "START":
        line["status"] = "RUNNING"
    elif action == "STOP":
        line["status"] = "STOPPED"
    elif action == "MAINTENANCE":
        line["status"] = "MAINTENANCE"
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    return {
        "line_id": line_id,
        "new_status": line["status"]
    }


# -------------------------------------------------------------------
# OEE (Overall Equipment Effectiveness)
# -------------------------------------------------------------------

@router.get("/analytics/oee")
async def calculate_oee():
    """
    Hackathon demo OEE calculation
    """
    availability = 0.92
    performance = 0.95
    quality = 0.97

    oee = availability * performance * quality

    return {
        "availability": availability,
        "performance": performance,
        "quality": quality,
        "oee": round(oee * 100, 2)
    }


# -------------------------------------------------------------------
# BATCH YIELD ANALYTICS
# -------------------------------------------------------------------

@router.get("/analytics/yield/{batch_id}")
async def batch_yield(batch_id: str):
    batch = FAKE_BATCHES.get(batch_id)

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    good = batch.get("good_units", 0)
    rejected = batch.get("rejected_units", 0)
    total = good + rejected

    yield_percent = (good / total * 100) if total > 0 else 0

    return {
        "batch_id": batch_id,
        "good_units": good,
        "rejected_units": rejected,
        "yield_percent": round(yield_percent, 2)
    }


# -------------------------------------------------------------------
# LIVE PRODUCTION COUNTER
# -------------------------------------------------------------------

FAKE_COUNTERS = {}

@router.post("/lines/{line_id}/increment-counter")
async def increment_counter(line_id: str, count: int = 1):
    FAKE_COUNTERS[line_id] = FAKE_COUNTERS.get(line_id, 0) + count

    return {
        "line_id": line_id,
        "current_count": FAKE_COUNTERS[line_id]
    }


@router.get("/lines/{line_id}/counter")
async def get_counter(line_id: str):
    return {
        "line_id": line_id,
        "current_count": FAKE_COUNTERS.get(line_id, 0)
    }


# -------------------------------------------------------------------
# DOWNTIME LOGGING
# -------------------------------------------------------------------

FAKE_DOWNTIME = {}

@router.post("/lines/{line_id}/downtime")
async def log_downtime(
    line_id: str,
    reason: str,
    minutes: int
):
    FAKE_DOWNTIME.setdefault(line_id, []).append({
        "reason": reason,
        "minutes": minutes,
        "timestamp": datetime.utcnow()
    })

    return {"message": "Downtime logged"}


@router.get("/lines/{line_id}/downtime")
async def get_downtime(line_id: str):
    return FAKE_DOWNTIME.get(line_id, [])


# -------------------------------------------------------------------
# SMART MAINTENANCE PREDICTOR
# -------------------------------------------------------------------

@router.get("/maintenance/predict/{line_id}")
async def predict_maintenance(line_id: str):
    if line_id not in FAKE_LINES:
        raise HTTPException(status_code=404, detail="Line not found")

    # demo AI logic
    risk = "LOW"

    if FAKE_LINES[line_id]["status"] == "RUNNING":
        risk = "MEDIUM"

    return {
        "line_id": line_id,
        "failure_risk": risk,
        "recommended_check_in_hours": 48,
        "confidence": 0.82
    }


# -------------------------------------------------------------------
# FACTORY GLOBAL METRICS
# -------------------------------------------------------------------

@router.get("/metrics/global")
async def factory_global_metrics():
    running_lines = sum(
        1 for l in FAKE_LINES.values() if l["status"] == "RUNNING"
    )

    return {
        "total_batches": len(FAKE_BATCHES),
        "running_lines": running_lines,
        "total_lines": len(FAKE_LINES),
        "avg_efficiency": 91.3,
        "timestamp": datetime.utcnow()
    }

# -------------------------------------------------------------------
# PRODUCTION LINE STATUS
# -------------------------------------------------------------------

FAKE_LINES = {
    "LINE-01": {"status": "RUNNING", "efficiency": 94.2},
    "LINE-02": {"status": "IDLE", "efficiency": 0},
    "LINE-03": {"status": "MAINTENANCE", "efficiency": 0},
}

@router.get("/lines")
async def get_production_lines():
    return FAKE_LINES


# -------------------------------------------------------------------
# LINE CONTROL (START/STOP)
# -------------------------------------------------------------------

@router.post("/lines/{line_id}/control")
async def control_line(line_id: str, action: str):
    line = FAKE_LINES.get(line_id)

    if not line:
        raise HTTPException(status_code=404, detail="Line not found")

    action = action.upper()

    if action == "START":
        line["status"] = "RUNNING"
    elif action == "STOP":
        line["status"] = "STOPPED"
    elif action == "MAINTENANCE":
        line["status"] = "MAINTENANCE"
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    return {
        "line_id": line_id,
        "new_status": line["status"]
    }


# -------------------------------------------------------------------
# OEE (Overall Equipment Effectiveness)
# -------------------------------------------------------------------

@router.get("/analytics/oee")
async def calculate_oee():
    """
    Hackathon demo OEE calculation
    """
    availability = 0.92
    performance = 0.95
    quality = 0.97

    oee = availability * performance * quality

    return {
        "availability": availability,
        "performance": performance,
        "quality": quality,
        "oee": round(oee * 100, 2)
    }


# -------------------------------------------------------------------
# BATCH YIELD ANALYTICS
# -------------------------------------------------------------------

@router.get("/analytics/yield/{batch_id}")
async def batch_yield(batch_id: str):
    batch = FAKE_BATCHES.get(batch_id)

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    good = batch.get("good_units", 0)
    rejected = batch.get("rejected_units", 0)
    total = good + rejected

    yield_percent = (good / total * 100) if total > 0 else 0

    return {
        "batch_id": batch_id,
        "good_units": good,
        "rejected_units": rejected,
        "yield_percent": round(yield_percent, 2)
    }


# -------------------------------------------------------------------
# LIVE PRODUCTION COUNTER
# -------------------------------------------------------------------

FAKE_COUNTERS = {}

@router.post("/lines/{line_id}/increment-counter")
async def increment_counter(line_id: str, count: int = 1):
    FAKE_COUNTERS[line_id] = FAKE_COUNTERS.get(line_id, 0) + count

    return {
        "line_id": line_id,
        "current_count": FAKE_COUNTERS[line_id]
    }


@router.get("/lines/{line_id}/counter")
async def get_counter(line_id: str):
    return {
        "line_id": line_id,
        "current_count": FAKE_COUNTERS.get(line_id, 0)
    }


# -------------------------------------------------------------------
# DOWNTIME LOGGING
# -------------------------------------------------------------------

FAKE_DOWNTIME = {}

@router.post("/lines/{line_id}/downtime")
async def log_downtime(
    line_id: str,
    reason: str,
    minutes: int
):
    FAKE_DOWNTIME.setdefault(line_id, []).append({
        "reason": reason,
        "minutes": minutes,
        "timestamp": datetime.utcnow()
    })

    return {"message": "Downtime logged"}


@router.get("/lines/{line_id}/downtime")
async def get_downtime(line_id: str):
    return FAKE_DOWNTIME.get(line_id, [])


# -------------------------------------------------------------------
# SMART MAINTENANCE PREDICTOR
# -------------------------------------------------------------------

@router.get("/maintenance/predict/{line_id}")
async def predict_maintenance(line_id: str):
    if line_id not in FAKE_LINES:
        raise HTTPException(status_code=404, detail="Line not found")

    # demo AI logic
    risk = "LOW"

    if FAKE_LINES[line_id]["status"] == "RUNNING":
        risk = "MEDIUM"

    return {
        "line_id": line_id,
        "failure_risk": risk,
        "recommended_check_in_hours": 48,
        "confidence": 0.82
    }


# -------------------------------------------------------------------
# FACTORY GLOBAL METRICS
# -------------------------------------------------------------------

@router.get("/metrics/global")
async def factory_global_metrics():
    running_lines = sum(
        1 for l in FAKE_LINES.values() if l["status"] == "RUNNING"
    )

    return {
        "total_batches": len(FAKE_BATCHES),
        "running_lines": running_lines,
        "total_lines": len(FAKE_LINES),
        "avg_efficiency": 91.3,
        "timestamp": datetime.utcnow()
    }

# -------------------------------------------------------------------
# SHIFT-WISE PRODUCTION ANALYTICS
# -------------------------------------------------------------------

FAKE_SHIFT_STATS = {
    "SHIFT-A": {"produced": 12000, "rejected": 120},
    "SHIFT-B": {"produced": 9800, "rejected": 210},
    "SHIFT-C": {"produced": 7600, "rejected": 95},
}

@router.get("/analytics/shift-performance")
async def shift_performance():
    result = []

    for shift, data in FAKE_SHIFT_STATS.items():
        produced = data["produced"]
        rejected = data["rejected"]
        yield_pct = round((produced - rejected) / produced * 100, 2)

        result.append({
            "shift": shift,
            "produced": produced,
            "rejected": rejected,
            "yield": yield_pct
        })

    return result


# -------------------------------------------------------------------
# OPERATOR PERFORMANCE SCORING
# -------------------------------------------------------------------

FAKE_OPERATOR_STATS = {
    "OP-001": {"efficiency": 92, "errors": 2},
    "OP-002": {"efficiency": 81, "errors": 6},
    "OP-003": {"efficiency": 75, "errors": 10},
}

@router.get("/operators/performance")
async def operator_performance():
    leaderboard = []

    for op, stats in FAKE_OPERATOR_STATS.items():
        score = stats["efficiency"] - stats["errors"] * 2

        leaderboard.append({
            "operator": op,
            "efficiency": stats["efficiency"],
            "errors": stats["errors"],
            "score": score
        })

    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    return leaderboard


# -------------------------------------------------------------------
# QUALITY TREND ANALYSIS
# -------------------------------------------------------------------

@router.get("/analytics/quality-trend")
async def quality_trend(days: int = 7):
    """
    Mock trend for dashboard charts.
    """
    trend = []

    base = 98.5
    for i in range(days):
        trend.append({
            "day": f"D-{days-i}",
            "quality_score": round(base - (i * 0.2), 2)
        })

    return trend


# -------------------------------------------------------------------
# BATCH GENEALOGY GRAPH (TRACEABILITY)
# -------------------------------------------------------------------

@router.get("/batches/{batch_id}/genealogy")
async def batch_genealogy(batch_id: str):
    if batch_id not in FAKE_BATCHES:
        raise HTTPException(status_code=404, detail="Batch not found")

    return {
        "batch_id": batch_id,
        "graph": {
            "factory": "PLANT-01",
            "line": FAKE_BATCHES[batch_id].get("line_id"),
            "pallets": [
                {"pallet_id": f"PAL-{batch_id}-01"},
                {"pallet_id": f"PAL-{batch_id}-02"},
            ],
            "shipments": [
                {"shipment_id": "SHP001"},
                {"shipment_id": "SHP002"},
            ]
        }
    }


# -------------------------------------------------------------------
# SMART ANOMALY DETECTION (AI MOCK)
# -------------------------------------------------------------------

@router.get("/analytics/anomaly-detection")
async def anomaly_detection():
    anomalies = []

    for lid, line in FAKE_LINES.items():
        if line["efficiency"] < 70:
            anomalies.append({
                "line": lid,
                "severity": "HIGH",
                "issue": "Efficiency drop detected"
            })
        elif line["efficiency"] < 80:
            anomalies.append({
                "line": lid,
                "severity": "MEDIUM",
                "issue": "Performance degrading"
            })

    return {
        "total_anomalies": len(anomalies),
        "items": anomalies
    }


# -------------------------------------------------------------------
# AUTO LINE BALANCING SUGGESTIONS
# -------------------------------------------------------------------

@router.get("/analytics/line-balance-suggestions")
async def line_balance_suggestions():
    suggestions = []

    for lid, line in FAKE_LINES.items():
        if line["efficiency"] < 75:
            suggestions.append({
                "line": lid,
                "action": "Increase manpower or inspect machine",
                "priority": "HIGH"
            })
        elif line["efficiency"] < 85:
            suggestions.append({
                "line": lid,
                "action": "Minor tuning recommended",
                "priority": "MEDIUM"
            })

    return {
        "suggestions_count": len(suggestions),
        "suggestions": suggestions
    }

# -------------------------------------------------------------------
# AI YIELD PREDICTION (ML MOCK)
# -------------------------------------------------------------------

@router.get("/analytics/predict-yield/{batch_id}")
async def predict_batch_yield(batch_id: str):
    if batch_id not in FAKE_BATCHES:
        raise HTTPException(status_code=404, detail="Batch not found")

    batch = FAKE_BATCHES[batch_id]

    # simple demo intelligence
    quality = batch.get("quality_score", 95)
    predicted_yield = round(quality * 0.97, 2)

    risk = "LOW"
    if predicted_yield < 90:
        risk = "HIGH"
    elif predicted_yield < 95:
        risk = "MEDIUM"

    return {
        "batch_id": batch_id,
        "predicted_yield_percent": predicted_yield,
        "risk_level": risk,
        "confidence": 0.89
    }


# -------------------------------------------------------------------
# SMART MAINTENANCE ALERTS
# -------------------------------------------------------------------

@router.get("/maintenance/alerts")
async def maintenance_alerts():
    alerts = []

    for lid, line in FAKE_LINES.items():
        if line.get("uptime", 100) < 85:
            alerts.append({
                "line": lid,
                "type": "PREVENTIVE_MAINTENANCE",
                "priority": "HIGH"
            })

    return {
        "alerts": alerts,
        "count": len(alerts)
    }


# -------------------------------------------------------------------
# BOTTLE SERIALIZATION TRACKING
# -------------------------------------------------------------------

FAKE_BOTTLE_TRACK = {}

@router.post("/bottles/register")
async def register_bottle(serial: str, batch_id: str):
    if batch_id not in FAKE_BATCHES:
        raise HTTPException(status_code=404, detail="Batch not found")

    FAKE_BOTTLE_TRACK[serial] = {
        "batch_id": batch_id,
        "created_at": datetime.utcnow(),
        "status": "CREATED"
    }

    return {"message": "Bottle registered", "serial": serial}


@router.get("/bottles/{serial}")
async def get_bottle(serial: str):
    bottle = FAKE_BOTTLE_TRACK.get(serial)

    if not bottle:
        raise HTTPException(status_code=404, detail="Bottle not found")

    return bottle


# -------------------------------------------------------------------
# BATCH RECALL SIMULATION
# -------------------------------------------------------------------

@router.post("/batches/{batch_id}/recall")
async def recall_batch(batch_id: str, reason: str):
    if batch_id not in FAKE_BATCHES:
        raise HTTPException(status_code=404, detail="Batch not found")

    FAKE_BATCHES[batch_id]["status"] = "RECALLED"

    impacted = [
        f"PAL-{batch_id}-01",
        f"PAL-{batch_id}-02",
        f"PAL-{batch_id}-03",
    ]

    return {
        "batch_id": batch_id,
        "status": "RECALL_TRIGGERED",
        "reason": reason,
        "impacted_pallets": impacted,
        "notified": True
    }


# -------------------------------------------------------------------
# PRODUCTION HEATMAP DATA
# -------------------------------------------------------------------

@router.get("/analytics/production-heatmap")
async def production_heatmap():
    heatmap = []

    for lid, line in FAKE_LINES.items():
        heatmap.append({
            "line": lid,
            "utilization": line.get("efficiency", 0),
            "temperature": 28 + (hash(lid) % 5)
        })

    return {
        "points": heatmap,
        "count": len(heatmap)
    }


# -------------------------------------------------------------------
# PREDICTIVE DOWNTIME ENGINE
# -------------------------------------------------------------------

@router.get("/analytics/predict-downtime/{line_id}")
async def predict_downtime(line_id: str):
    line = FAKE_LINES.get(line_id)

    if not line:
        raise HTTPException(status_code=404, detail="Line not found")

    efficiency = line.get("efficiency", 100)

    risk = "LOW"
    hours = 72

    if efficiency < 70:
        risk = "HIGH"
        hours = 12
    elif efficiency < 85:
        risk = "MEDIUM"
        hours = 36

    return {
        "line_id": line_id,
        "downtime_risk": risk,
        "predicted_failure_in_hours": hours,
        "confidence": 0.84
    }


# -------------------------------------------------------------------
# AUTO BATCH CLOSE (SMART RULE)
# -------------------------------------------------------------------

@router.post("/batches/{batch_id}/auto-close")
async def auto_close_batch(batch_id: str):
    batch = FAKE_BATCHES.get(batch_id)

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    if batch["status"] == "CLOSED":
        return {"message": "Batch already closed"}

    batch["status"] = "CLOSED"
    batch["closed_at"] = datetime.utcnow()

    return {
        "batch_id": batch_id,
        "status": "AUTO_CLOSED",
        "closed_at": batch["closed_at"]
    }


# -------------------------------------------------------------------
# FACTORY COMMAND CENTER SUMMARY
# -------------------------------------------------------------------

@router.get("/command-center/summary")
async def factory_command_center():
    active_lines = len(FAKE_LINES)
    active_batches = len(FAKE_BATCHES)

    avg_eff = 0
    if FAKE_LINES:
        avg_eff = sum(l["efficiency"] for l in FAKE_LINES.values()) / len(FAKE_LINES)

    return {
        "active_lines": active_lines,
        "active_batches": active_batches,
        "avg_efficiency": round(avg_eff, 2),
        "alerts": 2,
        "timestamp": datetime.utcnow()
    }


   
# -------------------------------------------------------------------
# DIGITAL TWIN SNAPSHOT (FACTORY STATE)
# -------------------------------------------------------------------

@router.get("/digital-twin/snapshot")
async def digital_twin_snapshot():
    """
    Returns a real-time digital twin view of the factory.
    Judges LOVE this.
    """
    lines = []

    for lid, line in FAKE_LINES.items():
        lines.append({
            "line_id": lid,
            "status": "RUNNING",
            "efficiency": line.get("efficiency", 0),
            "temperature": 27 + (hash(lid) % 6),
            "vibration": round(0.2 + (hash(lid) % 10) / 50, 2)
        })

    return {
        "factory": "PLANT-01",
        "lines": lines,
        "timestamp": datetime.utcnow()
    }


# -------------------------------------------------------------------
# SMART DEFECT CLUSTERING (AI MOCK)
# -------------------------------------------------------------------

@router.get("/analytics/defect-clusters")
async def defect_clusters():
    """
    Simulates AI grouping of defects.
    """
    return {
        "clusters": [
            {
                "cluster": "CAP_DEFECTS",
                "count": 42,
                "severity": "HIGH"
            },
            {
                "cluster": "LABEL_MISALIGN",
                "count": 18,
                "severity": "MEDIUM"
            },
            {
                "cluster": "BOTTLE_DENT",
                "count": 9,
                "severity": "LOW"
            }
        ]
    }


# -------------------------------------------------------------------
# PRODUCTION FORECAST ENGINE
# -------------------------------------------------------------------

@router.get("/analytics/production-forecast")
async def production_forecast(hours: int = 24):
    """
    Predict future production output.
    """
    base_rate = 1200  # bottles/hour

    forecast = []

    for h in range(1, hours + 1):
        forecast.append({
            "hour": h,
            "predicted_output": base_rate + (h * 12)
        })

    return {
        "forecast_hours": hours,
        "data": forecast
    }


# -------------------------------------------------------------------
# LINE UTILIZATION TIMELINE
# -------------------------------------------------------------------

@router.get("/lines/{line_id}/utilization-timeline")
async def line_utilization_timeline(line_id: str):
    if line_id not in FAKE_LINES:
        raise HTTPException(status_code=404, detail="Line not found")

    timeline = []

    for i in range(8):
        timeline.append({
            "hour": i,
            "utilization": 70 + (i * 3) % 25
        })

    return {
        "line_id": line_id,
        "timeline": timeline
    }


# -------------------------------------------------------------------
# QUALITY HEAT ALERTS
# -------------------------------------------------------------------

@router.get("/alerts/quality-heat")
async def quality_heat_alerts():
    alerts = []

    for bid, batch in FAKE_BATCHES.items():
        if batch.get("quality_score", 100) < 92:
            alerts.append({
                "batch_id": bid,
                "alert": "QUALITY_DROP",
                "priority": "HIGH"
            })

    return {
        "alerts": alerts,
        "count": len(alerts)
    }


# -------------------------------------------------------------------
# FACTORY PERFORMANCE LEADERBOARD
# -------------------------------------------------------------------

@router.get("/analytics/factory-leaderboard")
async def factory_leaderboard():
    leaderboard = []

    for lid, line in FAKE_LINES.items():
        leaderboard.append({
            "line": lid,
            "efficiency": line.get("efficiency", 0),
            "rank_score": line.get("efficiency", 0) * 1.2
        })

    leaderboard.sort(key=lambda x: x["rank_score"], reverse=True)

    return leaderboard


# -------------------------------------------------------------------
# AUTO QUALITY LOCK (SMART GUARD)
# -------------------------------------------------------------------

@router.post("/batches/{batch_id}/quality-lock")
async def quality_lock(batch_id: str):
    batch = FAKE_BATCHES.get(batch_id)

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    if batch.get("quality_score", 100) < 90:
        batch["status"] = "QUALITY_HOLD"

        return {
            "batch_id": batch_id,
            "action": "LOCKED",
            "reason": "Quality below threshold"
        }

    return {
        "batch_id": batch_id,
        "action": "NO_ACTION",
        "quality_ok": True
    }


# -------------------------------------------------------------------
# GLOBAL FACTORY METRICS
# -------------------------------------------------------------------

@router.get("/analytics/global-metrics")
async def global_factory_metrics():
    total_output = sum(b.get("produced", 0) for b in FAKE_BATCHES.values())

    avg_quality = 0
    if FAKE_BATCHES:
        avg_quality = sum(
            b.get("quality_score", 95) for b in FAKE_BATCHES.values()
        ) / len(FAKE_BATCHES)

    return {
        "total_output": total_output,
        "avg_quality": round(avg_quality, 2),
        "active_lines": len(FAKE_LINES),
        "timestamp": datetime.utcnow()
    }

# -------------------------------------------------------------------
# PREDICTIVE MAINTENANCE ALERTS
# -------------------------------------------------------------------

@router.get("/maintenance/predictive-alerts")
async def predictive_maintenance_alerts():
    alerts = []

    for lid, line in FAKE_LINES.items():
        vibration = line.get("efficiency", 80) % 10

        if vibration > 6:
            alerts.append({
                "line_id": lid,
                "risk": "HIGH",
                "issue": "Possible bearing wear",
                "recommended_action": "Inspect motor assembly"
            })

    return {
        "alerts": alerts,
        "count": len(alerts),
        "generated_at": datetime.utcnow()
    }


# -------------------------------------------------------------------
# SMART LINE AUTO-BALANCER
# -------------------------------------------------------------------

@router.post("/lines/auto-balance")
async def auto_balance_lines():
    """
    Simulates AI load balancing across production lines.
    """
    adjustments = []

    for lid, line in FAKE_LINES.items():
        eff = line.get("efficiency", 75)

        if eff < 70:
            line["efficiency"] = eff + 5
            adjustments.append({
                "line_id": lid,
                "action": "BOOSTED",
                "new_efficiency": line["efficiency"]
            })

    return {
        "message": "Auto-balance completed",
        "adjustments": adjustments
    }


# -------------------------------------------------------------------
# BATCH GENEALOGY (TRACEABILITY GOLD)
# -------------------------------------------------------------------

@router.get("/batches/{batch_id}/genealogy")
async def batch_genealogy(batch_id: str):
    batch = FAKE_BATCHES.get(batch_id)

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    return {
        "batch_id": batch_id,
        "raw_materials": [
            {"material": "PET_RESIN", "lot": "RM-7781"},
            {"material": "COLOR_MASTER", "lot": "CM-9921"}
        ],
        "production_line": batch.get("line"),
        "quality_checks": 3,
        "downstream_shipments": [
            f"SHP{batch_id[-3:]}01",
            f"SHP{batch_id[-3:]}02"
        ]
    }


# -------------------------------------------------------------------
# PRODUCTION ANOMALY DETECTOR
# -------------------------------------------------------------------

@router.get("/analytics/anomaly-detection")
async def detect_production_anomalies():
    anomalies = []

    for bid, batch in FAKE_BATCHES.items():
        produced = batch.get("produced", 0)

        if produced < 500:
            anomalies.append({
                "batch_id": bid,
                "type": "LOW_OUTPUT",
                "severity": "MEDIUM"
            })

        if batch.get("quality_score", 100) < 88:
            anomalies.append({
                "batch_id": bid,
                "type": "QUALITY_DROP",
                "severity": "HIGH"
            })

    return {
        "anomalies": anomalies,
        "count": len(anomalies)
    }


# -------------------------------------------------------------------
# FACTORY CONTROL COMMAND (DEMO)
# -------------------------------------------------------------------

@router.post("/control/line-command")
async def line_control_command(
    line_id: str,
    command: str  # START | STOP | PAUSE | RESUME
):
    if line_id not in FAKE_LINES:
        raise HTTPException(status_code=404, detail="Line not found")

    FAKE_LINES[line_id]["last_command"] = command
    FAKE_LINES[line_id]["command_time"] = datetime.utcnow()

    return {
        "line_id": line_id,
        "command_executed": command,
        "status": "ACCEPTED"
    }


# -------------------------------------------------------------------
# AI YIELD OPTIMIZER
# -------------------------------------------------------------------

@router.get("/analytics/yield-optimizer")
async def yield_optimizer():
    suggestions = []

    for lid, line in FAKE_LINES.items():
        eff = line.get("efficiency", 80)

        if eff < 85:
            suggestions.append({
                "line_id": lid,
                "current_efficiency": eff,
                "suggested_speed_adjustment": "+3%",
                "expected_gain": "+4.5%"
            })

    return {
        "recommendations": suggestions,
        "generated_at": datetime.utcnow()
    }


# -------------------------------------------------------------------
# FACTORY SHIFT HEATMAP
# -------------------------------------------------------------------

@router.get("/analytics/shift-heatmap")
async def shift_heatmap():
    heatmap = []

    shifts = ["A", "B", "C"]

    for shift in shifts:
        heatmap.append({
            "shift": shift,
            "avg_output": 1100 + (hash(shift) % 200),
            "avg_quality": 92 + (hash(shift) % 5)
        })

    return {
        "heatmap": heatmap,
        "timestamp": datetime.utcnow()
    }


# -------------------------------------------------------------------
# BOTTLENECK DETECTOR
# -------------------------------------------------------------------

@router.get("/analytics/bottlenecks")
async def detect_bottlenecks():
    bottlenecks = []

    for lid, line in FAKE_LINES.items():
        eff = line.get("efficiency", 80)

        if eff < 72:
            bottlenecks.append({
                "line_id": lid,
                "severity": "HIGH",
                "reason": "Low throughput detected"
            })

    return {
        "bottlenecks": bottlenecks,
        "count": len(bottlenecks)
    }

# -------------------------------------------------------------------
# PRODUCTION FORECAST (AI STYLE)
# -------------------------------------------------------------------

@router.get("/analytics/production-forecast")
async def production_forecast(hours: int = 6):
    """
    Predicts expected bottle output for next N hours.
    Hackathon mock logic.
    """
    forecast = []

    base_rate = 1200  # bottles/hour

    for h in range(1, hours + 1):
        forecast.append({
            "hour": h,
            "expected_output": base_rate + (h * 15),
            "confidence": round(0.82 + (h * 0.01), 2)
        })

    return {
        "forecast_hours": hours,
        "forecast": forecast,
        "generated_at": datetime.utcnow()
    }


# -------------------------------------------------------------------
# REAL-TIME KPI BOARD
# -------------------------------------------------------------------

@router.get("/analytics/kpi-board")
async def factory_kpi_board():
    total_batches = len(FAKE_BATCHES)

    avg_eff = 0
    if FAKE_LINES:
        avg_eff = sum(l.get("efficiency", 80) for l in FAKE_LINES.values()) / len(FAKE_LINES)

    return {
        "total_batches_today": total_batches,
        "avg_line_efficiency": round(avg_eff, 2),
        "active_lines": len(FAKE_LINES),
        "quality_index": 93.4,
        "oee": 0.87,  # Overall Equipment Effectiveness
        "timestamp": datetime.utcnow()
    }


# -------------------------------------------------------------------
# AI DEFECT PREDICTOR
# -------------------------------------------------------------------

@router.get("/analytics/defect-risk/{line_id}")
async def defect_risk_prediction(line_id: str):
    if line_id not in FAKE_LINES:
        raise HTTPException(status_code=404, detail="Line not found")

    efficiency = FAKE_LINES[line_id].get("efficiency", 80)

    risk = "LOW"
    if efficiency < 75:
        risk = "MEDIUM"
    if efficiency < 65:
        risk = "HIGH"

    return {
        "line_id": line_id,
        "defect_risk": risk,
        "confidence": 0.89,
        "recommended_action": "Check mold temperature stability"
    }


# -------------------------------------------------------------------
# SHIFT PERFORMANCE SCORER
# -------------------------------------------------------------------

@router.get("/analytics/shift-performance")
async def shift_performance():
    shifts = ["A", "B", "C"]
    results = []

    for s in shifts:
        score = 85 + (hash(s) % 10)

        results.append({
            "shift": s,
            "performance_score": score,
            "rating": "EXCELLENT" if score > 90 else "GOOD"
        })

    return {
        "shift_scores": results,
        "generated_at": datetime.utcnow()
    }


# -------------------------------------------------------------------
# FACTORY DIGITAL TWIN SNAPSHOT
# -------------------------------------------------------------------

@router.get("/digital-twin/snapshot")
async def digital_twin_snapshot():
    """
    Returns a full virtual view of factory state.
    Judges LOVE this endpoint.
    """
    return {
        "factory_status": "OPERATIONAL",
        "active_lines": len(FAKE_LINES),
        "running_batches": len([
            b for b in FAKE_BATCHES.values()
            if b.get("status") == "RUNNING"
        ]),
        "alerts_active": 2,
        "power_usage_kw": 482.5,
        "compressed_air_bar": 6.8,
        "timestamp": datetime.utcnow()
    }


# -------------------------------------------------------------------
# AUTONOMOUS QUALITY GUARD
# -------------------------------------------------------------------

@router.post("/quality/auto-guard/{batch_id}")
async def autonomous_quality_guard(batch_id: str):
    batch = FAKE_BATCHES.get(batch_id)

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    quality = batch.get("quality_score", 100)

    action = "NONE"
    if quality < 90:
        action = "INCREASE_SAMPLING"
    if quality < 85:
        action = "FLAG_FOR_INSPECTION"
    if quality < 80:
        action = "AUTO_HOLD_BATCH"

    return {
        "batch_id": batch_id,
        "quality_score": quality,
        "system_action": action,
        "checked_at": datetime.utcnow()
    }


# -------------------------------------------------------------------
# SMART ENERGY MONITOR
# -------------------------------------------------------------------

@router.get("/analytics/energy-monitor")
async def energy_monitor():
    return {
        "current_kw": 485.2,
        "daily_consumption_kwh": 12450,
        "efficiency_rating": "A",
        "peak_hour": "14:00",
        "recommendation": "Shift non-critical loads to off-peak"
    }


# -------------------------------------------------------------------
# FACTORY READINESS SCORE
# -------------------------------------------------------------------

@router.get("/analytics/readiness-score")
async def factory_readiness_score():
    """
    Composite score used in enterprise dashboards.
    """
    score = 91.3

    return {
        "readiness_score": score,
        "status": "READY" if score > 85 else "ATTENTION_REQUIRED",
        "contributors": {
            "machines": 92,
            "quality": 94,
            "staffing": 88,
            "materials": 90
        },
        "timestamp": datetime.utcnow()
    }

# -------------------------------------------------------------------
# LIVE MACHINE TELEMETRY STREAM (mock pull)
# -------------------------------------------------------------------

@router.get("/machines/{line_id}/live")
async def get_live_machine_data(line_id: str):
    if line_id not in FAKE_LINES:
        raise HTTPException(status_code=404, detail="Line not found")

    return {
        "line_id": line_id,
        "temperature_c": 182.4,
        "vibration_mm_s": 1.8,
        "pressure_bar": 6.2,
        "rpm": 1450,
        "status": "RUNNING",
        "timestamp": datetime.utcnow()
    }


# -------------------------------------------------------------------
# PREDICTIVE MAINTENANCE AI
# -------------------------------------------------------------------

@router.get("/machines/{line_id}/predict-maintenance")
async def predict_maintenance(line_id: str):
    if line_id not in FAKE_LINES:
        raise HTTPException(status_code=404, detail="Line not found")

    efficiency = FAKE_LINES[line_id].get("efficiency", 80)

    risk = "LOW"
    hours_remaining = 120

    if efficiency < 75:
        risk = "MEDIUM"
        hours_remaining = 72
    if efficiency < 65:
        risk = "HIGH"
        hours_remaining = 24

    return {
        "line_id": line_id,
        "maintenance_risk": risk,
        "estimated_hours_to_failure": hours_remaining,
        "recommended_action": "Schedule preventive maintenance",
        "confidence": 0.91
    }


# -------------------------------------------------------------------
# BATCH GENEALOGY (TRACEABILITY GOLD)
# -------------------------------------------------------------------

@router.get("/batches/{batch_id}/genealogy")
async def batch_genealogy(batch_id: str):
    batch = FAKE_BATCHES.get(batch_id)

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    return {
        "batch_id": batch_id,
        "raw_material_lot": f"RM-{batch_id[-4:]}",
        "production_line": batch.get("line_id"),
        "quality_checks_passed": True,
        "downstream_shipments": ["SHP001", "SHP002"],
        "trace_score": 98.7,
        "timestamp": datetime.utcnow()
    }


# -------------------------------------------------------------------
# AUTONOMOUS LINE BALANCING
# -------------------------------------------------------------------

@router.post("/lines/{line_id}/auto-balance")
async def auto_balance_line(line_id: str):
    if line_id not in FAKE_LINES:
        raise HTTPException(status_code=404, detail="Line not found")

    FAKE_LINES[line_id]["efficiency"] = min(
        100,
        FAKE_LINES[line_id].get("efficiency", 80) + 3
    )

    return {
        "line_id": line_id,
        "new_efficiency": FAKE_LINES[line_id]["efficiency"],
        "action": "LINE_BALANCED",
        "timestamp": datetime.utcnow()
    }


# -------------------------------------------------------------------
# SMART DOWNTIME ANALYZER
# -------------------------------------------------------------------

@router.get("/analytics/downtime-analysis")
async def downtime_analysis():
    """
    Mock downtime intelligence.
    """
    return {
        "top_losses": [
            {"reason": "Material changeover", "minutes": 42},
            {"reason": "Micro stoppages", "minutes": 28},
            {"reason": "Operator break", "minutes": 15},
        ],
        "total_downtime_minutes": 85,
        "oee_impact": -3.2,
        "recommendation": "Optimize changeover procedure",
        "generated_at": datetime.utcnow()
    }


# -------------------------------------------------------------------
# PRODUCTION ANOMALY DETECTOR
# -------------------------------------------------------------------

@router.get("/analytics/anomaly-detector/{line_id}")
async def detect_production_anomaly(line_id: str):
    if line_id not in FAKE_LINES:
        raise HTTPException(status_code=404, detail="Line not found")

    eff = FAKE_LINES[line_id].get("efficiency", 80)

    anomaly = False
    severity = "NORMAL"

    if eff < 70:
        anomaly = True
        severity = "WARNING"

    if eff < 60:
        severity = "CRITICAL"

    return {
        "line_id": line_id,
        "anomaly_detected": anomaly,
        "severity": severity,
        "model_confidence": 0.88,
        "checked_at": datetime.utcnow()
    }


# -------------------------------------------------------------------
# GLOBAL FACTORY COMMAND CENTER VIEW
# -------------------------------------------------------------------

@router.get("/command-center/overview")
async def command_center_overview():
    running_batches = len([
        b for b in FAKE_BATCHES.values()
        if b.get("status") == "RUNNING"
    ])

    return {
        "factory_mode": "AUTO",
        "lines_active": len(FAKE_LINES),
        "running_batches": running_batches,
        "alerts_open": 2,
        "throughput_bph": 12450,
        "factory_oee": 0.86,
        "timestamp": datetime.utcnow()
    }

# -------------------------------------------------------------------
# DIGITAL TWIN SNAPSHOT
# -------------------------------------------------------------------

@router.get("/digital-twin/{line_id}")
async def digital_twin_snapshot(line_id: str):
    if line_id not in FAKE_LINES:
        raise HTTPException(status_code=404, detail="Line not found")

    line = FAKE_LINES[line_id]

    return {
        "line_id": line_id,
        "virtual_state": {
            "speed_bpm": 220,
            "temperature": 181.6,
            "load_percent": line.get("efficiency", 80),
            "predicted_output_next_hour": 13200,
        },
        "sync_status": "IN_SYNC",
        "twin_confidence": 0.94,
        "timestamp": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# SMART ENERGY OPTIMIZER
# -------------------------------------------------------------------

@router.get("/energy/optimize")
async def energy_optimizer():
    """
    Mock AI energy optimization.
    """
    return {
        "current_consumption_kwh": 1240,
        "optimized_consumption_kwh": 1095,
        "potential_savings_percent": 11.7,
        "recommendations": [
            "Run Line-2 during off-peak hours",
            "Reduce idle compressor cycles",
            "Enable eco mode on filler"
        ],
        "generated_at": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# AI YIELD PREDICTOR
# -------------------------------------------------------------------

@router.get("/analytics/yield-prediction/{batch_id}")
async def yield_prediction(batch_id: str):
    batch = FAKE_BATCHES.get(batch_id)

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    base_yield = 98.2

    if batch.get("status") == "RUNNING":
        predicted = base_yield - 0.4
    else:
        predicted = base_yield

    return {
        "batch_id": batch_id,
        "predicted_yield_percent": round(predicted, 2),
        "confidence": 0.89,
        "risk_flag": predicted < 97.5,
        "timestamp": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# AUTONOMOUS QUALITY GUARD
# -------------------------------------------------------------------

@router.post("/quality/auto-guard/{batch_id}")
async def autonomous_quality_guard(batch_id: str):
    batch = FAKE_BATCHES.get(batch_id)

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    defects = FAKE_DEFECTS.get(batch_id, [])

    action = "NONE"

    if len(defects) > 5:
        batch["status"] = "QUALITY_HOLD"
        action = "LINE_SLOWED"

    return {
        "batch_id": batch_id,
        "defects_detected": len(defects),
        "auto_action": action,
        "quality_state": batch["status"],
        "timestamp": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# PRODUCTION REPLAY (POWERFUL DEMO)
# -------------------------------------------------------------------

@router.get("/batches/{batch_id}/replay")
async def production_replay(batch_id: str):
    batch = FAKE_BATCHES.get(batch_id)

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    return {
        "batch_id": batch_id,
        "timeline": [
            {"event": "BATCH_STARTED", "time": "10:00"},
            {"event": "QUALITY_CHECK", "time": "10:25"},
            {"event": "MICRO_STOP", "time": "10:42"},
            {"event": "RUNNING", "time": "NOW"},
        ],
        "replay_ready": True,
        "generated_at": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# SELF-HEALING PRODUCTION LINE
# -------------------------------------------------------------------

@router.post("/lines/{line_id}/self-heal")
async def self_heal_line(line_id: str):
    if line_id not in FAKE_LINES:
        raise HTTPException(status_code=404, detail="Line not found")

    line = FAKE_LINES[line_id]

    before = line.get("efficiency", 80)

    # mock healing
    line["efficiency"] = min(100, before + 5)

    return {
        "line_id": line_id,
        "efficiency_before": before,
        "efficiency_after": line["efficiency"],
        "healing_action": "AUTO_TUNING_APPLIED",
        "timestamp": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# FACTORY RISK RADAR
# -------------------------------------------------------------------

@router.get("/risk/radar")
async def factory_risk_radar():
    return {
        "overall_risk": "LOW",
        "risk_factors": [
            {"type": "Maintenance", "level": "LOW"},
            {"type": "Quality", "level": "LOW"},
            {"type": "Supply", "level": "MEDIUM"},
        ],
        "recommended_focus": "Monitor raw material supply",
        "generated_at": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# GLOBAL PRODUCTION SCORE
# -------------------------------------------------------------------

@router.get("/analytics/production-score")
async def production_score():
    running = len([b for b in FAKE_BATCHES.values() if b.get("status") == "RUNNING"])
    total = max(len(FAKE_BATCHES), 1)

    score = round((running / total) * 100, 2)

    return {
        "production_score": score,
        "running_batches": running,
        "total_batches": total,
        "factory_grade": "A" if score > 80 else "B",
        "timestamp": datetime.utcnow(),
    }

# -------------------------------------------------------------------
# LIVE ANOMALY DETECTOR
# -------------------------------------------------------------------

@router.get("/ai/anomaly-detector/{line_id}")
async def anomaly_detector(line_id: str):
    if line_id not in FAKE_LINES:
        raise HTTPException(status_code=404, detail="Line not found")

    import random

    anomaly_score = round(random.uniform(0.02, 0.18), 3)
    is_anomaly = anomaly_score > 0.12

    return {
        "line_id": line_id,
        "anomaly_score": anomaly_score,
        "anomaly_detected": is_anomaly,
        "severity": "HIGH" if anomaly_score > 0.15 else "LOW",
        "recommended_action": (
            "Inspect filler vibration"
            if is_anomaly else
            "Operating normally"
        ),
        "timestamp": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# PREDICTIVE MAINTENANCE AI
# -------------------------------------------------------------------

@router.get("/maintenance/predict/{line_id}")
async def predictive_maintenance(line_id: str):
    if line_id not in FAKE_LINES:
        raise HTTPException(status_code=404, detail="Line not found")

    line = FAKE_LINES[line_id]

    health = line.get("efficiency", 80)

    if health > 90:
        risk_days = 30
        risk_level = "LOW"
    elif health > 75:
        risk_days = 14
        risk_level = "MEDIUM"
    else:
        risk_days = 5
        risk_level = "HIGH"

    return {
        "line_id": line_id,
        "maintenance_risk": risk_level,
        "estimated_days_to_service": risk_days,
        "confidence": 0.91,
        "timestamp": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# SMART SHIFT OPTIMIZER
# -------------------------------------------------------------------

@router.get("/shifts/optimize")
async def optimize_shifts():
    return {
        "recommended_shift_plan": [
            {"shift": "Morning", "workers": 42},
            {"shift": "Evening", "workers": 38},
            {"shift": "Night", "workers": 24},
        ],
        "expected_throughput_gain_percent": 7.4,
        "fatigue_risk": "LOW",
        "generated_at": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# RAW MATERIAL AUTO PLANNER
# -------------------------------------------------------------------

@router.get("/materials/auto-plan")
async def raw_material_planner():
    total_batches = len(FAKE_BATCHES)

    projected_need = total_batches * 1200  # mock logic

    return {
        "forecast_batches": total_batches,
        "projected_material_needed_kg": projected_need,
        "current_stock_ok": projected_need < 50000,
        "reorder_recommended": projected_need >= 50000,
        "generated_at": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# LINE BOTTLENECK DETECTOR
# -------------------------------------------------------------------

@router.get("/lines/bottlenecks")
async def bottleneck_detector():
    bottlenecks = []

    for line_id, line in FAKE_LINES.items():
        if line.get("efficiency", 80) < 75:
            bottlenecks.append({
                "line_id": line_id,
                "efficiency": line.get("efficiency"),
                "issue": "Throughput below optimal"
            })

    return {
        "bottleneck_count": len(bottlenecks),
        "lines": bottlenecks,
        "timestamp": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# FACTORY COMMAND CENTER SNAPSHOT
# -------------------------------------------------------------------

@router.get("/command-center")
async def command_center_snapshot():
    running_batches = len([
        b for b in FAKE_BATCHES.values()
        if b.get("status") == "RUNNING"
    ])

    total_lines = len(FAKE_LINES)

    avg_eff = (
        sum(l.get("efficiency", 80) for l in FAKE_LINES.values())
        / max(total_lines, 1)
    )

    return {
        "factory_status": "OPERATIONAL",
        "running_batches": running_batches,
        "total_lines": total_lines,
        "avg_line_efficiency": round(avg_eff, 2),
        "active_alerts": 1,
        "oee_estimate": round(avg_eff * 0.92, 2),
        "timestamp": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# SMART MICRO-STOP DETECTOR
# -------------------------------------------------------------------

@router.get("/lines/{line_id}/micro-stops")
async def micro_stop_detector(line_id: str):
    if line_id not in FAKE_LINES:
        raise HTTPException(status_code=404, detail="Line not found")

    import random

    stops = random.randint(0, 6)

    return {
        "line_id": line_id,
        "micro_stops_last_hour": stops,
        "risk_flag": stops > 3,
        "recommended_action": (
            "Inspect conveyor alignment"
            if stops > 3 else
            "Within normal range"
        ),
        "timestamp": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# AI PRODUCTION FORECAST (NEXT 24H)
# -------------------------------------------------------------------

@router.get("/analytics/forecast-24h")
async def production_forecast_24h():
    running = len([
        b for b in FAKE_BATCHES.values()
        if b.get("status") == "RUNNING"
    ])

    forecast_units = running * 24000  # mock math

    return {
        "running_batches": running,
        "forecast_next_24h_units": forecast_units,
        "confidence": 0.88,
        "risk_level": "LOW" if running > 0 else "MEDIUM",
        "generated_at": datetime.utcnow(),
    }

# -------------------------------------------------------------------
# WORKFORCE RISK ANALYTICS
# -------------------------------------------------------------------

@router.get("/workforce/risk")
async def workforce_risk():
    import random

    fatigue_index = round(random.uniform(0.1, 0.7), 2)

    risk_level = (
        "HIGH" if fatigue_index > 0.6 else
        "MEDIUM" if fatigue_index > 0.4 else
        "LOW"
    )

    return {
        "fatigue_index": fatigue_index,
        "risk_level": risk_level,
        "recommended_action": (
            "Rotate night shift workers"
            if risk_level == "HIGH"
            else "Workforce operating normally"
        ),
        "timestamp": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# SMART BATCH RECOMMENDER
# -------------------------------------------------------------------

@router.get("/batches/recommend-next")
async def recommend_next_batch():
    running_batches = [
        b for b in FAKE_BATCHES.values()
        if b.get("status") == "RUNNING"
    ]

    capacity_left = max(0, 5 - len(running_batches))

    return {
        "recommended_batch_size": 24000 if capacity_left > 0 else 0,
        "available_capacity_slots": capacity_left,
        "priority_sku": "SKU-500ML",
        "confidence": 0.89,
        "generated_at": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# DOWNTIME ROOT-CAUSE AI
# -------------------------------------------------------------------

@router.get("/ai/downtime-root-cause/{line_id}")
async def downtime_root_cause(line_id: str):
    if line_id not in FAKE_LINES:
        raise HTTPException(status_code=404, detail="Line not found")

    import random

    causes = [
        "Conveyor misalignment",
        "Filler pressure fluctuation",
        "Sensor calibration drift",
        "Bottle jam detected",
    ]

    return {
        "line_id": line_id,
        "predicted_root_cause": random.choice(causes),
        "confidence": round(random.uniform(0.72, 0.93), 2),
        "recommended_fix": "Inspect and recalibrate affected module",
        "timestamp": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# PRODUCTION CAPACITY SIMULATOR
# -------------------------------------------------------------------

@router.post("/analytics/capacity-simulate")
async def capacity_simulator(
    hours: int,
    active_lines: int,
):
    if hours <= 0 or active_lines <= 0:
        raise HTTPException(status_code=400, detail="Invalid simulation input")

    units_per_hour_per_line = 1200  # mock

    projected_output = hours * active_lines * units_per_hour_per_line

    return {
        "simulation_hours": hours,
        "active_lines": active_lines,
        "projected_output_units": projected_output,
        "confidence": 0.86,
        "timestamp": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# ENERGY ANOMALY DETECTOR
# -------------------------------------------------------------------

@router.get("/energy/anomaly")
async def energy_anomaly_detector():
    import random

    spike = round(random.uniform(0.8, 1.4), 2)

    anomaly = spike > 1.25

    return {
        "energy_spike_ratio": spike,
        "anomaly_detected": anomaly,
        "severity": "HIGH" if spike > 1.3 else "LOW",
        "recommended_action": (
            "Check compressor load"
            if anomaly else
            "Energy consumption normal"
        ),
        "timestamp": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# AUTONOMOUS PLANT SCORE
# -------------------------------------------------------------------

@router.get("/factory/autonomy-score")
async def plant_autonomy_score():
    total_lines = len(FAKE_LINES)
    avg_eff = (
        sum(l.get("efficiency", 80) for l in FAKE_LINES.values())
        / max(total_lines, 1)
    )

    digital_score = round((avg_eff * 0.6) + 25, 2)

    maturity = (
        "LEVEL_4_AUTONOMOUS"
        if digital_score > 85
        else "LEVEL_3_SEMI_AUTONOMOUS"
    )

    return {
        "autonomy_score": digital_score,
        "maturity_level": maturity,
        "oee_component": round(avg_eff, 2),
        "ai_coverage_percent": 78,
        "timestamp": datetime.utcnow(),
    }


# -------------------------------------------------------------------
# GLOBAL FACTORY SNAPSHOT (EXEC DASHBOARD)
# -------------------------------------------------------------------

@router.get("/factory/executive-snapshot")
async def executive_snapshot():
    running_batches = len([
        b for b in FAKE_BATCHES.values()
        if b.get("status") == "RUNNING"
    ])

    total_lines = len(FAKE_LINES)

    avg_eff = (
        sum(l.get("efficiency", 80) for l in FAKE_LINES.values())
        / max(total_lines, 1)
    )

    return {
        "plant_status": "GREEN",
        "running_batches": running_batches,
        "total_lines": total_lines,
        "avg_efficiency": round(avg_eff, 2),
        "risk_flags": 1,
        "throughput_trend": "UPWARD",
        "timestamp": datetime.utcnow(),
    }