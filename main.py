import asyncio

# === Render Python 3.14 Event Loop Fix (Must be at the absolute top) ===
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
# =======================================================================

import os
import re
import random
import string
import aiohttp
import datetime
from aiohttp import web
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant
from motor.motor_asyncio import AsyncIOMotorClient
import certifi

API_ID = 20579940
API_HASH = "6fc0ea1c8dacae05751591adedc177d7"
BOT_TOKEN = "8747542624:AAHeBJr-gMWldDWqaOlIIzm9oKl9hJCYlbE"
OWNER_ID = [6703335929, 5136260272]
MONGO_URI = "mongodb+srv://dxsimu:mnbvcxzdx@dxsimu.0qrxmsr.mongodb.net/?appName=dxsimu"
BOT_USERNAME = "Darkchainxbot"

ALLOWED_GROUPS = ["Dark_Zone_x", "DARK_GANG369"]

app = Client("DarkChainBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

db_client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
db = db_client["DARK-CHAIN"]
users_col = db["users"]
groups_col = db["groups"]
sudos_col = db["sudos"]
suspend_col = db["suspended"]
posts_col = db["posts"]

fontMap = {
    'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ғ','g':'ɢ','h':'ʜ','i':'ɪ','j':'ᴊ','k':'ᴋ','l':'ʟ','m':'ᴍ',
    'n':'ɴ','o':'ᴏ','p':'ᴘ','q':'ǫ','r':'ʀ','s':'s','t':'ᴛ','u':'ᴜ','v':'ᴠ','w':'ᴡ','x':'x','y':'ʏ','z':'ᴢ',
    'A':'ᴀ','B':'ʙ','C':'ᴄ','D':'ᴅ','E':'ᴇ','F':'ғ','G':'ɢ','H':'ʜ','I':'ɪ','J':'ᴊ','K':'ᴋ','L':'ʟ','M':'ᴍ',
    'N':'ɴ','O':'ᴏ','P':'ᴘ','Q':'ǫ','R':'ʀ','S':'s','T':'ᴛ','U':'ᴜ','V':'ᴠ','W':'ᴡ','X':'x','Y':'ʏ','Z':'ᴢ'
}

def fancy_text(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    
    url_pattern = r'(https?://\S+|www\.\S+)'
    parts = re.split(url_pattern, text)
    
    final_text = ""
    for part in parts:
        if part:
            if re.match(url_pattern, part):
                final_text += part  
            else:
                final_text += "".join(fontMap.get(c, c) for c in part)  
                
    return final_text

RANDOM_EMOJIS = ['🔥','💎','⚡','🌟','🌀','🛡️','🔮','📡','💥','🌌','🔑','🧬']

async def is_sudo(user_id):
    if user_id in OWNER_ID: return True
    sudo = await sudos_col.find_one({"uid": user_id})
    return bool(sudo)

def generate_token():
    nums = ''.join(random.choices(string.digits, k=5))
    text = ''.join(random.choices(string.ascii_letters, k=10))
    return f"dark-chain{nums}-{text}"

def get_ist_time():
    ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    return datetime.datetime.now(ist).strftime("%d-%m-%Y %H:%M")

async def get_target_id(message: Message):
    if message.reply_to_message:
        return message.reply_to_message.from_user.id
    if len(message.command) > 1:
        target = message.command[1]
        if target.isdigit(): return int(target)
        if target.startswith("@"):
            try:
                user = await app.get_users(target)
                return user.id
            except: pass
    return None

async def delete_after(msg, delay: int):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

def build_token_message(token: str, rtime: str) -> str:
    return f"<b>┏━━━「 ᴛᴏᴋᴇɴ 」━━┓\n┃🧪 ʏᴏᴜʀ ᴘʀɪᴠᴀᴛᴇ ᴛᴏᴋᴇɴ \n┗──────────╼\n┃ ʀᴇsᴇᴛ ᴛɪᴍᴇ: <code>{rtime}</code>\n┗──────────╼\n┃ 🔗 ᴛᴏᴋᴇɴ \n┃<code>{token}</code>\n┗━━━━━━━━━━━┛</b>"

def get_profile_text(user_data):
    profile_msg = (
        f"<b>┏━━「 📊 {fancy_text('PROFILE')} 」━━┓\n"
        f"┃ 👤 {fancy_text('NAME')}: {fancy_text(user_data.get('name', 'N/A'))}\n"
        f"┃ 🆔 {fancy_text('UID')}: <code>{user_data.get('uid', 'N/A')}</code>\n"
        f"┣━━━━━━━━━━\n"
        f"┃ 🚻 {fancy_text('GENDER')}: {fancy_text(user_data.get('gender', 'N/A'))}\n"
        f"┃ 🎖️ {fancy_text('POST')}: {fancy_text(user_data.get('post', 'N/A'))}\n"
        f"┃ 🎮 {fancy_text('HOBBY')}: {fancy_text(user_data.get('hobby', 'N/A'))}\n"
        f"┃ 📱 {fancy_text('WP')}: {user_data.get('wp', 'N/A')}\n"
        f"┃ 🔗 {fancy_text('LOYAL')}: <a href='{user_data.get('loyal', '')}'>Link</a>\n"
    )
    known_keys = {'_id', 'uid', 'token', 'reset_time', 'image', 'name', 'gender', 'post', 'hobby', 'date', 'loyal', 'wp'}
    for k, v in user_data.items():
        if k not in known_keys and k not in ['https', 'http']:
            emoji = random.choice(RANDOM_EMOJIS)
            profile_msg += f"┃ {emoji} {fancy_text(k.upper())}: {fancy_text(v)}\n"
    profile_msg += f"┗━━━━━━━━━━┛</b>"
    return profile_msg

async def upload_to_catbox(file_path):
    url = "https://catbox.moe/user/api.php"
    try:
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('reqtype', 'fileupload')
                data.add_field('fileToUpload', f, filename=os.path.basename(file_path))
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        return await response.text()
    except Exception as e:
        print(f"Catbox Upload Error: {e}")
    return None

async def send_token_with_copy_button(chat_id, text, token, uid):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    reply_markup = {
        "inline_keyboard": [
            [{"text": "📋 ᴄᴏᴘʏ ᴛᴏᴋᴇɴ", "copy_text": {"text": token}}],
            [{"text": "🔄 ʀᴇsᴇᴛ ᴛᴏᴋᴇɴ", "callback_data": f"reset_token_{uid}"}]
        ]
    }
    payload = {
        "chat_id": chat_id, "text": text, "parse_mode": "HTML", "reply_markup": reply_markup
    }
    async with aiohttp.ClientSession() as session:
        await session.post(url, json=payload)

async def edit_token_with_copy_button(chat_id, message_id, text, token, uid):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    reply_markup = {
        "inline_keyboard": [
            [{"text": "📋 ᴄᴏᴘʏ ᴛᴏᴋᴇɴ", "copy_text": {"text": token}}],
            [{"text": "🔄 ʀᴇsᴇᴛ ᴛᴏᴋᴇɴ", "callback_data": f"reset_token_{uid}"}]
        ]
    }
    payload = {
        "chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML", "reply_markup": reply_markup
    }
    async with aiohttp.ClientSession() as session:
        await session.post(url, json=payload)

async def ping_self():
    port = int(os.environ.get('PORT', 8080))
    URL = os.environ.get('RENDER_EXTERNAL_URL', f"http://localhost:{port}")
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(URL) as response:
                    pass
        except Exception as e: 
            pass
        await asyncio.sleep(300)

async def web_server():
    async def handle(request):
        return web.Response(text="Dark-Chain Bot is running perfectly!")
    app_web = web.Application()
    app_web.router.add_get('/', handle)
    runner = web.AppRunner(app_web)
    await runner.setup()
    port = int(os.environ.get('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port} for Render.")

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    if len(message.command) > 1 and message.command[1] == "token":
        await send_token(client, message)
    else:
        img_url = "https://graph.org/file/286753969727cb5f0d33f-e24fd829b618d7d740.jpg"
        caption_text = f"<b>{fancy_text('Welcome to Dark-Chain Bot! Use to /xmenu see commands.')}</b>"
        
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(fancy_text("🧪 TOKEN"), callback_data="btn_token"),
                InlineKeyboardButton(fancy_text("👤 PROFILE"), callback_data="btn_profile")
            ]
        ])
        
        await message.reply_photo(photo=img_url, caption=caption_text, reply_markup=markup)

@app.on_callback_query(filters.regex(r"^(btn_token|btn_profile)$"))
async def start_buttons_handler(client, callback_query):
    uid = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    if callback_query.data == "btn_token":
        user = await users_col.find_one({"uid": uid})
        if not user:
            btn = InlineKeyboardMarkup([[InlineKeyboardButton("👤 ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ", user_id=OWNER_ID[0])]])
            await callback_query.message.reply_text(f"<b>{fancy_text('You are not registered. Contact Admin.')}</b>", reply_markup=btn)
            return await callback_query.answer()
        
        sus = await suspend_col.find_one({"uid": uid})
        if sus: 
            await callback_query.message.reply_text(f"<b>{fancy_text('Your account is suspended!')}</b>")
            return await callback_query.answer()

        rtime = user.get('reset_time', get_ist_time())
        msg_text = build_token_message(user['token'], rtime)
        await send_token_with_copy_button(chat_id, msg_text, user['token'], uid)
        await callback_query.answer()
        
    elif callback_query.data == "btn_profile":
        user_data = await users_col.find_one({"uid": uid})
        if not user_data:
            await callback_query.message.reply_text(f"<b>{fancy_text('User not found in database.')}</b>")
            return await callback_query.answer()
        
        profile_msg = get_profile_text(user_data)

        if user_data.get('image'):
            try:
                await callback_query.message.reply_photo(photo=user_data['image'], caption=profile_msg)
            except:
                await callback_query.message.reply_text(profile_msg)
        else:
            await callback_query.message.reply_text(profile_msg)
        await callback_query.answer()

@app.on_message(filters.new_chat_members)
async def bot_added(client, message):
    for member in message.new_chat_members:
        if member.id == app.me.id:
            is_allowed = False
            if message.chat.username and message.chat.username in ALLOWED_GROUPS:
                is_allowed = True
            elif str(message.chat.id) in ALLOWED_GROUPS or message.chat.id in ALLOWED_GROUPS:
                is_allowed = True
                
            if not is_allowed:
                leave_msg = f"<b>{fancy_text('I am a private bot for Dark Gang. I am not allowed in this group. Leaving...')}</b>"
                await message.reply_text(leave_msg)
                await app.leave_chat(message.chat.id)
                return
            
            await groups_col.update_one({"chat_id": message.chat.id}, {"$set": {"chat_id": message.chat.id}}, upsert=True)
            bot_username = app.me.username
            btn = InlineKeyboardMarkup([[InlineKeyboardButton("✨ Add as Admin ✨", url=f"http://t.me/{bot_username}?startgroup=true&admin=invite_users+manage_video_chats+pin_messages+delete_messages+restrict_members")]])
            msg = f"<b>{fancy_text('Thanks for adding me! Please make me an admin using the button below to function properly.')}</b>"
            await message.reply_text(msg, reply_markup=btn)

@app.on_message(filters.command("xmenu"))
async def xmenu_command(client, message):
    if await is_sudo(message.from_user.id):
        menu = (
            f"┏━━「🛠️ {fancy_text('OWNER & SUDO MENU')}」━━┓\n"
            f"┃\n"
            f"┣🔹 <b>/xmenu</b> : <i>{fancy_text('Show this command menu.')}</i>\n"
            f"┣🔹 <b>/dark</b> : <i>{fancy_text('Register a new user to the database. (Sudo only)')}</i>\n"
            f"┣🔹 <b>/remove</b> : <i>{fancy_text('Remove user via ID/WP (Usage: /remove uid).')}</i>\n"
            f"┣🔹 <b>/search</b> : <i>{fancy_text('Find users via keyword (Usage: /search name).')}</i>\n"
            f"┣🔹 <b>/suspend</b> : <i>{fancy_text('Suspend a user (Usage: /suspend @user B/S/X).')}</i>\n"
            f"┣🔹 <b>/broadcast</b> : <i>{fancy_text('Send message to all users/groups.')}</i>\n"
            f"┣🔹 <b>/token</b> : <i>{fancy_text('View or reset private token.')}</i>\n"
            f"┣🔹 <b>/profile</b> : <i>{fancy_text('View user profile details.')}</i>\n"
            f"┣🔹 <b>/post</b> : <i>{fancy_text('Add special post for notifications.')}</i>\n"
            f"┣🔹 <b>/posts</b> : <i>{fancy_text('List all special posts.')}</i>\n"
            f"┣🔹 <b>/edit</b> : <i>{fancy_text('Edit user data in database.')}</i>\n"
            f"┣🔹 <b>/sudo</b> : <i>{fancy_text('Add sudo (owner only) / view list.')}</i>\n"
            f"┣🔹 <b>/rm</b> : <i>{fancy_text('Remove sudo (owner only).')}</i>\n"
            f"┃\n"
            f"┗━━━━━━━━━━━━━━━━┛"
        )
    else:
        menu = (
            f"┏━━「📜 {fancy_text('USER COMMAND MENU')}」━━┓\n"
            f"┃\n"
            f"┣🔹 <b>/xmenu</b> : <i>{fancy_text('Show this command menu.')}</i>\n"
            f"┣🔹 <b>/token</b> : <i>{fancy_text('View or reset your private token in DM.')}</i>\n"
            f"┣🔹 <b>/profile</b> : <i>{fancy_text('View your profile details.')}</i>\n"
            f"┃\n"
            f"┗━━━━━━━━━━━━━━━━┛"
        )
    await message.reply_text(menu)

@app.on_message(filters.command("dark"))
async def register_dark(client, message):
    if not await is_sudo(message.from_user.id):
        return await message.reply_text(f"<b>{fancy_text('Only Owner and Sudo users can use this command.')}</b>")

    text = message.caption if message.photo else message.text

    if not text or len(text.split()) == 1:
        usage = f"<b>{fancy_text('Usage of /dark command:')}</b>\n\n"
        usage += "<code>/dark\nuid: your_id\nName: your_name\nGender: male/female\nPost: ruler\nHobby: fighter\nDate: 2023\nloyal: url\nWP: number\nCity: Kolkata\nAnyExtra: value</code>\n\n"
        usage += f"<i>{fancy_text('💡 Tip: You can send a photo with this text in the caption to auto-upload the profile image, or put [profile](link) in the text!')}</i>"
        return await message.reply_text(usage)
    
    data = {}
    
    if message.photo:
        wait_msg = await message.reply_text(f"<b>{fancy_text('Uploading image to Catbox... Please wait.')}</b>")
        file_path = await message.download()
        catbox_url = await upload_to_catbox(file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        data['image'] = catbox_url if catbox_url else ""
        await wait_msg.delete()
    else:
        img_match = re.search(r'\[profile\]\((.*?)\)', text, re.IGNORECASE)
        data['image'] = img_match.group(1).strip() if img_match and img_match.group(1).strip() else ""
    
    clean_text = re.sub(r'^/dark\s*', '', text, flags=re.IGNORECASE)
    clean_text = re.sub(r'\[profile\]\(.*?\)', '', clean_text, flags=re.IGNORECASE).strip()
    
    for match in re.finditer(r'([a-zA-Z0-9_]+):\s*(.+?)(?=\n[a-zA-Z0-9_]+:|$)', clean_text, re.DOTALL):
        key = match.group(1).strip().lower()
        val = match.group(2).strip()
        if key not in ['https', 'http']:
            data[key] = val
    
    data['uid'] = int(data.get('uid', message.from_user.id)) if str(data.get('uid', '')).isdigit() else message.from_user.id
    data['token'] = generate_token()
    data['reset_time'] = get_ist_time()
    data = {k: v for k, v in data.items() if v}
    
    await users_col.update_one({"uid": data['uid']}, {"$set": data}, upsert=True)
    await message.reply_text(f"<b>{fancy_text('Successfully registered to Dark-Chain database! Extra fields saved.')}</b>")

@app.on_message(filters.command("remove"))
async def remove_user(client, message):
    if not await is_sudo(message.from_user.id): return
    if len(message.command) < 2:
        return await message.reply_text(f"<b>{fancy_text('Usage: /remove [User ID or WP Number]')}</b>")
    
    query = message.command[1].strip()
    uid_query = int(query) if query.isdigit() else query
    
    user = await users_col.find_one({"$or": [{"uid": uid_query}, {"wp": query}]})
    if not user:
        return await message.reply_text(f"<b>{fancy_text('User not found in database.')}</b>")
    
    await users_col.delete_one({"_id": user["_id"]})
    await message.reply_text(f"<b>{fancy_text(f'User {user.get('name', query)} successfully removed from database!')}</b>")

@app.on_message(filters.command("search"))
async def search_users(client, message):
    if not await is_sudo(message.from_user.id): return
    if len(message.command) < 2:
        return await message.reply_text(f"<b>{fancy_text('Usage: /search [keyword]')}</b>")
    
    query = " ".join(message.command[1:]).strip()
    search_regex = {"$regex": query, "$options": "i"}
    
    found_users = await users_col.find({
        "$or": [
            {"name": search_regex},
            {"post": search_regex},
            {"hobby": search_regex},
            {"wp": search_regex},
            {"city": search_regex},
            {"gender": search_regex},
            {"loyal": search_regex}
        ]
    }).to_list(length=None)
    
    if not found_users:
        return await message.reply_text(f"<b>{fancy_text('No users found matching:')} {query}</b>")
        
    await message.reply_text(f"<b>{fancy_text(f'Found {len(found_users)} users. Sending profiles...')}</b>")
    
    for user_data in found_users:
        profile_msg = get_profile_text(user_data)
        if user_data.get('image'):
            try:
                await message.reply_photo(photo=user_data['image'], caption=profile_msg)
            except:
                await message.reply_text(profile_msg)
        else:
            await message.reply_text(profile_msg)
        await asyncio.sleep(0.5)

@app.on_message(filters.command("token") & filters.private)
async def send_token(client, message):
    user = await users_col.find_one({"uid": message.from_user.id})
    if not user:
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("👤 ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ", user_id=OWNER_ID[0])]])
        return await message.reply_text(f"<b>{fancy_text('You are not registered. Contact Admin.')}</b>", reply_markup=btn)
    
    sus = await suspend_col.find_one({"uid": message.from_user.id})
    if sus: return await message.reply_text(f"<b>{fancy_text('Your account is suspended!')}</b>")

    rtime = user.get('reset_time', get_ist_time())
    msg_text = build_token_message(user['token'], rtime)
    await send_token_with_copy_button(message.chat.id, msg_text, user['token'], message.from_user.id)

