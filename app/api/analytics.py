from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.analytics import DashboardStats
from app.services import analytics as analytics_service

router = APIRouter(prefix="/analytics", tags=["Аналитика"])


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return analytics_service.get_dashboard_stats(db, current_user.id, start_date, end_date)