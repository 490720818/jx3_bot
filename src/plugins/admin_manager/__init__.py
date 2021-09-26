from datetime import datetime

from configs.config import DEFAULT_FIREND_ADD, DEFAULT_GROUP_ADD, PRIVATE_CHAT
from nonebot import on_message, on_notice, on_regex, on_request
from nonebot.adapters.cqhttp import (Bot, FriendAddNoticeEvent,
                                     FriendRequestEvent, GroupRequestEvent,
                                     MessageSegment, PrivateMessageEvent)
from nonebot.permission import SUPERUSER
from nonebot.plugin import export
from utils.browser import get_html_screenshots
from utils.log import logger
from utils.utils import get_admin_list, nickname

from ..chat.data_source import get_reply_jx3, get_reply_qingyunke
from .data_source import (change_status_all, check_event, get_all_data,
                          get_text_num, leave_group, set_robot_status)

export = export()
export.plugin_name = '超级用户管理'
export.plugin_usage = '用于超级用户私聊机器人管理指令。'
export.ignore = True  # 插件管理器忽略此插件


check_firend_add = ['notice.friend_add']
someone_add_me = on_notice(rule=check_event(check_firend_add), priority=3, block=True)


@someone_add_me.handle()
async def _(bot: Bot, event: FriendAddNoticeEvent):
    '''添加好友'''
    user_id = event.user_id
    user_info = await bot.get_stranger_info(user_id=user_id, no_cache=True)
    user_name = user_info['nickname']
    msg = f"我添加了好友[{user_name}]({user_id})"
    admin_user_list = get_admin_list()
    for admin_id in admin_user_list:
        user_id = int(admin_id)
        await bot.send_private_msg(user_id=user_id, message=msg)
    await someone_add_me.finish()


check_friend_add = ['request.friend']
friend_add = on_request(rule=check_event(check_friend_add), priority=3, block=True)


@friend_add.handle()
async def _(bot: Bot, event: FriendRequestEvent):
    '''加好友请求事件'''
    if DEFAULT_FIREND_ADD:
        await event.approve(bot)
    await friend_add.finish()

check_group_add = ['request.group.invite']
group_add = on_request(rule=check_event(check_group_add), priority=3, block=True)


@group_add.handle()
async def _(bot: Bot, event: GroupRequestEvent):
    '''加群请求事件'''
    if DEFAULT_GROUP_ADD:
        await event.approve(bot)
    await group_add.finish()


group_list_event = ['message.private.friend', 'message.private.group']
get_group_list = on_regex(pattern=r"(^状态$)|(^运行状态$)", rule=check_event(
    group_list_event), permission=SUPERUSER, priority=2, block=True)


@get_group_list.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    '''超级用户私聊消息'''
    data = {}
    groups = await get_all_data()
    group_nums = len(groups)
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data['time'] = time_now
    data['groups'] = groups
    data['group_nums'] = group_nums
    data['nickname'] = nickname

    pagename = "status.html"
    img = await get_html_screenshots(pagename=pagename, data=data)
    msg = MessageSegment.image(img)
    await get_group_list.finish(msg)


group_status_regex = r"^(打开|关闭) [0-9]+$"
set_group_status = on_regex(pattern=group_status_regex, rule=check_event(
    group_list_event), permission=SUPERUSER, priority=2, block=True)


@set_group_status.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    '''管理员私聊打开关闭机器人'''
    text = event.get_plaintext()
    status, group_id = get_text_num(text)
    result = await set_robot_status(group_id, status)
    if result:
        msg = f"群（{group_id}）状态设置成功！"
    else:
        msg = f"未找到群（{group_id}），设置失败！"
    await set_group_status.finish(msg)


change_all_regex = r"^(打开|关闭)所有$"
change_all = on_regex(pattern=change_all_regex, rule=check_event(
    group_list_event), permission=SUPERUSER, priority=2, block=True)


@change_all.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    '''管理员私聊打开关闭所有'''
    text = event.get_plaintext()
    status = (text == "打开所有")
    await change_status_all(status)
    if status:
        msg = "所有群已打开机器人！"
    else:
        msg = "所有群已关闭机器人！"
    await change_all.finish(msg)


chat_event = ['message.private.friend', 'message.private.group']
chat = on_message(rule=check_event(chat_event), priority=9, block=True)


@chat.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    '''其他人私聊消息
    自动根据确定API
    '''
    if not PRIVATE_CHAT:
        await chat.finish()
    # 获得聊天内容
    text = event.get_plaintext()
    name = event.sender.nickname
    log = f'{name}（{event.user_id}）私聊闲聊：{text}'
    logger.info(log)

    # 使用jx3api访问
    msg = await get_reply_jx3(text)
    if msg is None:
        # 使用青云客访问
        msg = await get_reply_qingyunke(text)
        if msg is None:
            # 访问失败
            log = '接口访问失败，关闭事件。'
            logger.info(log)
            await chat.finish()

    log = f'接口返回：{msg}'
    logger.info(log)
    await chat.finish(msg)


set_group_leave_regex = r"^退群 [0-9]+$"
set_group_leave = on_regex(pattern=set_group_leave_regex, rule=check_event(
    chat_event), permission=SUPERUSER, priority=2, block=True)


@set_group_leave.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    '''私聊退群'''
    text = event.get_plaintext()
    group_id = int(text.split(' ')[-1])
    flag, group_name = await leave_group(group_id)
    if flag:
        await bot.set_group_leave(group_id=group_id, is_dismiss=True)
        msg = f'成功，已退出群：[{group_name}]({group_id})'
    else:
        msg = f'失败，未找到群：({group_id})。'
    await set_group_leave.finish(msg)


get_friend_regex = r"^好友列表$"
get_friend = on_regex(pattern=get_friend_regex, rule=check_event(
    chat_event), permission=SUPERUSER, priority=2, block=True)


@get_friend.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    '''获取好友列表'''
    self_id = event.self_id
    friend_list = await bot.get_friend_list()
    friends = []
    for friend in friend_list:
        if self_id == friend.get('user_id'):
            continue
        one_friend = {}
        one_friend['user_name'] = friend.get('nickname')
        one_friend['user_id'] = friend.get('user_id')
        friends.append(one_friend)
    data = {}
    data['friends'] = friends
    data['nickname'] = nickname
    data['friend_nums'] = len(friends)
    pagename = "friend.html"
    img = await get_html_screenshots(pagename, data)
    msg = MessageSegment.image(img)
    await get_friend.finish(msg)


detele_friend_regex = r"^删除好友 [0-9]+$"
detele_friend = on_regex(pattern=detele_friend_regex, rule=check_event(
    chat_event), permission=SUPERUSER, priority=2, block=True)


@detele_friend.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    '''私聊删好友'''

    text = event.get_plaintext()
    user_id = int(text.split(' ')[-1])
    friend_list = await bot.get_friend_list()
    flag = False
    user_name = ""
    for friend in friend_list:
        if user_id == friend.get('user_id'):
            flag = True
            user_name = friend.get('nickname')
            break

    if flag:
        try:
            await bot.call_api(api="delete_friend", id=user_id)
            msg = f'成功，删除好友：{user_name}({user_id})。'
        except Exception as e:
            msg = f'删除好友失败：{e}'
    else:
        msg = f'失败，未找到好友：({user_id})。'
    await detele_friend.finish(msg)