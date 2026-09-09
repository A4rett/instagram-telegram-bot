import telebot
import instaloader
import time
import threading
import os
import sys

TOKEN = os.environ.get('BOT_TOKEN')

if not TOKEN:
    print("❌ هەڵە: تۆکنی تیلیگرام نەدۆزرایەوە!")
    sys.exit()

bot = telebot.TeleBot(TOKEN)
user_data = {}

DELAY_BETWEEN_ACCOUNTS = 30
BATCH_SIZE = 10
DELAY_BETWEEN_BATCHES = 120

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('📋 لیستی کۆمبۆ (Combo)', '📍 گەڕان بەپێی شوێن (Location)')
    
    bot.send_message(
        message.chat.id, 
        "👋 بەخێربێیت!\n\nشێوازی کارکردن هەڵبژێرە:", 
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_mode_choice)

def process_mode_choice(message):
    chat_id = message.chat.id
    text = message.text
    
    if 'کۆمبۆ' in text:
        user_data[chat_id] = {'mode': 'combo'}
        bot.send_message(chat_id, "🎯 یوزەرنەیمی ئامانج (ئەو کەسەی کە لێی دەگەڕێیت) بنووسە:")
        bot.register_next_step_handler(message, process_target)
    elif 'شوێن' in text:
        user_data[chat_id] = {'mode': 'location'}
        bot.send_message(chat_id, "📍 ناوی شوێن یان هاشتاگ بنووسە (بۆ نموونە: halabja یان هەڵەبجە):")
        bot.register_next_step_handler(message, process_location_name)
    else:
        bot.send_message(chat_id, "❌ هەڵبژاردنەکە ناتەواوە. تکایە /start بنووسە.")

def process_location_name(message):
    chat_id = message.chat.id
    user_data[chat_id]['location'] = message.text.strip().replace('#', '').lower()
    
    bot.send_message(chat_id, "🎯 ئێستا یوزەرنەیمی ئامانج بنووسە:")
    bot.register_next_step_handler(message, process_target)

def process_target(message):
    chat_id = message.chat.id
    user_data[chat_id]['target'] = message.text.strip().replace('@', '')
    
    if user_data[chat_id].get('mode') == 'combo':
        bot.send_message(chat_id, "📄 لیستی کۆمبۆ بنووسە (هەر یوزەرێک لە دێڕێکدا):")
        bot.register_next_step_handler(message, process_combo_list)
    else:
        # ئەگەر شێوازی شوێن بوو، ڕاستەوخۆ داوای لۆگینی ئینستاگرام دەکەین بۆ ئەوەی خۆی پەیجەکان بدۆزێتەوە
        ask_login(chat_id)

def process_combo_list(message):
    chat_id = message.chat.id
    combo_list = [line.strip().replace('@', '') for line in message.text.split('\n') if line.strip()]
    
    if not combo_list:
        bot.send_message(chat_id, "❌ هیچ ناوێک نەدۆزرایەوە. /start بنووسە.")
        return
        
    user_data[chat_id]['combo'] = combo_list
    ask_login(chat_id)

def ask_login(chat_id):
    bot.send_message(chat_id, "🔑 یوزەرنەیمی ئەکاونتی ئینستاگرامی خۆت بنووسە بۆ لۆگین (ئەکاونتی فەیک):")
    bot.register_next_step_handler(message, process_ig_user)

def process_ig_user(message):
    chat_id = message.chat.id
    user_data[chat_id]['ig_user'] = message.text.strip()
    bot.send_message(chat_id, "پاسۆردی ئەکاونتەکە بنووسە:")
    bot.register_next_step_handler(message, process_ig_pass)

def process_ig_pass(message):
    chat_id = message.chat.id
    user_data[chat_id]['ig_pass'] = message.text.strip()
    
    bot.send_message(chat_id, "⚙️ زانیارییەکان وەرگیران. پڕۆسەکە دەست پێ دەکات...")
    t = threading.Thread(target=run_scraper, args=(chat_id,))
    t.start()

def run_scraper(chat_id):
    data = user_data.get(chat_id)
    if not data:
        return
        
    target = data['target']
    ig_user = data['ig_user']
    ig_pass = data['ig_pass']
    mode = data.get('mode')
    
    L = instaloader.Instaloader()
    
    try:
        bot.send_message(chat_id, "⏳ چوونەژوورەوە بۆ ئینستاگرام...")
        L.login(ig_user, ig_pass)
        bot.send_message(chat_id, "✅ سەرکەوتوو بوو!")
    except Exception as e:
        bot.send_message(chat_id, f"❌ هەڵە لە لۆگین: {e}")
        return

    # ئەگەر دۆخەکە Location بوو، لێرەدا خۆکارانە پەیجەکان دەدۆزینەوە
    if mode == 'location':
        loc_query = data['location']
        bot.send_message(chat_id, f"🔍 گەڕان بەدوای ئەکاونتەکان بۆ شوێنی: {loc_query} ...")
        combo = []
        try:
            hashtag = instaloader.Hashtag.from_name(L.context, loc_query)
            for post in hashtag.get_posts():
                owner = post.owner_profile
                if not owner.is_private and owner.username not in combo:
                    combo.append(owner.username)
                if len(combo) >= 15: # سنووردارکردن بۆ خێرایی
                    break
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ هەڵە لە دۆزینەوەی پەیجەکان بەپێی شوێن: {e}")
            return
            
        if not combo:
        
            bot.send_message(chat_id, "❌ هیچ ئەکاونتێکی پبلیک لەو شوێنە نەدۆزرایەوە.")
            return
        bot.send_message(chat_id, f"📄 {len(combo)} ئەکاونت دۆزرانەوە. دەست بە پشکنین دەکرێت...")
    else:
        combo = data['combo']

    total = len(combo)
    found_in = []
    
    for index, acc in enumerate(combo, start=1):
        bot.send_message(chat_id, f"🔍 [{index}/{total}] پشکنینی: @{acc}")
        
        try:
            profile = instaloader.Profile.from_username(L.context, acc)
            is_found = False
            for follower in profile.get_followers():
                if follower.username.lower() == target.lower():
                    is_found = True
                    break
                    
            if is_found:
                bot.send_message(chat_id, f"✅ دۆزرایەوە! @{target} فۆڵۆوی @{acc} ـی کردووە.")
                found_in.append(acc)
            else:
                bot.send_message(chat_id, "❌ نەدۆزرایەوە.")
                
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ نەتوانرا @{acc} بپشکنرێت: {e}")

        if index < total:
            if index % BATCH_SIZE == 0:
                bot.send_message(chat_id, f"💤 پشووی {DELAY_BETWEEN_BATCHES} چرکە بۆ پاراستنی ئەکاونتەکە...")
                time.sleep(DELAY_BETWEEN_BATCHES)
            else:
                time.sleep(DELAY_BETWEEN_ACCOUNTS)
                
    result_text = "🎉 پڕۆسەی پشکنین کۆتایی هات!\n\n"
    if found_in:
        result_text += f"یوزەری @{target} لەم ئەکاونتانەدا دۆزرایەوە:\n"
        for f in found_in:
            result_text += f"✔️ @{f}\n"
    else:
        result_text += f"یوزەری @{target} لە هیچ کام لە پەیجەکاندا نەدۆزرایەوە."
        
    bot.send_message(chat_id, result_text)

print("بۆتەکە کەوتە کار...")
bot.infinity_polling()
