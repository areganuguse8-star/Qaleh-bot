
🖤ᬼ𑲭 ✞𖣔ꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋ🤫𝙙𝙖𝙣𝙞 ᬼ⃝:
import os
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.executor import start_webhook
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import google.generativeai as genai

# 1. መሠረታዊ ቅንብሮች (Configuration)
API_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Render ላይ በሰላም እንዲነሳ የWebhook ቅንብር
WEBHOOK_HOST = os.environ.get('RENDER_EXTERNAL_URL')  # በRender ራሱ የሚሰጥ URL
WEBHOOK_PATH = f'/webhook/{API_TOKEN}'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.environ.get('PORT', 8080))

# 2. የዳታቤዝ (SQLite) ዝግጅት ለንባብ መከታተያ
def init_db():
    conn = sqlite3.connect('qaleh_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracker (
            user_id INTEGER,
            chapter TEXT,
            status TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 3. የ AI (Gemini) ቅንብር
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# 4. የቦቱ ስቴቶች (FSM States)
class BotStates(StatesGroup):
    waiting_for_verse = State()
    waiting_for_track = State()
    chatting_with_ai = State()

# 5. የቁልፎች ማውጫ (Keyboards)
def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="📖 የጥናት ክፍል (Commentary)", callback_data="menu_study"),
        InlineKeyboardButton(text="📅 የእኔ መንፈሳዊ ጉዞ (Tracker)", callback_data="menu_tracker"),
        InlineKeyboardButton(text="💬 ከገጸ-ባህሪያት ጋር ውይይት (AI)", callback_data="menu_ai")
    )
    return keyboard

def tracker_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="📝 አዲስ የንባብ ምዕራፍ መዝግብ", callback_data="track_add"),
        InlineKeyboardButton(text="📊 የንባብ ታሪኬን አሳይ", callback_data="track_view"),
        InlineKeyboardButton(text="🔙 ወደ ዋና ማውጫ", callback_data="go_main")
    )
    return keyboard

def ai_characters_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="🐪 ነቢዩ ሙሴ", callback_data="ai_moses"),
        InlineKeyboardButton(text="👑 ንጉሥ ሰሎሞን", callback_data="ai_solomon"),
        InlineKeyboardButton(text="🔙 ወደ ዋና ማውጫ", callback_data="go_main")
    )
    return keyboard

# 6. የቦቱ መልእክት አስተናጋጆች (Handlers)

@dp.message_handler(commands=['start', 'help'], state='*')
async def send_welcome(message: types.Message, state: FSMContext):
    await state.finish()
    text = (
        f"ሰላም {message.from_user.first_name}! ወደ ቃልህ ቦት በደህና መጡ።\n"
        "«ቃልህ ለእግሬ መብራት፥ ለመንገዴም ብርሃን ነው» (መዝ 119:105)\n\n"
        "ለመቀጠል ከታች ካሉት አማራጮች አንዱን ይምረጡ፦"
    )
    await message.reply(text, reply_markup=main_menu(), parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data == 'go_main', state='*')
