# app/api/mobile/dashboard/factory/quality.py

from fastapi import APIRouter, Depends, Query, Path, Body
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.config.database import get_db
from app.core.dependencies import get_current_user
from app.core.roles import require_role
from app.core.pagination import paginate
from app.schemas.common import SuccessResponse
from app.schemas.quality import (
    QualityCheckCreate,
    QualityCheckUpdate,
    QualityCheckResponse,
    QualityApprovalRequest,
    ReworkRequest,
    QualityScoreResponse,
    DefectTrendResponse
)
from app.services.dashboard.factory_service import FactoryService

router = APIRouter()


# =========================================================
# 🧪 CREATE QUALITY CHECK
# =========================================================
@router.post("/quality/check", response_model=QualityCheckResponse)
async def create_quality_check(
    payload: QualityCheckCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "qc"])
    service = FactoryService(db)
    return service.create_quality_check(payload, inspector_id=current_user.id)


# =========================================================
# ✏️ UPDATE QUALITY CHECK
# =========================================================
@router.put("/quality/{check_id}", response_model=QualityCheckResponse)
async def update_quality_check(
    check_id: str,
    payload: QualityCheckUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "qc"])
    service = FactoryService(db)
    return service.update_quality_check(check_id, payload)


# =========================================================
# 📋 LIST QUALITY CHECKS
# =========================================================
@router.get("/quality/checks", response_model=List[QualityCheckResponse])
async def list_quality_checks(
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    batch_id: Optional[str] = None,
    line: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "qc"])
    service = FactoryService(db)

    checks = service.get_quality_checks(
        batch_id=batch_id,
        line=line,
        start_date=start_date,
        end_date=end_date
    )

    return paginate(checks, page, limit)


# =========================================================
# 🔍 GET QUALITY CHECK DETAILS
# =========================================================
@router.get("/quality/{check_id}", response_model=QualityCheckResponse)
async def get_quality_check(
    check_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "qc"])
    service = FactoryService(db)
    return service.get_quality_check_by_id(check_id)


# =========================================================
# ✅ APPROVE QUALITY CHECK
# =========================================================
@router.post("/quality/approve", response_model=SuccessResponse)
async def approve_quality_check(
    payload: QualityApprovalRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["qc", "admin"])
    service = FactoryService(db)
    service.approve_quality_check(payload.check_id, approver_id=current_user.id)
    return {"message": "Quality check approved successfully"}


# =========================================================
# ❌ REJECT BATCH BASED ON QC
# =========================================================
@router.post("/quality/reject/{batch_id}", response_model=SuccessResponse)
async def reject_batch(
    batch_id: str,
    reason: str = Body(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["qc", "admin"])
    service = FactoryService(db)
    service.reject_batch(batch_id, reason)
    return {"message": "Batch rejected successfully"}


# =========================================================
# 🔁 SEND BATCH FOR REWORK
# =========================================================
@router.post("/quality/rework", response_model=SuccessResponse)
async def send_for_rework(
    payload: ReworkRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "qc"])
    service = FactoryService(db)
    service.send_batch_for_rework(payload.batch_id, payload.instructions)
    return {"message": "Batch sent for rework"}


# =========================================================
# 📊 QUALITY SCORE
# =========================================================
@router.get("/quality/score", response_model=QualityScoreResponse)
async def quality_score(
    batch_id: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "qc"])
    service = FactoryService(db)
    return service.calculate_quality_score(batch_id)


# =========================================================
# 📈 DEFECT TREND ANALYSIS
# =========================================================
@router.get("/quality/trends", response_model=List[DefectTrendResponse])
async def defect_trends(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "qc"])
    service = FactoryService(db)
    return service.get_defect_trends(start_date, end_date)


# =========================================================
# 🔥 DEFECT HEATMAP
# =========================================================
@router.get("/quality/heatmap")
async def defect_heatmap(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "qc"])
    service = FactoryService(db)
    return service.get_defect_heatmap()


# =========================================================
# 📤 EXPORT QUALITY DATA
# =========================================================
@router.get("/quality/export")
async def export_quality_data(
    format: str = Query("csv"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(current_user, ["factory", "qc"])
    service = FactoryService(db)
    return service.export_quality_data(format)


# =========================================================
# 🌐 EMBEDDED QUALITY DASHBOARD (HTML)
# =========================================================
@router.get("/quality/dashboard", response_class=HTMLResponse)
async def quality_dashboard():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Factory Quality Dashboard</title>
    <style>
        body {
            background: #121212;
            color: #ffffff;
            font-family: Arial, sans-serif;
            padding: 40px;
        }
        h1 {
            color: #00e6b8;
        }
        .card {
            background: #1e1e1e;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(0, 230, 184, 0.15);
        }
        button {
            background: #00e6b8;
            border: none;
            padding: 10px 20px;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
        }
        button:hover {
            background: #00b38f;
        }
    </style>
</head>
<body>

<h1>🧪 Quality Control Dashboard</h1>

<div class="card">
    <h2>Record Quality Check</h2>
    <button onclick="alert('Call POST /quality/check')">Add QC</button>
</div>

<div class="card">
    <h2>View Trends</h2>
    <button onclick="alert('Call GET /quality/trends')">Load Trends</button>
</div>

<div class="card">
    <h2>Quality Score</h2>
    <button onclick="alert('Call GET /quality/score')">View Score</button>
</div>

<div class="card">
    <h2>Heatmap</h2>
    <button onclick="alert('Call GET /quality/heatmap')">View Heatmap</button>
</div>

<script>
    console.log("Quality Dashboard Loaded");
</script>

</body>
</html>
"""