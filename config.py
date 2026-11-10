# LOCAL CONFIGURATION
# Fill these values in Termux AFTER cloning the repository.
# Do not upload real credentials, messages containing private information,
# or your Telegram session file to GitHub.

API_ID = 123456
API_HASH = "PASTE_YOUR_API_HASH_HERE"

# Private-message auto-reply
DM_AUTO_REPLY = True
DM_MESSAGE = "Hello! Thanks for your message. I will reply when I am available."
DM_COOLDOWN_SECONDS = 60  # At most one automatic reply per sender per minute.

# Scheduled group message
GROUP_AUTO_MESSAGE = True
GROUP_IDS = [
    # Add numeric IDs only for groups where you have permission to post.
    # Example: -1001234567890,
]
GROUP_MESSAGE = "Your scheduled group message goes here."
GROUP_INTERVAL = 3600  # Seconds. The program enforces a minimum of 1 hour.
