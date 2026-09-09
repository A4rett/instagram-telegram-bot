import instaloader
import time
import sys

# ڕێکخستنی کاتەکان بۆ ئەوەی ئینستاگرام بلۆکمان نەکات
DELAY_BETWEEN_ACCOUNTS = 30  # ٣٠ چرکە وەستان لە نێوان هەر ئەکاونتێک
BATCH_SIZE = 10              # پشکنینی ١٠ ئەکاونت لە هەر قۆناغێکدا
DELAY_BETWEEN_BATCHES = 120  # ٢ خولەک وەستان لە نێوان قۆناغەکاندا

def load_combo_list(filename="combo.txt"):
    """خوێندنەوەی یوزەرنەیمەکان لە فایلی کۆمبۆوە"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            # پاککردنەوەی ناوەکان لە بۆشایی و نیشانەی @
            return [line.strip().replace('@', '') for line in file if line.strip()]
    except FileNotFoundError:
        print(f"❌ هەڵە: فایلی {filename} نەدۆزرایەوە.")
        sys.exit(1)

def main():
    print("=== سیستەمی گەڕان بەدوای یوزەر لەناو کۆمبۆ ===\n")
    
    # ١. وەرگرتنی زانیارییەکان
    target_user = input("یوزەرنەیمی ئامانج بنووسە (ئەو کەسەی کە لێی دەگەڕێیت): ").strip().replace('@', '')
    my_username = input("یوزەرنەیمی ئەکاونتەکەی خۆت بنووسە (بۆ لۆگین): ").strip()
    my_password = input("پاسۆردی ئەکاونتەکەی خۆت بنووسە: ").strip()

    # ٢. دروستکردنی پەیوەندی لەگەڵ ئینستاگرام
    L = instaloader.Instaloader()
    
    try:
        print("\n⏳ خەریکی چوونەژوورەوەم بۆ ئینستاگرام...")
        L.login(my_username, my_password)
        print("✅ بە سەرکەوتوویی چووە ژوورەوە!\n")
    except Exception as e:
        print(f"❌ هەڵە لە چوونەژوورەوە: {e}")
        sys.exit(1)

    # ٣. خوێندنەوەی لیستەکە
    combo_list = load_combo_list("combo.txt")
    total_accounts = len(combo_list)
    print(f"📄 {total_accounts} ئەکاونت لە فایلی کۆمبۆدا دۆزرایەوە.")
    
    found_in = [] # ئەو ئەکاونتانەی کە ئامانجەکەی تێدا دەدۆزرێتەوە لێرە هەڵدەگیرێت

    # ٤. لۆژیکی گەڕان و Batching
    for index, current_public_user in enumerate(combo_list, start=1):
        print(f"🔍 [{index}/{total_accounts}] پشکنینی فۆڵۆوەرەکانی: @{current_public_user}")
        
        try:
            # هێنانی زانیاری پڕۆفایلەکە
            profile = instaloader.Profile.from_username(L.context, current_public_user)
            
            # گەڕان بەناو فۆڵۆوەرەکاندا
            is_found = False
            for follower in profile.get_followers():
                if follower.username.lower() == target_user.lower():
                    is_found = True
                    break # دۆزرایەوە، پێویست ناکات بەردەوام بێت لە پشکنینی ئەم پەیجە
            
            if is_found:
                print(f"   ✅ دۆزرایەوە! @{target_user} فۆڵۆوی @{current_public_user} ـی کردووە.")
                found_in.append(current_public_user)
            else:
                print("   ❌ نەدۆزرایەوە.")
                
        except instaloader.exceptions.ProfileNotExistsException:
            print(f"   ⚠️ ئەکاونتی @{current_public_user} بوونی نییە یان سڕاوەتەوە.")
        except instaloader.exceptions.PrivateProfileNotFollowedException:
            print(f"   🔒 ئەکاونتی @{current_public_user} پرایڤەتە و ناتوانم بیپشکنم.")
        except Exception as e:
            print(f"   ⚠️ هەڵەیەک ڕوویدا لە کاتی پشکنینی @{current_public_user}: {e}")

        # سیستەمی وەستان (Rate Limiting) بۆ ئەوەی بلۆک نەبین
        if index < total_accounts:
            if index % BATCH_SIZE == 0:
                print(f"\n💤 قۆناغی {BATCH_SIZE} ئەکاونتی تەواو بوو. چاوەڕوانی بۆ ماوەی {DELAY_BETWEEN_BATCHES} چرکە...")
                time.sleep(DELAY_BETWEEN_BATCHES)
            else:
                print(f"   ⏱ چاوەڕوانی بۆ {DELAY_BETWEEN_ACCOUNTS} چرکە...")
                time.sleep(DELAY_BETWEEN_ACCOUNTS)

    # ٥. کۆتایی و ڕاپۆرت
    print("\n" + "="*40)
    print("پڕۆسەکە کۆتایی هات!")
    if found_in:
        print(f"🎉 یوزەری ئامانج (@{target_user}) لەم ئەکاونتانەدا دۆزرایەوە:")
        for acc in found_in:
            print(f" - @{acc}")
    else:
        print(f"یوزەری ئامانج (@{target_user}) لە هیچ کام لە ئەکاونتەکاندا نەدۆزرایەوە.")
    print("="*40)

if __name__ == "__main__":
    main()
