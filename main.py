
import asyncio
import logging
import time

from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

log = logging.getLogger("telegram-auto-system")

SESSION_NAME = "telegram_user_session"
MIN_GROUP_INTERVAL = 300  # 5 minutes

client = TelegramClient(
    SESSION_NAME,
    config.API_ID,
    config.API_HASH
)

last_dm_reply = {}


# ==============================
# PRIVATE MESSAGE AUTO-REPLY
# ==============================

@client.on(events.NewMessage(incoming=True))
async def handle_private_messages(event):

    if not config.DM_AUTO_REPLY:
        return

    if not event.is_private or event.out:
        return

    if event.sender_id is None:
        return

    try:
        sender = await event.get_sender()

        if getattr(sender, "bot", False):
            return

        now = time.monotonic()

        cooldown = max(
            0,
            int(config.DM_COOLDOWN_SECONDS)
        )

        previous = last_dm_reply.get(event.sender_id, 0)

        if now - previous < cooldown:
            return

        message = config.DM_MESSAGE.strip()

        if not message:
            return

        await event.respond(message)

        last_dm_reply[event.sender_id] = now

        log.info("DM auto-reply sent.")

    except FloodWaitError as exc:
        log.warning("Telegram rate limit: waiting %s seconds", exc.seconds)
        await asyncio.sleep(exc.seconds)

    except Exception:
        log.exception("DM reply error")


# ==============================
# GROUP SCHEDULED MESSAGES
# ==============================

async def group_scheduler():

    if not config.GROUP_AUTO_MESSAGE:
        log.info("Group automation disabled.")
        return

    interval = int(config.GROUP_INTERVAL)

    if interval < MIN_GROUP_INTERVAL:
        log.warning(
            "Minimum group interval is 300 seconds. "
            "Using 300 seconds."
        )
        interval = MIN_GROUP_INTERVAL

    groups = list(config.GROUP_IDS)
    message = config.GROUP_MESSAGE.strip()

    if not groups:
        log.info("No groups configured.")
        return

    if not message:
        log.warning("Group message is empty.")
        return

    log.info("Group scheduler started.")
    log.info("Configured interval: %s seconds", interval)

    while True:

        for group_id in groups:

            try:
                await client.send_message(
                    int(group_id),
                    message
                )

                log.info(
                    "Scheduled message sent to group %s",
                    group_id
                )

                await asyncio.sleep(3)

            except FloodWaitError as exc:

                log.warning(
                    "Telegram requested a wait of %s seconds",
                    exc.seconds
                )

                await asyncio.sleep(exc.seconds)

            except Exception:
                log.exception(
                    "Could not send message to group %s",
                    group_id
                )

        await asyncio.sleep(interval)


# ==============================
# MAIN
# ==============================

async def main():

    if not config.API_ID or not config.API_HASH:
        raise RuntimeError("Telegram API credentials missing.")

    await client.start()

    me = await client.get_me()

    log.info(
        "Logged in successfully: %s",
        me.id
    )

    scheduler = asyncio.create_task(group_scheduler())

    try:
        await client.run_until_disconnected()

    finally:
        scheduler.cancel()

        await asyncio.gather(
            scheduler,
            return_exceptions=True
        )

        await client.disconnect()


if __name__ == "__main__":

    asyncio.run(main())
