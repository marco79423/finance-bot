import fastapi

from finance_bot.infrastructure import infra

router = fastapi.APIRouter(prefix='/debug')


@router.get('/ping', response_class=fastapi.responses.PlainTextResponse)
async def ping():
    return 'pong'


@router.get('/notification')
async def send_notification():
    await infra.notifier.send(message='理財機器人通知測試')


@router.get('/scheduled-jobs')
async def get_scheduled_jobs():
    jobs = infra.scheduler.get_jobs()
    return [str(job) for job in jobs]
