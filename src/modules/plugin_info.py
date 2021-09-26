from typing import Optional

from tortoise import fields
from tortoise.models import Model


class PluginInfo(Model):
    '''
    插件管理表
    '''
    id = fields.IntField(pk=True, generated=True)
    module_name = fields.CharField(max_length=255)
    '''
    插件名称
    '''
    description = fields.CharField(max_length=255, default='')
    '''
    插件描述
    '''
    group_id = fields.IntField()
    '''
    QQ群号
    '''
    status = fields.BooleanField(default=True)
    '''
    插件状态
    '''

    class Meta:
        table = "plugin_info"
        table_description = "处理插件"

    @classmethod
    async def get_status(cls, module_name: str, group_id: int) -> Optional[bool]:
        '''
        :说明
            返回插件开关

        :参数
            * module_name：插件模块名称
            * group_id：QQ群号

        :返回
            * bool：当前插件开关状态
        '''
        record = await cls.get_or_none(module_name=module_name, group_id=group_id)
        return None if record is None else record.status

    @classmethod
    async def change_status(cls, module_name: str, group_id: int, status: bool) -> None:
        '''
        :说明
            设置插件开启状态

        :参数
            * module_name：插件模块名称
            * group_id：QQ群号
            * status：开关状态
        '''
        record = await cls.get_or_none(module_name=module_name, group_id=group_id)
        if record is not None:
            record.status = status
            await record.save(update_fields=["status"])
        else:
            raise Exception

    @classmethod
    async def append_or_update(cls, module_name: str, description: str,  group_id: int) -> None:
        '''
        :说明
            增加，或更新一条数据

        :参数
            * module_name：插件模块名
            * description：插件描述
            * group_id：QQ群号
        '''
        record, _ = await cls.get_or_create(module_name=module_name, group_id=group_id)
        record.description = description
        await record.save(update_fields=["description"])

    @classmethod
    async def set_group_status(cls, group_id: int, status: bool) -> None:
        '''
        :说明
            设置某个群所有插件状态

        :参数
            * group_id：QQ群号
            * status：插件状态
        '''
        await cls.filter(group_id=group_id).update(status=status)

    @classmethod
    async def set_module_status(cls, module_name: str, status: bool) -> None:
        '''
        :说明
            设置某个插件全局状态

        :参数
            * module_name：插件模块名
            * status：插件状态
        '''
        await cls.filter(module_name=module_name).update(status=status)

    @classmethod
    async def get_all_status_from_group(cls, group_id: int) -> list[dict]:
        '''
        :说明
            返回某个群的所有插件状态

        :参数
            * group_id：QQ群号

        :返回

            * list[dict]：dict字段：module_name，description，status
        '''
        req: list[dict] = []
        record_list = await cls.filter(group_id=group_id)
        for record in record_list:
            reqdict = {}
            reqdict['module_name'] = record.module_name
            reqdict['description'] = record.description
            reqdict['status'] = record.status
            req.append(reqdict)
        return req

    @classmethod
    async def deltele_group(cls, group_id: int) -> None:
        '''删除一个群插件'''
        record_list = await cls.filter(group_id=group_id)
        for record in record_list:
            await record.delete()