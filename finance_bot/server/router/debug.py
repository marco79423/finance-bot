import fastapi
import telegram

from finance_bot.config import conf

router = fastapi.APIRouter(prefix='/debug')


@router.get('/ping', response_class=fastapi.responses.PlainTextResponse)
async def ping():
    return 'pong'


@router.get('/notification')
async def send_notification():
    bot = telegram.Bot(conf.notification.telegram.token)
    await bot.send_message(chat_id=conf.notification.telegram.chat_id, text='理財機器人通知測試')
