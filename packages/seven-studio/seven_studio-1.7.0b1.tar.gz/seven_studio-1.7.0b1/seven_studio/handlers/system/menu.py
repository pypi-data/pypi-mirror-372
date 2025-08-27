"""
:Author: dongyu
:Date: 2020-04-11 18:44:08
:LastEditTime: 2025-08-26 18:33:00
:LastEditors: ChenXiaolei
:Description: 菜单相关类
"""
from seven_studio.handlers.studio_base import *
from seven_studio.models.db_models.menu.menu_cote_model import *
from seven_studio.models.db_models.menu.menu_info_model_ex import *
from seven_studio.models.power_model import *


class PowerPlatformMenuHandler(StudioBaseHandler):
    """
    :description: 权限的栏目菜单路由
    """
    @login_filter(True)
    def get_async(self):
        """
        :description: 根据登陆用户获取用户有权限的栏目菜单
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        # 数据库连接串
        manage_context_key = self.get_manage_context_key()
        # 是否超管
        is_super = self.get_is_super()
        # 当前用户id
        curr_user_id = self.request_user_id()
        # 产品id
        product_id = self.request_product_id()

        power_model = PowerModel(manage_context_key, is_super, curr_user_id, product_id)
        result = power_model.get_platform_power_menu_list()

        return self.response_json_success(result)


class PowerMenuTreeHandler(StudioBaseHandler):
    """
    :description: 菜单权限路由
    """
    @login_filter(True)
    def get_async(self):
        """
        :description: 获取权限树
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        manage_context_key = self.get_manage_context_key()
        is_super = self.get_is_super()
        curr_user_id = self.request_user_id()
        product_id = self.request_product_id()
        # 是否权限无限下放（0-无限等级，1-下放一级）
        power_grade = int(config.get_value("power_grade", 1))

        power_model = PowerModel(manage_context_key, is_super, curr_user_id, product_id)
        result = power_model.get_menu_item_tree()

        # 非超管则无权限下放功能，没有用户和角色添加权限
        if not is_super and power_grade > 0:
            result = [i for i in result if i['MenuID'] != config.get_value("menu_id_platform", "03E5D2A0-DB59-47F6-8F10-1ACDEFE9BDDD")]

        return self.response_json_success(result)


class MenuTreeHandler(StudioBaseHandler):
    """
    :description: 系统菜单路由
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 获取系统菜单树
        :param {type} 
        :return: 列表
        """
        manage_context_key = self.get_manage_context_key()
        curr_user_id = self.request_user_id()
        product_id = self.request_product_id()

        power_model = PowerModel(manage_context_key, True, curr_user_id, product_id)
        result = power_model.get_menu_item_tree(False)

        return self.response_json_success(result)


class MenuPowerInfoHandler(StudioBaseHandler):
    """
    :description: 栏目权限路由
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 栏目权限信息路由，用于获取栏目的角色和用户信息
        :param {type} 
        :return: 列表
        :last_editors: HuangJingCan
        """
        manage_context_key = self.get_manage_context_key()
        is_super = self.get_is_super()
        curr_user_id = self.request_user_id()
        product_id = self.request_product_id()

        power_model = PowerModel(manage_context_key, is_super, curr_user_id, product_id)
        result = power_model.get_power_menu_role_list(self.get_param("menuID"))

        return self.response_json_success(result)


class MenuCoteListHandler(StudioBaseHandler):
    """
    :description: 栏目数据路由
    """
    @login_filter(True)
    @power_filter(True)
    def post_async(self):
        """
        :description: 获取栏目数据列表
        :param {type} 
        :return: 列表
        :last_editors: HuangJingCan
        """
        page_index = self.get_page_index()
        page_size = self.get_page_size()
        condition, order = self.get_condition_by_body()

        p_dict, total = MenuCoteModel(self.get_manage_context_key()).get_dict_page_list("*", page_index, page_size, condition, "", order)

        return self.response_json_success(self.get_dict_page_info_list(page_index, page_size, p_dict, total))


