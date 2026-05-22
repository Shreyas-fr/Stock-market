from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.postgres import get_db
from app.models.risk import Alert
from typing import Optional
from pydantic import BaseModel

router = APIRouter(prefix="/alerts", tags=["Alerts"])


class AlertCreate(BaseModel):
    company_id: Optional[str] = None
    alert_type: str
    severity: str
    title: str
    message: Optional[str] = None


@router.get("/")
async def get_alerts(
    limit: int = Query(50, ge=1, le=200),
    severity: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Alert).order_by(desc(Alert.sent_at)).limit(limit)
    if severity:
        stmt = stmt.where(Alert.severity == severity)
    result = await db.execute(stmt)
    alerts = result.scalars().all()
    return [
        {
            "id": str(a.id),
            "alert_type": a.alert_type,
            "severity": a.severity,
            "title": a.title,
            "message": a.message,
            "sent_at": a.sent_at.isoformat() if a.sent_at else None,
        }
        for a in alerts
    ]


@router.post("/", status_code=201)
async def create_alert(alert_data: AlertCreate, db: AsyncSession = Depends(get_db)):
    from uuid import UUID
    alert = Alert(
        company_id=UUID(alert_data.company_id) if alert_data.company_id else None,
        alert_type=alert_data.alert_type,
        severity=alert_data.severity,
        title=alert_data.title,
        message=alert_data.message,
    )
    db.add(alert)
    await db.flush()
    return {"id": str(alert.id), "title": alert.title}
