import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path

from app.core.config import get_settings
from app.core.database import engine, Base, SessionLocal
from app.api import api_router
from app.tasks.scheduler import start_scheduler, stop_scheduler
from app.models import User, Account, Category, Transaction, Budget
from app.core.security import get_password_hash
from datetime import date, timedelta
import random

settings = get_settings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("fintrack")


def seed_demo_data():
    """Создание демо-данных при первом запуске"""
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return

        user = User(
            email="demo@fintrack.ru",
            username="demo",
            full_name="Демо Пользователь",
            hashed_password=get_password_hash("demo1234"),
        )
        db.add(user)
        db.flush()

        accounts = [
            Account(user_id=user.id, name="Основной счёт", balance=85000, icon="wallet", color="#6366f1"),
            Account(user_id=user.id, name="Накопления", balance=250000, icon="piggy-bank", color="#10b981"),
            Account(user_id=user.id, name="Карта", balance=12400, icon="credit-card", color="#f59e0b"),
        ]
        db.add_all(accounts)
        db.flush()

        expense_cats = [
            ("Продукты", "shopping-cart", "#ef4444"),
            ("Транспорт", "car", "#3b82f6"),
            ("Кафе и рестораны", "utensils", "#f97316"),
            ("Развлечения", "gamepad-2", "#8b5cf6"),
            ("Жильё", "home", "#06b6d4"),
            ("Здоровье", "heart", "#ec4899"),
            ("Одежда", "shirt", "#14b8a6"),
            ("Подписки", "repeat", "#a855f7"),
        ]
        income_cats = [
            ("Зарплата", "banknote", "#22c55e"),
            ("Фриланс", "laptop", "#84cc16"),
            ("Инвестиции", "trending-up", "#10b981"),
        ]

        cats = {}
        for name, icon, color in expense_cats:
            c = Category(user_id=user.id, name=name, type="expense", icon=icon, color=color)
            db.add(c)
            db.flush()
            cats[name] = c
        for name, icon, color in income_cats:
            c = Category(user_id=user.id, name=name, type="income", icon=icon, color=color)
            db.add(c)
            db.flush()
            cats[name] = c

        today = date.today()
        for i in range(60):
            d = today - timedelta(days=i)
            for _ in range(random.randint(1, 3)):
                cat_name = random.choice(list(expense_cats))[0]
                amount = round(random.uniform(200, 5000), 2)
                tx = Transaction(
                    user_id=user.id,
                    account_id=accounts[0].id,
                    category_id=cats[cat_name].id,
                    amount=amount,
                    type="expense",
                    description=f"Покупка — {cat_name}",
                    date=d,
                )
                db.add(tx)
            if i % 15 == 0:
                tx = Transaction(
                    user_id=user.id,
                    account_id=accounts[0].id,
                    category_id=cats["Зарплата"].id,
                    amount=120000,
                    type="income",
                    description="Зарплата",
                    date=d,
                )
                db.add(tx)

        budgets = [
            Budget(user_id=user.id, category_id=cats["Продукты"].id, amount=25000, period="monthly", start_date=today.replace(day=1)),
            Budget(user_id=user.id, category_id=cats["Транспорт"].id, amount=8000, period="monthly", start_date=today.replace(day=1)),
            Budget(user_id=user.id, category_id=cats["Кафе и рестораны"].id, amount=12000, period="monthly", start_date=today.replace(day=1)),
        ]
        db.add_all(budgets)
        db.commit()
        logger.info("Demo data seeded successfully. Login: demo@fintrack.ru / demo1234")
    except Exception as e:
        logger.error(f"Seed failed: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_demo_data()
    if settings.ENABLE_SCHEDULER:
        start_scheduler()
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} started")
    yield
    if settings.ENABLE_SCHEDULER:
        stop_scheduler()
    logger.info("Application stopped")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(api_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})