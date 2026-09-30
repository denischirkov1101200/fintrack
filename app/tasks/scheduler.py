import logging
from datetime import date, datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.models.user import User
from sqlalchemy import func

logger = logging.getLogger("fintrack.scheduler")

scheduler = BackgroundScheduler(timezone="Europe/Moscow")


def check_budgets():
    """Ежедневная проверка превышения бюджетов"""
    db: Session = SessionLocal()
    try:
        budgets = db.query(Budget).filter(Budget.is_active == True).all()
        for budget in budgets:
            end = budget.end_date or date.today()
            spent = (
                db.query(func.coalesce(func.sum(Transaction.amount), 0.0))
                .filter(
                    Transaction.user_id == budget.user_id,
                    Transaction.category_id == budget.category_id,
                    Transaction.type == "expense",
                    Transaction.date >= budget.start_date,
                    Transaction.date <= end,
                )
                .scalar()
            )
            if spent > budget.amount:
                logger.warning(
                    f"[Budget Alert] User {budget.user_id} | Category {budget.category_id} | "
                    f"Spent {spent:.2f} / Limit {budget.amount:.2f}"
                )
        logger.info(f"Budget check completed at {datetime.now(timezone.utc)}")
    except Exception as e:
        logger.error(f"Budget check failed: {e}")
    finally:
        db.close()


def daily_stats_recalc():
    """Пересчёт статистики (логирование)"""
    db: Session = SessionLocal()
    try:
        users_count = db.query(func.count(User.id)).scalar()
        tx_count = db.query(func.count(Transaction.id)).scalar()
        logger.info(f"Daily stats: users={users_count}, transactions={tx_count}")
    except Exception as e:
        logger.error(f"Stats recalc failed: {e}")
    finally:
        db.close()


def start_scheduler():
    if scheduler.running:
        return
    scheduler.add_job(check_budgets, CronTrigger(hour=3, minute=0), id="check_budgets")
    scheduler.add_job(daily_stats_recalc, CronTrigger(hour=4, minute=0), id="daily_stats")
    scheduler.start()
    logger.info("APScheduler started successfully")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")