class MenuCoteSelectHandler(StudioBaseHandler):
    """
    :description: MenuCoteSelectHandler
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: GetMenuCoteSelect
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        p_dict = MenuCoteModel(self.get_manage_context_key()).get_dict_list(field="MenuCoteID,CoteTitle")

        return self.response_json_success(p_dict)


class SaveMenuHandler(StudioBaseHandler):
    """
    :description: 保存菜单
    """
    @login_filter(True)
    @power_filter(True)
    def post_async(self):
        """
        :description: 保存菜单
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        # 菜单标识
        menu_id = self.get_param("id")
        # 父标识
        parent_id = self.get_param("parentID")
        # 菜单类型
        menu_type = self.get_param("menuType")
        # 图标地址
        menu_icon = self.get_param("menuIcon")
        # 菜单名称
        menu_name = self.get_param("menuName")
        # 是否显示0不显示1显示
        is_show = int(self.get_param("isShow", "0"))
        # 是否授权0不1是
        is_power = int(self.get_param("isPower", "0"))
        # 接口地址
        api_path = self.get_param("apiPath")
        # 视图地址
        view_path = self.get_param("viewPath")
        # 跳转地址
        target_url = self.get_param("targetUrl")
        # 菜单命令
        command_name = self.get_param("commandName")
        # 菜单参数
        command_parms = self.get_param("commandParms")
        # 1顶部2列表3底部
        button_place = self.get_param("buttonPlace")
        # 按钮颜色
        button_color = self.get_param("buttonColor")
        # 菜单显示条件
        show_condition_str = self.get_param("showConditionStr")
        # 栏目数据ID
        menu_cote_id = int(self.get_param("menuCoteID", "0"))
        # 栏目标识
        menu_cote_key = self.get_param("menuCoteKey")
        # 排序号
        sort_index = int(self.get_param("sortIndex", "0"))
        old_menu_name = ""

        # 验证数据
        if menu_name == "":
            return self.response_common("MenuNameEmpty", "菜单名为空")
        if [1, 2, 3].__contains__(menu_type):
            return self.response_common("MenuTypeError", "菜单类型错误")
        menu_info_model_ex = MenuInfoModelEx(self.get_manage_context_key())
        if menu_id != "":
            menu_info = menu_info_model_ex.get_entity_by_id(menu_id)
            if not menu_info:
                return self.response_common("NoExit", "菜单不存在")
            old_menu_name = menu_info.MenuName
        else:
            menu_info = MenuInfo()

        # 赋值保存
        menu_info.ParentID = parent_id
        menu_info.MenuType = menu_type
        menu_info.MenuIcon = menu_icon
        menu_info.MenuName = menu_name
        menu_info.IsShow = is_show
        menu_info.ApiPath = api_path
        menu_info.ViewPath = view_path
        menu_info.TargetUrl = target_url
        menu_info.IsPower = is_power
        menu_info.CommandName = command_name
        menu_info.CommandParms = command_parms
        menu_info.ButtonPlace = button_place
        menu_info.ButtonColor = button_color
        menu_info.ShowCondition = show_condition_str
        menu_info.MenuCoteID = menu_cote_id
        menu_info.MenuCoteKey = menu_cote_key
        menu_info.SortIndex = sort_index

        if menu_id == "":
            menu_info_model_ex.add_menu(menu_info)
        else:
            menu_info_model_ex.update_menu(menu_info)

        if old_menu_name and old_menu_name != menu_name:
            menu_info_model_ex.update_table(f"MenuNamePath=REPLACE(MenuNamePath,',{old_menu_name},',',{menu_name},')", f"IDPath LIKE '%{menu_id}%'")

        return self.response_json_success(menu_info)


class AddFastMenuHandler(StudioBaseHandler):
    """
    :description: 快速添加菜单
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 快速添加菜单-保存
        :return: 菜单id
        :last_editors: HuangJingCan
        """
        # 父栏目id
        parent_id = self.get_param("parentID")
        # 按钮类型
        button_type_str = self.get_param("buttonTypeStr")
        # 按钮名称后缀
        suffix_name = self.get_param("suffixName")

        if parent_id == "":
            return self.response_common("ParentIDEmpty", "父节点为空")
        if button_type_str == "":
            return self.response_common("ButtonTypeEmpty", "菜单类型为空")

        MenuInfoModelEx(self.get_manage_context_key()).add_fast_menu(parent_id, suffix_name, button_type_str)

        return self.response_json_success()


