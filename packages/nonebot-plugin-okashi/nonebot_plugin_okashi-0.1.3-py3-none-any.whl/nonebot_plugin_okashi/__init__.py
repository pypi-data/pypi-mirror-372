import logging
import re
import asyncio
import httpx
import nonebot
from nonebot import on_request
from nonebot.rule import Rule
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupRequestEvent
from nonebot.adapters.onebot.v11.message import MessageSegment

__plugin_meta__ = PluginMetadata(
    name='KIRAKIRA☆DOUGA入群验证',
    type='application',
    description='KIRAKIRA☆DOUGA入群验证！',
    homepage='https://github.com/NekoooDesu/nonebot-plugin-okashi',
    usage="通过判断用户入群提供的信息，通过 KiRAKiRA-Rosales 提供的 API 查询用户名验证入群",
    config={},
    extra={}
)

join_group = on_request(
    priority=1,
    block=True
)

async def get_username(uid: str) -> str:
    user_api = f'https://rosales.kirakira.moe/user/info?uid={uid}'
    async with httpx.AsyncClient() as client:
        resp = await client.get(user_api)
        data = resp.json()
        if data.get("success"):
            result = data.get("result", {})
            nickname = result.get("userNickname")
            if nickname:
                return nickname
            return result.get("username", "")
        return ""

async def check_comment(uid: str, invitation_code: str) -> bool:
    config = nonebot.get_driver().config
    uuid = getattr(config, "uuid", None)
    token = getattr(config, "token", None)
    logging.info(f"收到入群验证请求，uid={uid}, invitation_code={invitation_code}")
    if not uuid or not token:
        logging.error("uuid 或 token 未配置")
        return False
    verify_api = f'https://rosales.kirakira.moe/user/getUserByInvitationCode?invitationCode={invitation_code}'
    cookies = {"uuid": uuid, "token": token}
    async with httpx.AsyncClient() as client:
        resp = await client.get(verify_api, cookies=cookies)
        data = resp.json()
        logging.debug(f"后端返回数据: {data}")
        if data.get("success") and "userInfoResult" in data:
            result = str(data["userInfoResult"].get("uid")) == uid
            logging.info(f"验证结果: {result}")
            return result
        logging.warning("后端返回失败或缺少 userInfoResult")
        return False

@join_group.handle()
async def _grh(bot: Bot, event: GroupRequestEvent):
    if event.sub_type == 'add':
        comment = event.comment.strip().splitlines()[-1]
        match = re.search(r"(\d+)\s+([A-Za-z0-9\-]+)", event.comment)
        if match:
            uid, invitation_code = match.groups()
            if await check_comment(uid, invitation_code):
                await event.approve(bot)
                await asyncio.sleep(2)
                username = await get_username(uid)
                if username:
                    await bot.set_group_card(
                        group_id=event.group_id,
                        user_id=event.user_id,
                        card=f"{uid} {username}"
                    )
                else:
                    await bot.set_group_card(
                        group_id=event.group_id,
                        user_id=event.user_id,
                        card=f"{uid}"
                    )
                
                logging.info(f"<UNK>{uid}<UNK>{invitation_code}<UNK>")
                #await join_group.finish(MessageSegment.at(event.user_id) + f'\n欢迎加入群聊!\n请注意遵守群规，愉快地玩耍吧！')
            else:
                logging.warn(f'认证失败，uid={uid}, invitation_code={invitation_code}')
                await event.reject(bot, reason=f'id: {uid} 认证错误，请检查您输入的是否为正确的UID和邀请码')
        else:
            logging.warn(f'格式错误，comment={comment}')
            await event.reject(bot, reason='格式错误，请输入“UID [邀请码]” 如"123 KIRA-1234-1234"')
