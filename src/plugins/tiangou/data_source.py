from typing import Optional

import httpx
from src.utils.config import config as baseconfig
from src.utils.log import logger
from src.utils.user_agent import get_user_agent

config = baseconfig.get('jx3-api')


async def get_tiangou() -> Optional[str]:
    '''
    :说明
        获取一条舔狗日记

    :返回
        * `str`：获取内容
        * `None`：转换出错
    '''

    url: str = config.get('tiangou')

    async with httpx.AsyncClient(headers=get_user_agent()) as client:
        try:
            req_url = await client.get(url=url)
            req = req_url.json()
            if req['code'] == 200:
                data = req['data']
                text = data['text']
                log = f"请求日记成功：{text}"
                logger.debug(log)
                return text
            else:
                log = f'请求日记出错：{req["msg"]}'
                logger.debug(log)
                return None
        except Exception as e:
            log = f'请求链接失败，原因：{e}'
            logger.error(log)
            return None