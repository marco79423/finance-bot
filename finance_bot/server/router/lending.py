import fastapi

router = fastapi.APIRouter(prefix='/lending')


@router.get('/records')
async def records(request: fastapi.Request):
    lending_records = await request.app.state.service['lending'].get_lending_records()
    return [
        lending_record.json()
        for lending_record in lending_records
    ]
