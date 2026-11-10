# Telegram Auto-Reply and Scheduled Group Messages

A small Python user-client project intended to run locally in Termux on Android.

## Features

- Replies to incoming private messages using `DM_MESSAGE`.
- Sends a configured scheduled message to explicitly listed groups.
- Keeps the Telegram login session on the local device.
- Uses a per-sender DM cooldown.
- Enforces a minimum one-hour interval between scheduled group-message cycles.

## Important

- Use this only with your own account and in groups where you have permission to post.
- Tell people when an automated reply is being used where appropriate.
- Avoid repetitive or unwanted messages. Respect group rules and Telegram limits.
- Do not share your Telegram session file. It can provide access to your account.
- Never commit your real `config.py`, API credentials, or `*.session` files.
- The repository contains a placeholder `config.py`; `.gitignore` excludes it for Git-based uploads. If using GitHub's website, do not upload your filled-in local config.

## Setup

1. Clone/download this repository.
2. Install Python dependencies: `pip install -r requirements.txt`
3. Edit the local `config.py` with your Telegram API ID/hash, reply text, group IDs, and interval.
4. Run: `python main.py`
5. On first run, sign in to your Telegram account when prompted. The session is saved locally.

## Configuration

- `DM_AUTO_REPLY`: enable/disable private-message auto-replies.
- `DM_MESSAGE`: private-message response.
- `DM_COOLDOWN_SECONDS`: cooldown per sender.
- `GROUP_AUTO_MESSAGE`: enable/disable scheduled group messages.
- `GROUP_IDS`: numeric IDs of groups where you are allowed to post.
- `GROUP_MESSAGE`: scheduled group message.
- `GROUP_INTERVAL`: seconds between group-message cycles (minimum enforced by the program: 3600 seconds).

The group scheduler sends one cycle after startup, then waits for the configured interval before the next cycle.

## Notes

This starter does not automatically discover groups, message strangers, or respond to replies to group announcements. Those can be considered separately if needed.
