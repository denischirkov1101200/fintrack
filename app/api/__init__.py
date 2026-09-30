from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.accounts import router as accounts_router
from app.api.categories import router as categories_router
from app.api.transactions import router as transactions_router
from app.api.budgets import router as budgets_router
from app.api.analytics import router as analytics_router

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(accounts_router)
api_router.include_router(categories_router)
api_router.include_router(transactions_router)
api_router.include_router(budgets_router)
api_router.include_router(analytics_router)