@app.on_callback_query(filters.regex(r"^reset_token_"))
async def reset_token_callback(client, callback_query):
    user_id = int(callback_query.data.split("_")[2])
    if callback_query.from_user.id != user_id:
        return await callback_query.answer("Not your token!", show_alert=True)
    new_token = generate_token()
    new_time = get_ist_time()
    await users_col.update_one({"uid": user_id}, {"$set": {"token": new_token, "reset_time": new_time}})
    
    new_text = build_token_message(new_token, new_time)
    await edit_token_with_copy_button(callback_query.message.chat.id, callback_query.message.id, new_text, new_token, user_id)

@app.on_message(filters.regex(r"dark-chain\d{5}-[a-zA-Z]+"))
async def detect_token(client, message):
    token_match = re.search(r"(dark-chain\d{5}-[a-zA-Z]+)", message.text)
    if not token_match: return
    token = token_match.group(1)
    user_data = await users_col.find_one({"token": token})
    if not user_data: return

    if message.chat.type != "private":
        try:
            await message.delete()
        except: pass
        
        profile_msg = get_profile_text(user_data)

        if user_data.get('image'):
            profile_sent = await app.send_photo(message.chat.id, user_data['image'], caption=profile_msg)
        else:
            profile_sent = await app.send_message(message.chat.id, profile_msg)
        
        asyncio.create_task(delete_after(profile_sent, 60))
        
        new_token = generate_token()
        new_t
