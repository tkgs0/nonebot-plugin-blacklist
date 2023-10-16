import asyncio, random
from pathlib import Path
from typing import Literal

from nonebot import get_driver, on_command, on_notice
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    Event,
    MessageEvent,
    GroupMessageEvent,
    GroupBanNoticeEvent,
)
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg

import ujson as json

superusers = get_driver().config.superusers

file_path = Path() / 'data' / 'blacklist' / 'blacklist.json'
file_path.parent.mkdir(parents=True, exist_ok=True)

blacklist = (
    json.loads(file_path.read_text('utf-8'))
    if file_path.is_file()
    else {}
)


def save_blacklist() -> None:
    file_path.write_text(
        json.dumps(
            blacklist,
            ensure_ascii=False,
            escape_forward_slashes=False,
            indent=2
        ),
        encoding='utf-8'
    )


def check_self_id(self_id) -> str:
    self_id = f'{self_id}'

    if not blacklist.get(self_id):
        blacklist.update({
            self_id: {
            'grouplist': [],
            'userlist': [],
            'ban_auto_sleep': True
            }
        })
        save_blacklist()

    return self_id


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
def blacklist_processor(event: Event):
    self_id = check_self_id(event.self_id)

    if (uid := str(vars(event).get('user_id', None))) in superusers:
        return

    if (gid := str(vars(event).get('group_id', None))) and gid in blacklist[self_id]['grouplist']:
        logger.debug(f'群聊 {gid} 在 {self_id} 黑名单中, 忽略本次消息')
        raise IgnoredException('黑名单群组')
    elif uid in blacklist[self_id]['userlist']:
        logger.debug(f'用户 {uid} 在 {self_id} 黑名单中, 忽略本次消息')
        raise IgnoredException('黑名单用户')


def handle_msg(
    self_id,
    arg,
    mode: Literal['add', 'del'],
    type_: Literal['userlist', 'grouplist'],
) -> str:
    uids = arg.extract_plain_text().strip().split()
    if not uids:
        return '用法: \n拉黑(解禁)用户(群) qq qq1 qq2 ...'
    for uid in uids:
        if not is_number(uid):
            return '参数错误, id必须是数字..'
    msg = handle_blacklist(self_id, uids, mode, type_)
    return msg


def handle_blacklist(
    self_id,
    uids: list,
    mode: Literal['add', 'del'],
    type_: Literal['userlist', 'grouplist'],
) -> str:
    self_id = check_self_id(self_id)

    if mode == 'add':
        blacklist[self_id][type_].extend(uids)
        blacklist[self_id][type_] = list(set(blacklist[self_id][type_]))
        _mode = '拉黑'
    elif mode == 'del':
        blacklist[self_id][type_] = [uid for uid in blacklist[self_id][type_] if uid not in uids]
        _mode = '解禁'
    save_blacklist()
    _type = '用户' if type_ == 'userlist' else '群聊'
    return f"已{_mode} {len(uids)} 个{_type}: {', '.join(uids)}"


add_userlist = on_command('拉黑用户', aliases={'屏蔽用户'}, permission=SUPERUSER, priority=1, block=True)

@add_userlist.handle()
async def add_user_list(event: MessageEvent, arg: Message = CommandArg()):
    if uids := [at.data['qq'] for at in event.get_message()['at']]:
        msg = handle_blacklist(event.self_id, uids, 'add', 'userlist')
        await add_userlist.finish(msg)
    msg = handle_msg(event.self_id, arg, 'add', 'userlist')
    await add_userlist.finish(msg)


add_grouplist = on_command('拉黑群', aliases={'屏蔽群'}, permission=SUPERUSER, priority=1, block=True)

@add_grouplist.handle()
async def add_group_list(event: MessageEvent, arg: Message = CommandArg()):
    msg = handle_msg(event.self_id, arg, 'add', 'grouplist')
    await add_grouplist.finish(msg)


del_userlist = on_command('解禁用户', aliases={'解封用户'}, permission=SUPERUSER, priority=1, block=True)

@del_userlist.handle()
async def del_user_list(event: MessageEvent, arg: Message = CommandArg()):
    if uids := [at.data['qq'] for at in event.get_message()['at']]:
        msg = handle_blacklist(event.self_id, uids, 'del', 'userlist')
        await del_userlist.finish(msg)
    msg = handle_msg(event.self_id, arg, 'del', 'userlist')
    await del_userlist.finish(msg)


del_grouplist = on_command('解禁群', aliases={'解封群'}, permission=SUPERUSER, priority=1, block=True)

@del_grouplist.handle()
async def del_group_list(event: MessageEvent, arg: Message = CommandArg()):
    msg = handle_msg(event.self_id, arg, 'del', 'grouplist')
    await del_grouplist.finish(msg)


check_userlist = on_command('查看用户黑名单', permission=SUPERUSER, priority=1, block=True)

