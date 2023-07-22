import fastapi
from pydantic import BaseModel

router = fastapi.APIRouter(prefix='/tw-stock')


class UpdateTask(BaseModel):
    start: str
    end: str


@router.post('/update-prices-tasks')
async def update_prices_tasks(task: UpdateTask, request: fastapi.Request):
    request.app.state.scheduler.add_job(
        request.app.state.daemon['tw_stock'].update_prices_for_date_range,
        kwargs={
            'start': task.start,
            'end': task.end,
        }
    )

    return 'ok'
