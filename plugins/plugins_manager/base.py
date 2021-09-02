from nonebot.plugin import get_loaded_plugins
from utils.log import logger
import os


class PluginBase():
    '''
    插件管理器，基础类
    '''
    module_name: str
    '''
    模块名
    '''
    plugin_name: str
    '''
    插件名
    '''
    plugin_usage: str
    '''
    插件用法
    '''

    def __init__(self, module_name: str, plugin_name: str, plugin_usage: str):
        self.module_name = module_name
        self.plugin_name = plugin_name
        self.plugin_usage = plugin_usage


PluginManager: list[PluginBase] = []
'''
插件管理器，列表
'''


def manager_init() -> None:
    '''
    插件管理器初始化函数
    '''
    logger.debug('正在注册插件管理器')
    global PluginManager
    plugins_list = get_loaded_plugins()

    # 获取本模块名
    _, self_module = os.path.split(os.path.split(__file__)[0])

    for plugin in plugins_list:
        # 跳过本模块
        if plugin.name == self_module:
            continue

        # 设置插件
        try:
            # 跳过手动忽略的模块
            ignore = plugin.export['ignore']
            if ignore:
                continue

            module_name = plugin.name
            plugin_name = plugin.export['plugin_name']
            usage = plugin.export['plugin_usage']
            one = PluginBase(module_name, plugin_name, usage)
            PluginManager.append(one)
        except Exception:
            continue
    logger.debug('插件管理器注册完成')
