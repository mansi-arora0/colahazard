# app/api/mobile/dashboard/factory/defects.py

from fastapi import APIRouter, Depends, Query, Path, Body, UploadFile, File
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.config.database import get_db
from app.core.dependencies import get_current_user
from app.core.roles import require_role
from app.core.pagination import paginate
from app.schemas.common import SuccessResponse
from app.schemas.defect import (
    DefectCreate,
    DefectUpdate,
    DefectResponse,
    DefectSeverityStats,
    RootCauseAnalysis,
    CorrectiveActionRequest
)
from app.services.dashboard.factory_service import FactoryService

router = APIRouter()


# =========================================================
# 🐞 CREATE DEFECT ENTRY
# =========================================================
@router.post("/defect", response_model=DefectResponse)
async def create_defect(
    payload: DefectCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "qc"])
    service = FactoryService(db)
    return service.create_defect(payload, reporter_id=current_user.id)


# =========================================================
# ✏️ UPDATE DEFECT
# =========================================================
@router.put("/defect/{defect_id}", response_model=DefectResponse)
async def update_defect(
    defect_id: str,
    payload: DefectUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "qc"])
    service = FactoryService(db)
    return service.update_defect(defect_id, payload)


# =========================================================
# ❌ DELETE DEFECT
# =========================================================
@router.delete("/defect/{defect_id}", response_model=SuccessResponse)
async def delete_defect(
    defect_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["admin"])
    service = FactoryService(db)
    service.delete_defect(defect_id)
    return {"message": "Defect deleted successfully"}


# =========================================================
# 📋 LIST DEFECTS
# =========================================================
@router.get("/defects", response_model=List[DefectResponse])
async def list_defects(
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    batch_id: Optional[str] = None,
    severity: Optional[str] = None,
    line: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "qc"])
    service = FactoryService(db)

    defects = service.get_defects(
        batch_id=batch_id,
        severity=severity,
        line=line,
        start_date=start_date,
        end_date=end_date
    )

    return paginate(defects, page, limit)


# =========================================================
# 🔍 GET DEFECT DETAILS
# =========================================================
@router.get("/defect/{defect_id}", response_model=DefectResponse)
async def get_defect(
    defect_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "qc"])
    service = FactoryService(db)
    return service.get_defect_by_id(defect_id)


# =========================================================
# 📊 DEFECT SEVERITY STATISTICS
# =========================================================
@router.get("/defects/severity-stats", response_model=DefectSeverityStats)
async def defect_severity_stats(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "qc"])
    service = FactoryService(db)
    return service.calculate_defect_severity_stats()


# =========================================================
# 🧠 ROOT CAUSE ANALYSIS
# =========================================================
@router.post("/defect/root-cause", response_model=RootCauseAnalysis)
async def root_cause_analysis(
    defect_id: str = Body(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["qc"])
    service = FactoryService(db)
    return service.perform_root_cause_analysis(defect_id)


# =========================================================
# 🛠 APPLY CORRECTIVE ACTION
# =========================================================
@router.post("/defect/corrective-action", response_model=SuccessResponse)
async def corrective_action(
    payload: CorrectiveActionRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["qc", "admin"])
    service = FactoryService(db)
    service.apply_corrective_action(payload.defect_id, payload.action)
    return {"message": "Corrective action applied successfully"}


# =========================================================
# ✅ RESOLVE DEFECT
# =========================================================
@router.post("/defect/{defect_id}/resolve", response_model=SuccessResponse)
async def resolve_defect(
    defect_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["qc"])
    service = FactoryService(db)
    service.resolve_defect(defect_id)
    return {"message": "Defect resolved successfully"}


# =========================================================
# 🔄 REOPEN DEFECT
# =========================================================
@router.post("/defect/{defect_id}/reopen", response_model=SuccessResponse)
async def reopen_defect(
    defect_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["qc"])
    service = FactoryService(db)
    service.reopen_defect(defect_id)
    return {"message": "Defect reopened successfully"}


# =========================================================
# 🔥 DEFECT HEATMAP
# =========================================================
@router.get("/defects/heatmap")
async def defect_heatmap(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "qc"])
    service = FactoryService(db)
    return service.get_defect_heatmap()


# =========================================================
# 📈 LINE-WISE DEFECT ANALYTICS
# =========================================================
@router.get("/defects/line-stats")
async def line_defect_stats(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "qc"])
    service = FactoryService(db)
    return service.get_line_defect_stats()


# =========================================================
# 📤 EXPORT DEFECT DATA
# =========================================================
@router.get("/defects/export")
async def export_defects(
    format: str = Query("csv"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "qc"])
    service = FactoryService(db)
    return service.export_defects(format)


# =========================================================
# 📥 BULK DEFECT UPLOAD
# =========================================================
@router.post("/defects/bulk-upload")
async def bulk_upload_defects(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory"])
    service = FactoryService(db)
    return service.bulk_upload_defects(file)


# =========================================================
# 🌐 DEFECT DASHBOARD (HTML)
# =========================================================
@router.get("/defects/dashboard", response_class=HTMLResponse)
async def defect_dashboard():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Factory Defect Dashboard</title>
    <style>
        body {
            background: #0f172a;
            color: white;
            font-family: Arial, sans-serif;
            padding: 40px;
        }
        h1 { color: #f43f5e; }
        .card {
            background: #1e293b;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
        }
        button {
            background: #f43f5e;
            border: none;
            padding: 10px 15px;
            border-radius: 6px;
            color: white;
            cursor: pointer;
        }
        button:hover {
            background: #be123c;
        }
    </style>
</head>
<body>

<h1>🐞 Defect Management Dashboard</h1>

<div class="card">
    <h2>Create Defect</h2>
    <button onclick="alert('POST /defect')">Add Defect</button>
</div>

<div class="card">
    <h2>Severity Stats</h2>
    <button onclick="alert('GET /defects/severity-stats')">View Stats</button>
</div>

<div class="card">
    <h2>Heatmap</h2>
    <button onclick="alert('GET /defects/heatmap')">View Heatmap</button>
</div>

<div class="card">
    <h2>Line Stats</h2>
    <button onclick="alert('GET /defects/line-stats')">View Line Analytics</button>
</div>

<script>
    console.log("Defect dashboard loaded successfully.");
</script>

</body>
</html>
"""