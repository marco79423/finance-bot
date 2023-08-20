from typing import Optional

import fastapi
from pydantic import BaseModel

from finance_bot.infrastructure import infra

router = fastapi.APIRouter(prefix='/tw-stock')


@router.post('/update-stocks-tasks')
async def update_prices_tasks(request: fastapi.Request):
    infra.scheduler.add_task(
        request.app.state.service['tw_stock'].update_stocks,
    )

    return 'ok'


class UpdatePricesTask(BaseModel):
    start: str
    end: str


@router.post('/update-prices-tasks')
async def update_prices_tasks(task: UpdatePricesTask, request: fastapi.Request):
    infra.scheduler.add_task(
        request.app.state.service['tw_stock'].update_prices_for_date_range,
        kwargs={
            'start': task.start,
            'end': task.end,
        }
    )

    return 'ok'


class UpdateMonthlyRevenueTask(BaseModel):
    year: int
    month: int


@router.post('/update-monthly-revenue-tasks')
async def update_monthly_revenue_tasks(task: UpdateMonthlyRevenueTask, request: fastapi.Request):
    infra.scheduler.add_task(
        request.app.state.service['tw_stock'].update_monthly_revenue,
        kwargs={
            'year': task.year,
            'month': task.month,
        }
    )

    return 'ok'


class UpdateFinancialStatementsTask(BaseModel):
    stock_id: Optional[str]
    year: Optional[int]
    quarter: Optional[int]


@router.post('/update-financial-statements-tasks')
async def update_financial_statements_tasks(task: Optional[UpdateFinancialStatementsTask], request: fastapi.Request):
    if task:
        infra.scheduler.add_task(
            request.app.state.service['tw_stock'].update_financial_statements,
            kwargs={
                'stock_id': task.stock_id,
                'year': task.year,
                'quarter': task.quarter,
            }
        )
    else:
        infra.scheduler.add_task(
            request.app.state.service['tw_stock'].update_financial_statements,
        )
    return 'ok'
