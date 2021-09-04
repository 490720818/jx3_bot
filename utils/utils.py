import nonebot
from .ap_scheduler import APSscheduler


scheduler = APSscheduler
'''全局定时器对象'''


nickname = list(nonebot.get_driver().config.nickname)[0]
'''机器人昵称'''


def get_bot():
    '''
    全局获取bot对象
    '''
    return list(nonebot.get_bots().values())[0]