class DeleteMenuHandler(StudioBaseHandler):
    """
    :description: 删除菜单
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 删除菜单
        :param id：菜单id
        :return: 
        :last_editors: HuangJingCan
        """
        menu_id = self.get_param("id")
        if menu_id == "":
            return self.response_common("MenuIDEmpty", "菜单ID为空")

        MenuInfoModelEx(self.get_manage_context_key()).delete(menu_id)

        return self.response_json_success()


class SaveCopyMenuHandler(StudioBaseHandler):
    """
    :description: 复制粘贴菜单
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 复制粘贴菜单
        :param copyMenuID：复制的菜单id
        :param stickMenuID：粘贴的菜单id
        :return: 
        :last_editors: HuangJingCan
        """
        # 复制的菜单id
        copy_menu_id = self.get_param("copyMenuID")
        # 粘贴的菜单id
        stick_menu_id = self.get_param("stickMenuID")
        if copy_menu_id == "":
            return self.response_common("SaveCopyMenuHandler", "操作失败，复制节点为空")
        if stick_menu_id == "":
            return self.response_common("SaveCopyMenuHandler", "操作失败，粘贴节点为空")
        if copy_menu_id == stick_menu_id:
            return self.response_common("SaveCopyMenuHandler", "操作失败，无法粘贴到自身节点下")

        invoke_result = MenuInfoModelEx(self.get_manage_context_key()).add_copy_menu(copy_menu_id, stick_menu_id)
        if invoke_result.ResultCode != "0":
            return self.response_common("SaveCopyMenuHandler", invoke_result.ResultMessage)

        return self.response_json_success()


class MoveMenuHandler(StudioBaseHandler):
    """
    :description: 移动菜单
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 移动菜单
        :param id：被移动的菜单id
        :param targetId：目的地菜单id
        :param moveType：移动类型
        :return: 
        :last_editors: HuangJingCan
        """
        # 目的地菜单id
        target_id = self.get_param("targetId")
        # 移动类型
        move_type = self.get_param("moveType")
        # 被移动的菜单id
        menu_id = self.get_param("id")
        if menu_id == "":
            return self.response_common("MenuIDEmpty", "菜单ID为空")

        menu_info_model_ex = MenuInfoModelEx(self.get_manage_context_key())
        menu_info = menu_info_model_ex.get_entity_by_id(menu_id)

        if not menu_info:
            return self.response_common("NoExit", "菜单不存在")

        menu_info = menu_info_model_ex.get_entity_by_id(target_id)
        if menu_info and menu_info.MenuType == 1:
            return self.response_common("MoveMenuHandler", "移动失败，请勿移动到最外层")
        if menu_info and menu_info.MenuType == 3:
            return self.response_common("MoveMenuHandler", "移动失败，请勿移动到操作菜单下")

        if move_type == "inner":
            menu_info_model_ex.update_move(menu_id, target_id)
        elif move_type == "after":
            menu_info_model_ex.update_after_before_move(menu_id, target_id, "SortIndex", f"ParentID='{menu_info.ParentID}'")
        else:
            menu_info_model_ex.update_after_before_move(menu_id, target_id, "SortIndex", f"ParentID='{menu_info.ParentID}'", False)

        return self.response_json_success()


