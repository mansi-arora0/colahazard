# app/api/mobile/dashboard/factory/shift.py

from fastapi import APIRouter, Depends, Query, Path, Body, UploadFile, File
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from app.config.database import get_db
from app.core.dependencies import get_current_user
from app.core.roles import require_role
from app.core.pagination import paginate
from app.schemas.common import SuccessResponse
from app.schemas.shift import (
    ShiftCreate,
    ShiftUpdate,
    ShiftResponse,
    ShiftStartRequest,
    ShiftEndRequest,
    BreakLogRequest,
    OvertimeRequest,
    AttendanceRequest,
    IncidentReportRequest,
    ShiftPerformanceResponse
)
from app.services.dashboard.factory_service import FactoryService

router = APIRouter()


# =========================================================
# 🏭 CREATE SHIFT
# =========================================================
@router.post("/shift", response_model=ShiftResponse)
async def create_shift(
    payload: ShiftCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "admin"])
    service = FactoryService(db)
    return service.create_shift(payload)


# =========================================================
# ✏️ UPDATE SHIFT
# =========================================================
@router.put("/shift/{shift_id}", response_model=ShiftResponse)
async def update_shift(
    shift_id: str,
    payload: ShiftUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "admin"])
    service = FactoryService(db)
    return service.update_shift(shift_id, payload)


# =========================================================
# ▶️ START SHIFT
# =========================================================
@router.post("/shift/start", response_model=SuccessResponse)
async def start_shift(
    payload: ShiftStartRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory"])
    service = FactoryService(db)
    service.start_shift(payload.shift_id, datetime.utcnow())
    return {"message": "Shift started successfully"}


# =========================================================
# ⏹ END SHIFT
# =========================================================
@router.post("/shift/end", response_model=SuccessResponse)
async def end_shift(
    payload: ShiftEndRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory"])
    service = FactoryService(db)
    service.end_shift(payload.shift_id, datetime.utcnow())
    return {"message": "Shift ended successfully"}


# =========================================================
# 👥 ASSIGN WORKERS
# =========================================================
@router.post("/shift/{shift_id}/assign-workers", response_model=SuccessResponse)
async def assign_workers(
    shift_id: str,
    worker_ids: List[str] = Body(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "admin"])
    service = FactoryService(db)
    service.assign_workers(shift_id, worker_ids)
    return {"message": "Workers assigned successfully"}


# =========================================================
# ☕ LOG BREAK
# =========================================================
@router.post("/shift/break", response_model=SuccessResponse)
async def log_break(
    payload: BreakLogRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory"])
    service = FactoryService(db)
    service.log_break(payload)
    return {"message": "Break logged successfully"}


# =========================================================
# ⏰ LOG OVERTIME
# =========================================================
@router.post("/shift/overtime", response_model=SuccessResponse)
async def log_overtime(
    payload: OvertimeRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "admin"])
    service = FactoryService(db)
    service.log_overtime(payload)
    return {"message": "Overtime recorded successfully"}


# =========================================================
# 📋 ATTENDANCE MARKING
# =========================================================
@router.post("/shift/attendance", response_model=SuccessResponse)
async def mark_attendance(
    payload: AttendanceRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory"])
    service = FactoryService(db)
    service.mark_attendance(payload)
    return {"message": "Attendance marked successfully"}


# =========================================================
# 🚨 INCIDENT REPORT
# =========================================================
@router.post("/shift/incident", response_model=SuccessResponse)
async def report_incident(
    payload: IncidentReportRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "admin"])
    service = FactoryService(db)
    service.report_incident(payload)
    return {"message": "Incident reported successfully"}


# =========================================================
# 📊 SHIFT PERFORMANCE METRICS
# =========================================================
@router.get("/shift/{shift_id}/performance", response_model=ShiftPerformanceResponse)
async def shift_performance(
    shift_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "admin"])
    service = FactoryService(db)
    return service.get_shift_performance(shift_id)


# =========================================================
# 📈 SHIFT SUMMARY
# =========================================================
@router.get("/shift/summary")
async def shift_summary(
    date_filter: Optional[date] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "admin"])
    service = FactoryService(db)
    return service.get_shift_summary(date_filter)


# =========================================================
# 📤 EXPORT SHIFT DATA
# =========================================================
@router.get("/shift/export")
async def export_shift_data(
    format: str = Query("csv"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["admin"])
    service = FactoryService(db)
    return service.export_shift_data(format)


# =========================================================
# 📥 BULK ATTENDANCE UPLOAD
# =========================================================
@router.post("/shift/bulk-attendance")
async def bulk_attendance_upload(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["admin"])
    service = FactoryService(db)
    return service.bulk_upload_attendance(file)


# =========================================================
# 🌐 SHIFT DASHBOARD (HTML)
# =========================================================
@router.get("/shift/dashboard", response_class=HTMLResponse)
async def shift_dashboard():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Factory Shift Dashboard</title>
    <style>
        body {
            background-color: #111827;
            color: white;
            font-family: Arial, sans-serif;
            padding: 40px;
        }
        h1 { color: #3b82f6; }
        .card {
            background: #1f2937;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
        }
        button {
            background: #3b82f6;
            border: none;
            padding: 10px 15px;
            border-radius: 6px;
            color: white;
            cursor: pointer;
        }
        button:hover {
            background: #2563eb;
        }
    </style>
</head>
<body>

<h1>🏭 Shift Management Dashboard</h1>

<div class="card">
    <h2>Start Shift</h2>
    <button onclick="alert('POST /shift/start')">Start</button>
</div>

<div class="card">
    <h2>End Shift</h2>
    <button onclick="alert('POST /shift/end')">End</button>
</div>

<div class="card">
    <h2>Performance</h2>
    <button onclick="alert('GET /shift/{shift_id}/performance')">View Performance</button>
</div>

<div class="card">
    <h2>Shift Summary</h2>
    <button onclick="alert('GET /shift/summary')">View Summary</button>
</div>

<script>
    console.log("Shift dashboard loaded.");
</script>

</body>
</html>
"""