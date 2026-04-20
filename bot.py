import os
import logging
import json
from collections import deque
from dotenv import load_dotenv
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from openai import OpenAI

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize OpenAI client for OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Memory to store conversation history (max 10 messages per user/group)
# In a production environment, use a database like SQLite or Redis
memory = {}

def get_memory(chat_id):
    if chat_id not in memory:
        memory[chat_id] = deque(maxlen=10)
    return memory[chat_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I am your AI Study Assistant and Group Moderator. "
        "I can help you with your studies, answer questions, and keep this group safe. "
        "Just send me a message or use /image <prompt> to generate an image!"
    )

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a prompt for the image. Example: /image a futuristic library")
        return
    
    prompt = " ".join(context.args)
    await update.message.reply_text(f"Generating image for: '{prompt}'... Please wait.")
    
    try:
        # Using OpenAI's DALL-E 3 via OpenRouter
        response = client.images.generate(
            model="openai/dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response.data[0].url
        await update.message.reply_photo(photo=image_url)
    except Exception as e:
        logging.error(f"Image generation error: {e}")
        await update.message.reply_text("Sorry, I couldn't generate the image. Make sure your prompt is safe and try again.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    user_text = update.message.text
    user_name = update.effective_user.first_name

    # 1. Moderation Check
    moderation_prompt = (
        f"Analyze this message for abuse, danger, or unwanted content: '{user_text}'. "
        "Reply with 'SAFE' if it's okay, or 'REJECT' if it's abusive, dangerous, or unwanted. "
        "If it's extremely abusive or dangerous, reply with 'BAN'."
    )
    try:
        mod_response = client.chat.completions.create(
            model="google/gemini-2.0-flash-lite-preview-02-05:free",
            messages=[{"role": "user", "content": moderation_prompt}]
        )
        mod_result = mod_response.choices[0].message.content.upper()
        
        if "REJECT" in mod_result or "BAN" in mod_result:
            # Delete the message
            await update.message.delete()
            
            if update.effective_chat.type in [constants.ChatType.GROUP, constants.ChatType.SUPERGROUP]:
                if "BAN" in mod_result:
                    # Ban the user from the group
                    await context.bot.ban_chat_member(chat_id, update.effective_user.id)
                    await context.bot.send_message(chat_id, f"User {user_name} has been banned for extreme policy violation.")
                else:
                    # Just warn and delete
                    await context.bot.send_message(chat_id, f"Message from {user_name} was removed due to policy violation.")
            return
    except Exception as e:
        logging.error(f"Moderation error: {e}")

    # 2. AI Response with Memory
    history = get_memory(chat_id)
    messages = [
        {"role": "system", "content": "You are a helpful AI Study Assistant. You provide clear, accurate, and educational answers. You remember previous parts of the conversation. If asked about your purpose, you are here to help with studies and moderate the group."}
    ]
    
    # Add history to messages
    for msg in history:
        messages.append(msg)
    
    # Add current message
    messages.append({"role": "user", "content": user_text})

    try:
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-lite-preview-02-05:free",
            messages=messages
        )
        ai_reply = response.choices[0].message.content
        
        # Update memory
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": ai_reply})
        
        await update.message.reply_text(ai_reply)
    except Exception as e:
        logging.error(f"AI Response error: {e}")
        await update.message.reply_text("Sorry, I encountered an error while processing your request.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    image_handler = CommandHandler('image', generate_image)
    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(image_handler)
    application.add_handler(msg_handler)
    
    print("Bot is running...")
    application.run_polling()
