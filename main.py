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

# ✅ Function to send a welcome message when the user requests to join the channel
async def send_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    chat = update.chat_join_request.chat
    logger.info(f"Join request from {user.full_name} in {chat.title}")

    welcome_text = f"""
👋 Hi {user.first_name}!

Welcome to 👑 *{chat.title}* 👑 

🏆 Join our VVIP and Get daily Sureshots 🏆 

〰〰〰〰〰〰〰〰〰〰〰〰〰〰

▪️ 8–15 accurate signals (96% win rate)

▪️ Get Non MTG signals everyday 🦁

▪️ Fast deposit & withdrawal ♻️

▪️ Free giveaways & strategies 📊

▪️ Personal support anytime ✅

▪️ My personal 1000$ course free ✅

▪️ If any signals loss instant refund ✅

💵 Start making profit today 💵

〰〰〰〰〰〰〰〰〰〰〰〰〰〰

(1) Register from this link ⬇️

👉 https://broker-qx.pro/sign-up/?lid=1231115

(2) Deposit minimum $30 or above 💱

(3) Send your Trader ID : @vallyadmin ✅️

𝗟𝗲𝘁'𝘀 𝗴𝗿𝗼𝘄 𝘁𝗼𝗴𝗲𝘁𝗵𝗲𝗿 😎 🤝
"""

    keyboard = [
        [InlineKeyboardButton("👨‍💼 Admin", url="https://t.me/vallyadmin?text=Hello%F0%9F%91%8B%20Vally%20Trader%2C%20I%20want%20to%20Join%20your%20VVIP")]
    ]
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

# ✅ Function to send a welcome message with an image when the bot is started
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    try:
        # Send the image first
        with open("welcome.jpg", "rb") as image:  # Replace with your actual image file
            await context.bot.send_photo(chat_id=user.id, photo=InputFile(image))

        # Send the start message
        start_message = f"""
👋 Hello {user.first_name}

🔥 Welcome To “Wayne Traders” 🔥

✅ This Bot Will Lead You How You Can Make $300 To $600 Per Day For Free.

📌 Start The Bot To Join Our Free Telegram Channel.

😇 Select The Option Below.
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

# ✅ Function to detect when user leaves/kicked & send farewell DM
async def handle_member_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member = update.chat_member
    user = chat_member.from_user
    status = chat_member.new_chat_member.status

    if chat_member.chat.id != CHANNEL_ID:
        return

    if status in ['left', 'kicked']:
        logger.info(f"{user.full_name} left or was kicked from the channel.")
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=f"Goodbye {user.first_name}! 👋\nSorry to see you leave *{chat_member.chat.title}*.",
                parse_mode="Markdown"
            )
            logger.info(f"Sent farewell message to {user.full_name}")
        except Exception as e:
            logger.warning(f"Couldn't send farewell DM to {user.full_name}: {e}")

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
