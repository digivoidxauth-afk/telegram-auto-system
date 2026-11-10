import asyncio
import logging
import time

from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("telegram-auto-system")

SESSION_NAME = "telegram_user_session"
DM_COOLDOWN_SECONDS = max(0, int(getattr(config, "DM_COOLDOWN_SECONDS", 60)))
MIN_GROUP_INTERVAL_SECONDS = 3600  # Safety floor: at most one scheduled post per group per hour.

client = TelegramClient(SESSION_NAME, config.API_ID, config.API_HASH)
last_dm_reply = {}


@client.on(events.NewMessage(incoming=True))
async def handle_private_messages(event):
    if not getattr(config, "DM_AUTO_REPLY", False):
        return
    if not event.is_private or event.out or event.sender_id is None:
        return

    try:
        sender = await event.get_sender()
        if getattr(sender, "bot", False):
            return

        now = time.monotonic()
        previous = last_dm_reply.get(event.sender_id, 0)
        if now - previous < DM_COOLDOWN_SECONDS:
            return

        message = str(getattr(config, "DM_MESSAGE", "")).strip()
        if not message:
            log.warning("DM_MESSAGE is empty; skipping reply.")
            return

        await event.respond(message)
        last_dm_reply[event.sender_id] = now
        log.info("Sent DM auto-reply to user ID %s", event.sender_id)

    except FloodWaitError as exc:
        log.warning("Telegram requested a wait of %s seconds.", exc.seconds)
        await asyncio.sleep(exc.seconds)
    except Exception:
        log.exception("Could not process incoming private message.")


async def group_scheduler():
    if not getattr(config, "GROUP_AUTO_MESSAGE", False):
        log.info("Group auto-messaging is disabled.")
        return

    interval = int(getattr(config, "GROUP_INTERVAL", MIN_GROUP_INTERVAL_SECONDS))
    if interval < MIN_GROUP_INTERVAL_SECONDS:
        log.warning(
            "GROUP_INTERVAL was below 3600 seconds; using the 1-hour safety minimum."
        )
        interval = MIN_GROUP_INTERVAL_SECONDS

    group_ids = list(getattr(config, "GROUP_IDS", []))
    message = str(getattr(config, "GROUP_MESSAGE", "")).strip()

    if not group_ids:
        log.info("No GROUP_IDS configured; group scheduler is idle.")
        return
    if not message:
        log.warning("GROUP_MESSAGE is empty; group scheduler is idle.")
        return

    while True:
        for group_id in group_ids:
            try:
                await client.send_message(int(group_id), message)
                log.info("Sent scheduled message to configured group %s", group_id)
                await asyncio.sleep(2)
            except FloodWaitError as exc:
                log.warning("Telegram requested a wait of %s seconds.", exc.seconds)
                await asyncio.sleep(exc.seconds)
            except Exception:
                log.exception("Could not send to configured group %s", group_id)

        await asyncio.sleep(interval)


async def main():
    if not config.API_ID or not config.API_HASH:
        raise RuntimeError("Set API_ID and API_HASH in your local config.py first.")

    await client.start()
    me = await client.get_me()
    log.info("Logged in as %s (ID: %s)", getattr(me, "username", None), me.id)
    log.info("Session is stored locally in %s.session", SESSION_NAME)

    scheduler_task = asyncio.create_task(group_scheduler())
    try:
        await client.run_until_disconnected()
    finally:
        scheduler_task.cancel()
        await asyncio.gather(scheduler_task, return_exceptions=True)
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