async def go_back_main(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.send_message(callback_query.from_user.id, "ዋና ማውጫ፦", reply_markup=main_menu())
    await callback_query.answer()

# --- ክፍል 1፦ የጥናት ክፍል (Commentary) ---
@dp.callback_query_handler(lambda c: c.data == 'menu_study', state='*')
async def start_study(callback_query: types.CallbackQuery):
    await BotStates.waiting_for_verse.set()
    await bot.send_message(
        callback_query.from_user.id, 
        "📖 ማብራሪያ የሚፈልጉትን ጥቅስ ይጻፉልኝ።\n(ለአሁኑ መሞከሪያ፡ ዮሐንስ 3:16 ወይም ሮሜ 8:28 ብለው ይጻፉ)"
    )
    await callback_query.answer()

@dp.message_handler(state=BotStates.waiting_for_verse)
async def give_commentary(message: types.Message, state: FSMContext):
    user_input = message.text.strip()
    
    # የጥቅሶች ማከማቻ (Mock Data)
    bible_data = {
        "ዮሐንስ 3:16": "«በእርሱ የሚያምን ሁሉ የዘላለም ሕይወት እንዲኖረው እንጂ እንዳይጠፋ እግዚአብሔር አንድያ ልጁን እስኪሰጥ ድረስ ዓለሙን እንዲሁ ወዶታልና።»\n\n💡 ማብራሪያ፦ ይህ ጥቅስ የመጽሐፍ ቅዱስ ልብ ይባላል። የእግዚአብሔርን ፍጹም ፍቅር፣ የክርስቶስን መስዋዕትነት እና በነፃ የሚገኘውን የዘላለም ሕይወት በአንድ ላይ ያሳያል።",
        "ሮሜ 8:28": "«እግዚአብሔርንም ለሚወዱት እንደ አሳቡም ለተጠሩት ነገር ሁሉ ለበጎ እንዲደረግ እናውቃለን።»\n\n💡 ማብራሪያ፦ በአማኝ ሕይወት ውስጥ የሚከሰቱ ማናቸውም ነገሮች (ደስ የሚሉም ሆነ የሚያዝኑ) እግዚአብሔር በመጨረሻ ለመልካም ነገር እንደሚቀይራቸው ትልቅ ተስፋ የሚሰጥ ክፍል ነው።"
    }
    
    response = bible_data.get(user_input, "⚠️ ይቅርታ፣ ያቀረቡት ጥቅስ አሁን ላይ በዳታቤዛችን ውስጥ አልተገኘም። በቅርቡ ይጨመራል!")
    await message.reply(response, reply_markup=main_menu())
    await state.finish()

# --- ክፍል 2፦ የንባብ መከታተያ (Tracker) ---
@dp.callback_query_handler(lambda c: c.data == 'menu_tracker', state='*')
async def open_tracker(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "📅 የእኔ መንፈሳዊ ጉዞ መከታተያ ገጽ። ምን ማድረግ ይፈልጋሉ?", reply_markup=tracker_menu())
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == 'track_add', state='*')
async def ask_track_input(callback_query: types.CallbackQuery):
    await BotStates.waiting_for_track.set()
    await bot.send_message(callback_query.from_user.id, "📝 ዛሬ ያነበቡትን መጽሐፍ እና ምዕራፍ ይጻፉ (ለምሳሌ፦ ኦሪት ዘፍጥረት ምዕራፍ 1)")
    await callback_query.answer()

