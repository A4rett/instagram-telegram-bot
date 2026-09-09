import streamlit as st
import instaloader
import time

st.set_page_config(page_title="Instagram Scanner", page_icon="🔍")

st.title("🔍 پشکنیری فۆڵۆوەری اینستاگرام")
st.write("لەم سایتەدا دەتوانیت پشکنین بکەیت بە بێ تیلیگرام.")

# خانەکانی وەرگرتنی زانیاری لە سایتدا
mode = st.radio("شێوازی کارکردن هەڵبژێرە:", ["لیستی کۆمبۆ (Combo)", "گەڕان بەپێی شوێن (Location)"])

target = st.text_input("🎯 یوزەرنەیمی ئامانج (ئەو کەسەی دەگەڕێیت بەدوایدا):").strip().replace('@', '')

if mode == "لیستی کۆمبۆ (Combo)":
    combo_text = st.text_area("📄 لیستی کۆمبۆ بنووسە (هەر یوزەرێک لە دێڕێکدا):")
    combo = [line.strip().replace('@', '') for line in combo_text.split('\n') if line.strip()]
else:
    location_name = st.text_input("📍 ناوی شوێن یان هاشتاگ بنووسە (بۆ نموونە: halabja):").strip().replace('#', '').lower()
    combo = []

st.markdown("---")
st.subheader("🔑 زانیاری ئەکاونتی اینستاگرام (فەیک)")
ig_user = st.text_input("یوزەرنەیمی اینستاگرامی خۆت:").strip()
ig_pass = st.text_input("پاسۆردی اینستاگرام:", type="password").strip()

DELAY_BETWEEN_ACCOUNTS = 15
BATCH_SIZE = 10
DELAY_BETWEEN_BATCHES = 60

if st.button("🚀 دەستپێکردنی پشکنین"):
    if not ig_user or not ig_pass or not target:
        st.error("❌ تکایە هەموو خانە پێویستەکان پڕ بکەرەوە (یوزەری ئامانج، ئەکاونتی لۆگین).")
    else:
        with st.spinner("⏳ چوونەژوورەوە و پشکنین دەستی پێکرد..."):
            L = instaloader.Instaloader()
            try:
                L.login(ig_user, ig_pass)
                st.success("✅ سەرکەوتوو بوو لە لۆگینکردن!")
            except Exception as e:
                st.error(f"❌ هەڵە لە لۆگین: {e}")
                st.stop()

            # ئەگەر دۆخەکە Location بوو
            if mode == "گەڕان بەپێی شوێن (Location)" and location_name:
                st.write(f"🔍 گەڕان بەدوای ئەکاونتەکان بۆ شوێنی: {location_name} ...")
                try:
                    hashtag = instaloader.Hashtag.from_name(L.context, location_name)
                    for post in hashtag.get_posts():
                        owner = post.owner_profile
                        if not owner.is_private and owner.username not in combo:
                            combo.append(owner.username)
                        if len(combo) >= 15:
                            break
                except Exception as e:
                    st.error(f"⚠️ هەڵە لە دۆزینەوەی پەیجەکان: {e}")
                    st.stop()

            if not combo:
                st.warning("❌ هیچ یوزەرێک یان پەیجێک نەدۆزرایەوە بۆ پشکنین.")
                st.stop()

            st.write(f"📄 کۆی گشتی پەیجەکان بۆ پشکنین: {len(combo)}")
            total = len(combo)
            found_in = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()

            for index, acc in enumerate(combo, start=1):
                status_text.text(f"🔍 [{index}/{total}] پشکنینی: @{acc}")
                
                try:
                    profile = instaloader.Profile.from_username(L.context, acc)
                    is_found = False
                    for follower in profile.get_followers():
                        if follower.username.lower() == target.lower():
                            is_found = True
                            break
                            
                    if is_found:
                        st.success(f"✅ دۆزرایەوە! @{target} فۆڵۆوی @{acc} ـی کردووە.")
                        found_in.append(acc)
                except Exception as e:
                    st.warning(f"⚠️ نەتوانرا @{acc} بپشکنرێت: {e}")

                progress_bar.progress(index / total)

                if index < total:
                    if index % BATCH_SIZE == 0:
                        time.sleep(DELAY_BETWEEN_BATCHES)
                    else:
                        time.sleep(DELAY_BETWEEN_ACCOUNTS)
                        
            st.markdown("---")
            st.subheader("🎉 ئەنجامی کۆتایی پشکنین:")
            if found_in:
                st.write(f"یوزەری @{target} لەم ئەکاونتانەدا دۆزرایەوە:")
                for f in found_in:
                    st.write(f"✔️ @{f}")
            else:
                st.info(f"یوزەری @{target} لە هیچ کام لە پەیجەکاندا نەدۆزرایەوە.")
