from pathlib import Path
from typing import Literal

from nonebot import get_driver, logger, on_command
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageEvent,
    PokeNotifyEvent,
    GroupMessageEvent,
)
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg

try:
    import ujson as json
except ModuleNotFoundError:
    import json

superusers = get_driver().config.superusers

file_path = Path() / "data" / "blacklist" / "blacklist.json"
file_path.parent.mkdir(parents=True, exist_ok=True)

blacklist = (
    json.loads(file_path.read_text("utf-8"))
    if file_path.is_file()
    else {"grouplist": [], "userlist": []}
)



def save_blacklist() -> None:
    file_path.write_text(json.dumps(blacklist), encoding="utf-8")



def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False



@event_preprocessor
def blacklist_processor_poke(event: PokeNotifyEvent):
    uid = str(event.user_id)
    if uid in superusers:
        return
    if isinstance(event, GroupMessageEvent) and str(event.group_id) in blacklist["grouplist"]:
        logger.debug(f"群聊 {event.group_id} 在黑名单中, 忽略本次消息")
        raise IgnoredException("黑名单群组")
    elif uid in blacklist["userlist"]:
        logger.debug(f"用户 {uid} 在黑名单中, 忽略本次消息")
        raise IgnoredException("黑名单用户")



@event_preprocessor
def blacklist_processor(event: MessageEvent):
    uid = str(event.user_id)
    if uid in superusers:
        return
    if isinstance(event, GroupMessageEvent) and str(event.group_id) in blacklist["grouplist"]:
        logger.debug(f"群聊 {event.group_id} 在黑名单中, 忽略本次消息")
        raise IgnoredException("黑名单群组")
    elif uid in blacklist["userlist"]:
        logger.debug(f"用户 {uid} 在黑名单中, 忽略本次消息")
        raise IgnoredException("黑名单用户")



def handle_blacklist(
    arg,
    mode: Literal["add", "del"],
    type_: Literal["userlist", "grouplist"],
) -> str:
    uids = arg.extract_plain_text().strip().split()
    if not uids:
        return "用法: \n拉黑(解禁)用户(群) qq qq1 qq2 ..."
    for uid in uids:
        if not is_number(uid):
            return "参数错误, id必须是数字.."
    if mode == "add":
        blacklist[type_].extend(uids)
        blacklist[type_] = list(set(blacklist[type_]))
        _mode = "拉黑"
    elif mode == "del":
        blacklist[type_] = [uid for uid in blacklist[type_] if uid not in uids]
        _mode = "解禁"
    save_blacklist()
    _type = "用户" if type_ == "userlist" else "群聊"
    return f"已{_mode} {len(uids)} 个{_type}: {', '.join(uids)}"




add_userlist = on_command("拉黑用户", aliases={"屏蔽用户"}, permission=SUPERUSER, priority=1, block=True)

@add_userlist.handle()
async def add_user_list(arg: Message = CommandArg()):
    msg = handle_blacklist(arg, "add", "userlist")
    await add_userlist.finish(msg)



add_grouplist = on_command("拉黑群", aliases={"屏蔽群"}, permission=SUPERUSER, priority=1, block=True)

@add_grouplist.handle()
async def add_group_list(arg: Message = CommandArg()):
    msg = handle_blacklist(arg, "add", "grouplist")
    await add_grouplist.finish(msg)



del_userlist = on_command("解禁用户", aliases={"解封用户"}, permission=SUPERUSER, priority=1, block=True)

@del_userlist.handle()
async def del_user_list(arg: Message = CommandArg()):
    msg = handle_blacklist(arg, "del", "userlist")
    await del_userlist.finish(msg)



del_grouplist = on_command("解禁群", aliases={"解封群"}, permission=SUPERUSER, priority=1, block=True)

@del_grouplist.handle()
async def del_group_list(arg: Message = CommandArg()):
    msg = handle_blacklist(arg, "del", "grouplist")
    await del_grouplist.finish(msg)



check_userlist = on_command("查看用户黑名单", permission=SUPERUSER, priority=1, block=True)

@check_userlist.handle()
async def check_user_list():
    await check_userlist.finish(f"当前已屏蔽{len(blacklist['userlist'])}个用户: {', '.join(blacklist['userlist'])}")



check_grouplist = on_command("查看群聊黑名单", permission=SUPERUSER, priority=1, block=True)

@check_grouplist.handle()
async def check_group_list():
    await check_grouplist.finish(f"当前已屏蔽{len(blacklist['grouplist'])}个群聊: {', '.join(blacklist['grouplist'])}")



def add_gid(gid):
    blacklist["grouplist"].append(gid)
    blacklist["grouplist"] = list(set(blacklist["grouplist"]))
    save_blacklist()
    return "那我先睡觉了..."
def del_gid(gid):
    blacklist["grouplist"] = [uid for uid in blacklist["grouplist"] if not uid == gid]
    save_blacklist()
    return "呜......醒来力..."



add_group = on_command("/静默", permission=SUPERUSER, priority=1, block=True)

@add_group.handle()
async def add_group_(event: GroupMessageEvent):
    msg = add_gid(str(event.group_id))
    await add_group.finish(msg)



del_group = on_command("/响应", permission=SUPERUSER, priority=1, block=True)

@del_group.handle()
async def del_group_(event: GroupMessageEvent):
    msg = del_gid(str(event.group_id))
    await del_group.finish(msg)