@dp.message_handler(state=BotStates.waiting_for_track)
async def save_track(message: types.Message, state: FSMContext):
    chapter = message.text.strip()
    user_id = message.from_user.id
    
    conn = sqlite3.connect('qaleh_tracker.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tracker (user_id, chapter, status) VALUES (?, ?, ?)", (user_id, chapter, "የተነበበ"))
    conn.commit()
    conn.close()
    
    await message.reply(f"✅ ጥቅስ ስኬታማ በሆነ መንገድ ተመዝግቧል፦ *{chapter}*\nበርቱ! ቃሉን ማንበብዎን ይቀጥሉ ሰናይ ቀን።", parse_mode="Markdown", reply_markup=main_menu())
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == 'track_view', state='*')
async def view_tracks(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    conn = sqlite3.connect('qaleh_tracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT chapter, date FROM tracker WHERE user_id = ? ORDER BY date DESC LIMIT 5", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        text = "📊 እስካሁን ምንም የተመዘገበ የንባብ ታሪክ የሎትም። አሁን ማስታወሻ መያዝ ይጀምሩ!"
    else:
        text = "📊 የመጨረሻዎቹ 5 የንባብ ታሪኮችዎ፦\n\n"
        for row in rows:
            text += f"🔹 {row[0]} \n"
            
    await bot.send_message(callback_query.from_user.id, text, parse_mode="Markdown", reply_markup=tracker_menu())
    await callback_query.answer()

# --- ክፍል 3፦ ከገጸ-ባህሪያት ጋር ውይይት (AI) ---
@dp.callback_query_handler(lambda c: c.data == 'menu_ai', state='*')
async def open_ai_menu(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "💬 ለመነጋገር የሚፈልጉትን መጽሐፍ ቅዱሳዊ ገጸ-ባህሪ ይምረጡ፦", reply_markup=ai_characters_menu())
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith('ai_'), state='*')
async def select_character(callback_query: types.CallbackQuery, state: FSMContext):
    char_code = callback_query.data
    character_name = "ነቢዩ ሙሴ" if char_code == "ai_moses" else "ንጉሥ ሰሎሞን"
    
    await BotStates.chatting_with_ai.set()
    await state.update_data(character=character_name)
    
    await bot.send_message(
        callback_query.from_user.id, 
        f"💬 አሁን ከ {character_name} ጋር መነጋገር ይችላሉ። ማንኛውንም ጥያቄ ይጠይቁት! \n(ለመውጣት /start ይበሉ)"
    )
    await callback_query.answer()

@dp.message_handler(state=BotStates.chatting_with_ai)
async def chat_with_character(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    character = user_data.get('character', 'ሙሴ')
    user_msg = message.text
    
    if GEMINI_KEY:
        try:
            # ለAI ባህሪ የምንሰጠው ትዕዛዝ (System Prompt)
            prompt = (
                f"አንተ መጽሐፍ ቅዱሳዊው ገጸ-ባህሪ {character} ነህ። "
                f"ከተጠቃሚው ለሚቀርብልህ ጥያቄ ልክ እንደ እሱ ባህሪ ሆነህ በጥበብ፣ በትሕትና፣ "
                f"በመንፈሳዊ እውቀት እና በመጽሐፍ ቅዱስ ታሪክ ላይ ብቻ ተመስርተህ በአማርኛ ቋንቋ ምላሽ ስጥ።"
                f"\n\nተጠቃሚው የጠየቀህ ጥያቄ፦ {user_msg}"
            )
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            await message.reply(response.text)
        except Exception as e:
            await message.reply("⚠️ ይቅርታ፣ ከ AI ሰርቨር ጋር መገናኘት አልተቻለም። እባክዎን ቆይተው ይሞክሩ።")
    else:
        # የጌሚኒ ቁልፍ ከሌለ ቦቱ እንዳይበላሽ የመጠባበቂያ (Fallback) መልእክት
        fallback_responses = {
            "ነቢዩ ሙሴ": f"እኔ የእግዚአብሔር ባሪያ ሙሴ ነኝ። ስለ መራሁት ሕዝብ ወይስ ስለ ሕጉ ማወቅ የምትፈልገው ምንድን ነው? (ማሳሰቢያ፦ የ AI መገናኛ ቁልፍ ስላልተገጠመ የተሟላ ምላሽ መስጠት አልቻልኩም)።",
            "ንጉሥ ሰሎሞን": f"ሰላም ለአንተ ይሁን ልጄ። እግዚአብሔር ከሰጠኝ ጥበብ ምን ማወቅ ትሻለህ? (ማሳሰቢያ፦ የ AI መገናኛ ቁልፍ ስላልተገጠመ የተሟላ ምላሽ መስጠት አልቻልኩም)።"
        }
        await message.reply(fallback_responses.get(character))

# 7. ቦቱን በሰርቨር ላይ የማስነሻ መንገዶች (Webhook & Polling)
async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()

if name == 'main':
    if os.environ.get('RENDER_EXTERNAL_URL'):
        # በCloud/Render ላይ ሲሆን Webhook ይጠቀማል
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )
    else:
        # በኮምፒውተር ወይም በስልክ ለሙከራ Run ሲደረግ
        from aiogram import executor
        executor.start_polling(dp, skip_updates=True)
