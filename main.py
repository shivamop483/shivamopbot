import logging
import os
import sys
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    ApplicationBuilder,
    ChatJoinRequestHandler,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
)
from aiohttp import web

# ✅ Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ✅ Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_PATH = "/telegram"
WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}{WEBHOOK_PATH}" if RENDER_EXTERNAL_URL else ""

app = None  # Global app reference for webhook processing

# ✅ Function to send a welcome message
async def send_welcome_message(user, chat, context):
    welcome_text = f"""
👋 Hey {user.first_name}, Welcome to 👑 *{chat.title}* 👑  

🔥 You’ve just joined the elite trading community of **Wayne Traders** – where success is the only option! 🔥  

🏆 **Join our VVIP and receive daily sureshots!** 🏆  

🚀 **Why choose Wayne Traders?**  
▪️ **8–15 accurate signals daily (96% win rate)**  
▪️ **Non-MTG signals every day 🦁**  
▪️ **Fast deposit & withdrawal ♻️**  
▪️ **Exclusive giveaways & winning strategies 📊**  
▪️ **24/7 personal support ✅**   

💵 **Start making profits today – don't miss out!** 💵  

(1) **Register from this link ⬇️**  
👉 [Sign Up Here](https://bit.ly/WayneFreeSignals)  

(2) **Deposit a minimum of $50 or above 💱**  

(3) **Send your Trader ID to:**  
👨‍💼 [@Wayne_Trader01](https://t.me/Wayne_Trader01) ✅  

🔗 **Let’s grow together and achieve financial freedom! 😎 🤝**
"""
    keyboard = [[InlineKeyboardButton("👨‍💼 Admin", url="https://t.me/Wayne_Trader01?text=Hello%F0%9F%91%8B%20Wayne%20Trader%2C%20I%20want%20to%20Join%20your%20VVIP")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=welcome_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        logger.info(f"Sent welcome message to {user.full_name}")
    except Exception as e:
        logger.warning(f"Couldn't send DM to {user.full_name}: {e}")

# ✅ Chat Join Request Handling
async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    chat = update.chat_join_request.chat
    await send_welcome_message(user, chat, context)

# ✅ User Joins without Request Handling
async def handle_member_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_member.from_user
    chat = update.chat_member.chat
    if update.chat_member.new_chat_member.status == "member":
        await send_welcome_message(user, chat, context)

# ✅ Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    with open("welcome.jpg", "rb") as image:
        await context.bot.send_photo(chat_id=user.id, photo=InputFile(image))

    start_message = f"""
👋 Hey {user.first_name}, Welcome!

🔥 You’ve just unlocked the gateway to **Wayne Traders** – your ticket to financial success! 🔥  

💰 Ready to make $300 to $600 per day for FREE? 💰  

🚀 This bot will guide you step by step to achieve consistent profits.

🔹 Join our exclusive trading community
🔹 Get expert insights & winning strategies
🔹 Start earning like a pro!

📌 Need assistance? Our admin is here to help!
👨‍💼 Admin Contact: [@Wayne_Trader01](https://t.me/Wayne_Trader01)  

👇 Click the button below to join our free Telegram channel now!
"""
    keyboard = [[InlineKeyboardButton("🔥 JOIN CHANNEL 🔥", url="https://t.me/+VMf10CU1Qf9mOTA1")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=user.id,
        text=start_message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
            logger.info(f"Sent start message to {user.full_name}")
    except Exception as e:
        logger.error(f"Failed to send start message to {user.full_name}: {e}")

# ✅ HTTP health check endpoint
async def handle_health(request):
    return web.Response(text="Bot is alive and running! 🚀")

# ✅ Telegram webhook handler
async def handle_telegram_webhook(request):
    try:
        data = await request.json()
        update = Update.de_json(data, app.bot)
        await app.process_update(update)
    except Exception as e:
        logger.error(f"Error processing update: {e}")
    return web.Response(text="OK")

# ✅ Run the aiohttp web server
async def run_web_server():
    port = int(os.environ.get('PORT', 10000))
    web_app = web.Application()
    web_app.router.add_get('/', handle_health)
    web_app.router.add_post(WEBHOOK_PATH, handle_telegram_webhook)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"HTTP server running on port {port}")

# ✅ Main function
async def main():
    global app
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ✅ Register handlers
    app.add_handler(CommandHandler("start", start))  # Start message
    app.add_handler(ChatJoinRequestHandler(send_welcome_message))  # Welcome message on join request
    app.add_handler(ChatMemberHandler(handle_member_status, ChatMemberHandler.CHAT_MEMBER))

    logger.info("Starting bot and setting webhook...")

    await app.initialize()
    await app.bot.set_webhook(WEBHOOK_URL)
    await app.start()

    # ✅ Start web server to receive webhook updates
    await run_web_server()

    # ✅ Keep running
    stop_event = asyncio.Event()
    await stop_event.wait()

    # ✅ Graceful shutdown
    await app.stop()
    await app.shutdown()

# ✅ Entry point
if __name__ == '__main__':
    if sys.platform.startswith('win') and sys.version_info[:2] >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
