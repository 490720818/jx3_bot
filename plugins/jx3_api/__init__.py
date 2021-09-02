from nonebot import get_driver
from utils.jx3_soket import on_connect
from nonebot.plugin import on
from nonebot.adapters.cqhttp import Bot
import asyncio
from datetime import datetime
from .data_source import get_server
from nonebot.plugin import export
from utils.jx3_event import (
    OpenServerRecvEvent,
    NewsRecvEvent,
    AdventureRecvEvent,
    DailyEvent,
    OpenServerSendEvent,
    GoldQueryEvent,
    ExtraPointEvent,
    MedicineEvent,
    MacroEvent,
    AdventureConditionEvent,
    ExamEvent,
    PendantEvent,

)

export = export()
export.plugin_name = 'ws链接回复'
export.plugin_usage = '用于jx3_api的ws链接，处理服务器接收信息。'
export.ignore = True  # 插件管理器忽略此插件

driver = get_driver()


@driver.on_bot_connect
async def _(bot: Bot):
    '''
    初始化链接ws
    '''
    loop = asyncio.get_event_loop()
    loop.create_task(on_connect(loop, bot))


open_server_recv = on(type="open_server_recv", priority=5, block=True)  # 开服推送
news_recv = on(type="news_recv", priority=5, block=True)  # 新闻推送
adventure_recv = on(type="adventure_recv", priority=5, block=True)  # 奇遇推送
daily = on(type="daily", priority=5, block=True)    # 日常查询
open_server_send = on(type='open_server_send', priority=5, block=True)  # 开服查询
gold_query = on(type='gold_query', priority=5, block=True)  # 金价查询
# TODO：花价，配装查询
extra_point = on(type='extra_point', priority=5, block=True)  # 奇穴查询
medicine = on(type='medicine', priority=5, block=True)  # 小药查询
macro = on(type='macro', priority=5, block=True)  # 宏查询
# TODO：物价查询
adventurecondition = on(type='adventurecondition', priority=5, block=True)  # 奇遇条件查询
exam = on(type='exam', priority=5, block=True)  # 科举查询
# TODO：地图器物查询，装饰物查询，奇遇查询
pendant = on(type='pendant', priority=5, block=True)  # 挂件查询


@open_server_recv.handle()
async def _(bot: Bot, event: OpenServerRecvEvent):
    '''
    开服推送事件
    '''
    server = event.server
    stauts = event.status
    msg = None
    time_now = datetime.now().strftime("%H时%M分")
    if stauts:
        msg = f'时间：{time_now}\n[{server}] 开服啦！'
    group_list = await bot.get_group_list()
    for group in group_list:
        group_server = await get_server(group['group_id'])
        if group_server == server:
            await bot.send_group_msg(group_id=group['group_id'], message=msg)
    await open_server_recv.finish()


@news_recv.handle()
async def _(bot: Bot, event: NewsRecvEvent):
    '''
    新闻推送事件
    '''
    news_type = event.news_type
    news_tittle = event.news_tittle
    news_url = event.news_url
    news_date = event.news_date

    msg = f"[{news_type}]来惹\n标题：{news_tittle}\nurl：{news_url}\n日期：{news_date}"
    group_list = await bot.get_group_list()
    for group in group_list:
        await bot.send_group_msg(group_id=group['id'], message=msg)
    await news_recv.finish()


@adventure_recv.handle()
async def _(bot: Bot, event: AdventureRecvEvent):
    '''
    奇遇推送事件
    '''
    server = event.server
    msg = f'奇遇播报：\n[{event.serendipity}]在[{event.time}]被[{event.name}]抱走惹。'
    group_list = await bot.get_group_list()
    for group in group_list:
        group_server = await get_server(group['group_id'])
        if group_server == server:
            await bot.send_group_msg(group_id=group['group_id'], message=msg)
    await adventure_recv.finish()


@daily.handle()
async def _(bot: Bot, event: DailyEvent):
    '''
    日常查询
    '''
    msg = f'当前时间：{event.DateTime} 星期{event.Week}\n'
    msg += f'今日大战：{event.DayWar}\n'
    msg += f'今日战场：{event.DayBattle}\n'
    msg += f'公共任务：{event.DayCommon}\n'
    msg += f'阵营任务：{event.DayCamp}\n'
    if event.DayDraw is not None:
        msg += f'美人画像：{event.DayDraw}\n'
    msg += f'\n武林通鉴·公共任务\n{event.WeekCommon}\n'
    msg += f'武林通鉴·秘境任务\n{event.WeekFive}\n'
    msg += f'武林通鉴·团队秘境\n{event.WeekTeam}'
    await daily.finish(msg)


@open_server_send.handle()
async def _(bot: Bot, event: OpenServerSendEvent):
    '''
    开服查询
    '''
    status = "已开服" if event.status else "维护中"
    msg = f'{event.server}当前状态是[{status}]'
    await open_server_send(msg)


@gold_query.handle()
async def _(bot: Bot, event: GoldQueryEvent):
    '''
    金价查询
    '''
    date_now = datetime.now().strftime("%Y-%m-%d")
    msg = f'[{event.server}]金价，日期：{date_now}\n'
    msg += f'万宝楼：{event.price_wanbaolou}\n'
    msg += f'uu898：{event.price_uu898}\n'
    msg += f'dd373：{event.price_dd373}\n'
    msg += f'5173：{event.price_5173}\n'
    msg += f'7881：{event.price_7881}'
    await gold_query.finish(msg)


@extra_point.handle()
async def _(bot: Bot, event: ExtraPointEvent):
    '''
    奇穴查询
    '''
    msg = f'[{event.name}]奇穴：\n'
    msg += f'龙门绝境奇穴：\n{event.longmen}\n'
    msg += f'战场任务奇穴：\n{event.battle}'
    await extra_point.finish(msg)


@medicine.handle()
async def _(bot: Bot, event: MedicineEvent):
    '''
    小药查询
    '''
    msg = f'[{event.name}]小药：\n'
    msg += f'增强食品：{event.heightenFood}\n'
    msg += f'辅助食品：{event.auxiliaryFood}\n'
    msg += f'增强药品：{event.heightenDrug}\n'
    msg += f'辅助药品：{event.auxiliaryDrug}'

    await medicine.finish(msg)


@macro.handle()
async def _(bot: Bot, event: MacroEvent):
    '''
    宏查询
    '''
    msg = f'[{event.name}]宏：\n'
    msg += f'{event.command}\n\n'
    msg += f'奇穴：{event.plan}'

    await macro.finish(msg)


@adventurecondition.handle()
async def _(bot: Bot, event: AdventureConditionEvent):
    '''
    奇遇条件查询
    '''
    msg = f'[{event.name}]条件：\n'
    msg += f'触发方式：{event.method}\n'
    msg += f'满足条件：{event.need}\n'
    msg += f'其他可能：{event.other}\n'
    msg += f'物品奖励：{event.reward}'

    await adventurecondition.finish(msg)


@exam.handle()
async def _(bot: Bot, event: ExamEvent):
    '''
    科举查询
    '''
    msg = f'[问题]\n{event.question}\n'
    msg+f'[答案]\n{event.answer}'

    await exam.finish(msg)


@pendant.handle()
async def _(bot: Bot, event: PendantEvent):
    '''
    挂件查询
    '''
    msg = f'[{event.name}]\n'
    msg += f'物品类型：{event.type}\n'
    msg += f'使用特效：{event.use}\n'
    msg += f'物品说明：{event.explain}\n'
    msg += f'获取方式：{event.obtain}'

    await pendant.finish(msg)
