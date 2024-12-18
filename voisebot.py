import os
import subprocess
import whisper
import torch
from datetime import datetime  # مكتبة الوقت
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# توكن البوت
TELEGRAM_BOT_TOKEN = "7974990515:AAHf3kEGrK5HUJ_7VxbE1-MFGefiye984BI"

# اختيار الجهاز المناسب (CPU أو GPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# تحميل نموذج Whisper
print("🔄 جاري تحميل النموذج...")
model = whisper.load_model("small").to(device)  # استخدم "base" أو "small" للأداء السريع
print("✅ تم تحميل النموذج بنجاح.")

# دالة لمعرفة التوقيت
def get_greeting():
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return "صباح الخير! ☀️"
    elif 12 <= current_hour < 18:
        return "مساء الخير! 🌤️"
    else:
        return "مساء الخير! 🌙"

# رسالة الترحيب عند إرسال /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    greeting = get_greeting()
    await update.message.reply_text(
        f"{greeting}\nتفضل، كيف أقدر أساعدك؟ 😎"
    )

# التعامل مع الملفات الصوتية
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("⏳ جارٍ معالجة الصوت... قد يستغرق بعض الوقت.")
        
        # تحميل الملف الصوتي
        voice_file = await update.message.voice.get_file()
        file_path_ogg = "audio.ogg"
        file_path_wav = "audio.wav"
        await voice_file.download_to_drive(file_path_ogg)

        # تحويل الصوت إلى WAV
        subprocess.run(["ffmpeg", "-i", file_path_ogg, "-ar", "16000", "-ac", "1", file_path_wav], check=True)

        # استخراج النص باستخدام Whisper
        result = model.transcribe(file_path_wav, language="ar", fp16=False)
        text = result["text"]

        # إرسال النص
        if text.strip():
            await update.message.reply_text(f"📝 النص المستخرج:\n{text}")
        else:
            await update.message.reply_text("⚠️ لم أتمكن من استخراج نص من الصوت. تأكد من وضوح التسجيل.")

    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")

    finally:
        # حذف الملفات المؤقتة
        for temp_file in [file_path_ogg, file_path_wav]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

# تشغيل البوت
def main():
    print("🚀 البوت قيد التشغيل...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.run_polling()

if __name__ == "__main__":
    main()