@check_userlist.handle()
async def check_user_list(event: MessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().strip()
    self_id = check_self_id(arg) if is_number(arg) else check_self_id(event.self_id)
    uids = blacklist[self_id]['userlist']
    await check_userlist.finish(f"{self_id}\n当前已屏蔽 {len(uids)} 个用户: {', '.join(uids)}")


check_grouplist = on_command('查看群聊黑名单', permission=SUPERUSER, priority=1, block=True)

@check_grouplist.handle()
async def check_group_list(event: MessageEvent, args: Message = CommandArg()):
    arg = args.extract_plain_text().strip()
    self_id = check_self_id(arg) if is_number(arg) else check_self_id(event.self_id)
    gids = blacklist[self_id]['grouplist']
    await check_grouplist.finish(f"{self_id}\n自觉静默: {'开' if blacklist[self_id]['ban_auto_sleep'] else '关'}\n当前已屏蔽 {len(gids)} 个群聊: {', '.join(gids)}")


add_group = on_command('/静默', permission=SUPERUSER, priority=1, block=True)

@add_group.handle()
async def add_group_(event: GroupMessageEvent):
    handle_blacklist(event.self_id, [f'{event.group_id}'], 'add', 'grouplist')
    await add_group.finish('那我先去睡觉了...')


del_group = on_command('/响应', permission=SUPERUSER, priority=1, block=True)

@del_group.handle()
async def del_group_(event: GroupMessageEvent):
    handle_blacklist(event.self_id, [f'{event.group_id}'], 'del', 'grouplist')
    await del_group.finish('呜......醒来力...')


add_all_group = on_command('拉黑所有群', aliases={'屏蔽所有群'}, permission=SUPERUSER, priority=1, block=True)

@add_all_group.handle()
async def add_all_group_(bot: Bot, event: MessageEvent):
    gl = await bot.get_group_list()
    gids = ['{group_id}'.format_map(g) for g in gl]
    handle_blacklist(event.self_id, gids, 'add', 'grouplist')
    await add_all_group.finish(f'已拉黑 {len(gids)} 个群聊')


del_all_group = on_command('解禁所有群', aliases={'解封所有群'}, permission=SUPERUSER, priority=1, block=True)

@del_all_group.handle()
async def del_all_group_(bot: Bot, event: MessageEvent):
    gl = await bot.get_group_list()
    gids = ['{group_id}'.format_map(g) for g in gl]
    handle_blacklist(event.self_id, gids, 'del', 'grouplist')
    await del_all_group.finish(f'已解禁 {len(gids)} 个群聊')


add_all_friend = on_command('拉黑所有好友', aliases={'屏蔽所有好友'}, permission=SUPERUSER, priority=1, block=True)

@add_all_friend.handle()
async def add_all_friend_(bot: Bot, event: MessageEvent):
    gl = await bot.get_friend_list()
    uids = ['{user_id}'.format_map(g) for g in gl]
    handle_blacklist(event.self_id, uids, 'add', 'userlist')
    await add_all_friend.finish(f'已拉黑 {len(uids)} 个用户')


del_all_friend = on_command('解禁所有好友', aliases={'解封所有好友'}, permission=SUPERUSER, priority=1, block=True)

@del_all_friend.handle()
async def del_all_friend_(bot: Bot, event: MessageEvent):
    gl = await bot.get_friend_list()
    uids = ['{user_id}'.format_map(g) for g in gl]
    handle_blacklist(event.self_id, uids, 'del', 'userlist')
    await del_all_friend.finish(f'已解禁 {len(uids)} 个用户')


reset_all_blacklist = on_command('重置所有黑名单', aliases={'清空所有黑名单'}, permission=SUPERUSER, priority=1, block=True)

@reset_all_blacklist.got('FLAG', prompt='确定重置所有黑名单? (y/n)')
async def reset_all_list(matcher: Matcher):
    flag = matcher.state['FLAG'].extract_plain_text().strip()
    if flag.lower() in ['y', 'yes', 'true']:
        blacklist.clear()
        save_blacklist()
        await reset_all_blacklist.finish('已重置所有黑名单')
    else:
        await reset_all_blacklist.finish('操作已取消')


reset_blacklist = on_command('重置黑名单', aliases={'清空黑名单'}, permission=SUPERUSER, priority=1, block=True)

@reset_blacklist.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    matcher.state["ARGS"] = args.extract_plain_text().strip()

@reset_blacklist.got('FLAG', prompt='确定重置黑名单? (y/n)')
async def reset_list(event: MessageEvent, matcher: Matcher):
    args = matcher.state['ARGS']
    flag = matcher.state['FLAG'].extract_plain_text().strip()

    uids = args.strip().split()
    uids = [check_self_id(i) for i in uids if is_number(i)] or [check_self_id(event.self_id)]

    if flag.lower() in ['y', 'yes', 'true']:
        for i in uids:
            blacklist.pop(i)
        save_blacklist()
        await reset_blacklist.finish(f'已重置{len(uids)}个黑名单')
    else:
        await reset_blacklist.finish('操作已取消')


@on_notice(priority=2, block=False).handle()
async def _(bot: Bot, event: GroupBanNoticeEvent):
    self_id = check_self_id(event.self_id)

    if event.is_tome() and event.duration:
        msg = f"在群聊 {event.group_id} 受到 {event.operator_id} 禁言"
        logger.info(f'{self_id} {msg}')
        if blacklist[self_id]['ban_auto_sleep']:
            handle_blacklist(self_id, [f'{event.group_id}'], 'add', 'grouplist')
            for superuser in bot.config.superusers:
                await bot.send_private_msg(
                    user_id=int(superuser),
                    message=f'ⓘ{msg}, 已自动拉黑该群聊.'
                )
                await asyncio.sleep(random.random()+1)


ban_auto_sleep = on_command('自觉静默', permission=SUPERUSER, priority=1, block=True)

@ban_auto_sleep.handle()
async def _(event: MessageEvent, arg: Message = CommandArg()):
    self_id = check_self_id(event.self_id)
    msg = arg.extract_plain_text().strip()

    if not msg or msg.startswith('开'):
        blacklist[self_id]['ban_auto_sleep'] = True
        text = '自觉静默已开启.'
    elif msg.startswith('关'):
        blacklist[self_id]['ban_auto_sleep'] = False
        text = '自觉静默已关闭.'
    else:
        return
    save_blacklist()
    await ban_auto_sleep.finish(text)
