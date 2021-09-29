import re
from typing import Optional, Tuple

import httpx
from src.modules.group_info import GroupInfo
from src.utils.config import config as baseconfig
from src.utils.user_agent import get_user_agent

from .config import zhiye_name

config = baseconfig.get('jx3-api')


async def get_server(bot_id: int, group_id: int) -> Optional[str]:
    '''
    获取绑定服务器名称
    '''
    return await GroupInfo.get_server(bot_id, group_id)


async def ger_master_server(server: str) -> Optional[str]:
    '''
    获取主服务器名称
    '''
    url: str = config.get('master-server')
    async with httpx.AsyncClient(headers=get_user_agent()) as client:
        params = {
            "name": server
        }
        try:
            req_url = await client.get(url, params=params)
            req = req_url.json()
            if req['code'] == 200:
                data = req['data']
                return data['server']
        except Exception:
            return None


def get_equipquery_name(text: str) -> Tuple[Optional[str], str]:
    '''处理查询装备'''
    text_list = text.split(' ')
    if len(text_list) == 2:
        name = text_list[1]
        server = None
    else:
        server = text_list[1]
        name = text_list[2]
    return server, name


def get_macro_name(text: str) -> str:
    '''宏查询返回职业'''
    args = re.search(r'^[\u4e00-\u9fa5]+宏$', text)
    if args is not None:
        return text[:-1]
    else:
        return text.split(' ')[-1]


def get_qixue_name(text: str) -> str:
    '''奇穴查询返回职业'''
    args = re.search(r'^[\u4e00-\u9fa5]+奇穴$', text)
    if args is not None:
        return text[:-2]
    else:
        return text.split(' ')[-1]


def get_medicine_name(text: str) -> str:
    '''小药查询返回职业'''
    args = re.search(r'^[\u4e00-\u9fa5]+小药$', text)
    if args is not None:
        return text[:-2]
    else:
        return text.split(' ')[-1]


def get_peizhuang_name(text: str) -> str:
    '''配装查询返回职业'''
    args = re.search(r'^[\u4e00-\u9fa5]+配装$', text)
    if args is not None:
        return text[:-2]
    else:
        return text.split(' ')[-1]


def get_gonglue_name(text: str) -> str:
    '''攻略查询返回'''
    args = re.search(r'^[\u4e00-\u9fa5]+攻略$', text)
    if args is not None:
        return text[:-2]
    else:
        return text.split(' ')[-1]


def get_xinfa(name: str) -> str:
    '''获取心法名称'''
    for key, xinfa in zhiye_name.items():
        for one_name in xinfa:
            if one_name == name:
                return key

    # 未找到，返回原值
    return name