class SaveMenuCoteHandler(StudioBaseHandler):
    """
    :description: 修改栏目数据
    """
    @login_filter(True)
    @power_filter(True)
    def post_async(self):
        """
        :description: 保存栏目数据
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        # 栏目数据id
        menu_cote_id = int(self.get_param("MenuCoteID", "0"))
        # 栏目名称
        cote_title = self.get_param("CoteTitle")
        # 栏目表名
        cote_table_name = self.get_param("CoteTableName")
        # 主键名
        id_name = self.get_param("IDName")
        # 显示名称
        name = self.get_param("Name")
        # 父节点标识
        parent_id_name = self.get_param("ParentIDName")
        # ID路经名称
        id_path_name = self.get_param("IDPathName")
        # 链接字符串
        connection_string_name = self.get_param("ConnectionStringName")
        # 根节点ID值
        root_id_value = self.get_param("RootIDValue")
        # ID类型1整型2字符串
        id_data_type = int(self.get_param("IDDataType", "0"))
        # 排序
        sort_Expression = self.get_param("SortExpression")
        # 条件
        condtion = self.get_param("Condtion")
        # 是否父节点链接
        is_paren_url = int(self.get_param("IsParentUrl", "0"))

        menu_cote_model = MenuCoteModel(self.get_manage_context_key())
        menu_cote = MenuCote()
        if menu_cote_id > 0:
            menu_cote = menu_cote_model.get_entity_by_id(menu_cote_id)
            if not menu_cote:
                return self.response_common("NoExit", "数据不存在")

        menu_cote.CoteTitle = cote_title
        menu_cote.CoteTableName = cote_table_name
        menu_cote.IDName = id_name
        menu_cote.Name = name
        menu_cote.ParentIDName = parent_id_name
        menu_cote.IDPathName = id_path_name
        menu_cote.ConnectionStringName = connection_string_name
        menu_cote.RootIDValue = root_id_value
        menu_cote.IDDataType = id_data_type
        menu_cote.SortExpression = sort_Expression
        menu_cote.Condtion = condtion
        menu_cote.IsParentUrl = is_paren_url

        if menu_cote.MenuCoteID > 0:
            menu_cote_model.update_entity(menu_cote)
        else:
            menu_cote_model.add_entity(menu_cote)

        return self.response_json_success(menu_cote)


class DeleteMenuCoteHandler(StudioBaseHandler):
    """
    :description: 删除栏目数据
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 删除栏目数据
        :param id：栏目数据id
        :return: 
        :last_editors: HuangJingCan
        """
        menu_cote_id = self.get_param("MenuCoteID")
        if menu_cote_id == "":
            return self.response_common("MenuCoteIDEmpty", "栏目数据ID为空")

        MenuCoteModel(self.get_manage_context_key()).del_entity("MenuCoteID=%s", menu_cote_id)

        return self.response_json_success()


class SyncSqlHandler(StudioBaseHandler):
    """
    :description: sql同步语句导出
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        # 栏目ID
        menu_id = self.get_param("menuID")
        if menu_id == "":
            return self.response_common("MenuIDEmpty", "栏目ID为空")

        sql = PowerModel().export_sql(menu_id)

        sql_file_name = config.get_value("export_sql_folder", "c:\\") + "SyncSql" + TimeHelper.get_now_format_time("%Y-%m-%d") + ".sql"
        with open(sql_file_name, 'a') as file_handle:
            file_handle.write("{}\n".format(sql))

        return self.response_json_success()


class InsertSqlHandler(StudioBaseHandler):
    """
    :description: sql插入语句导出
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        menu_id = self.get_param("menuID")
        if menu_id == "":
            return self.response_common("MenuIDEmpty", "栏目ID为空")

        sql = PowerModel().export_sql(menu_id, 1)

        sql_file_name = config.get_value("export_sql_folder", "c:\\") + "InsertSql" + TimeHelper.get_now_format_time("%Y-%m-%d") + ".sql"
        with open(sql_file_name, 'a') as file_handle:
            file_handle.write("{}\n".format(sql))

        return self.response_json_success()


class UpdateSqlHandler(StudioBaseHandler):
    """
    :description: sql更新语句导出
    """
    @login_filter(True)
    @power_filter(True)
    def get_async(self):
        """
        :description: 
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        menu_id = self.get_param("menuID")
        if menu_id == "":
            return self.response_common("MenuIDEmpty", "栏目ID为空")

        sql = PowerModel().export_sql(menu_id, 2)

        sql_file_name = config.get_value("export_sql_folder", "c:\\") + "UpdateSql" + TimeHelper.get_now_format_time("%Y-%m-%d") + ".sql"
        with open(sql_file_name, 'a') as file_handle:
            file_handle.write("{}\n".format(sql))

        return self.response_json_success()