import fastapi
from pydantic import BaseModel

router = fastapi.APIRouter(prefix='/tw-stock')


class UpdatePricesTask(BaseModel):
    start: str
    end: str


@router.post('/update-prices-tasks')
async def update_prices_tasks(task: UpdatePricesTask, request: fastapi.Request):
    request.app.state.scheduler.add_job(
        request.app.state.service['tw_stock'].update_prices_for_date_range,
        kwargs={
            'start': task.start,
            'end': task.end,
        }
    )

    return 'ok'


class UpdateStatementsTask(BaseModel):
    stock_id: str
    year: int
    season: int


@router.post('/update-statements-tasks')
async def update_statements_tasks(task: UpdateStatementsTask, request: fastapi.Request):
    request.app.state.scheduler.add_job(
        request.app.state.service['tw_stock'].update_statements,
        kwargs={
            'stock_id': task.stock_id,
            'year': task.year,
            'season': task.season,
        }
    )

    return 'ok'
