import os
import time
import tempfile
import telebot
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from pypdf import PdfReader

# Bot token
TOKEN = "8085614647:AAFg6oXkg0CdLeW2xoHMJ3lan53PGZjvIWE"
bot = telebot.TeleBot(TOKEN)

# Copyrights and contact info
BOT_RIGHTS = "🤍 تلجرام :- @altaee_z\n🌐موقعي : www.ali-Altaee.free.nf"

# Function to convert docx to PDF (text only)
def convert_docx_to_pdf_simple(input_path, output_path):
    doc = Document(input_path)
    pdf = SimpleDocTemplate(output_path)
    styles = getSampleStyleSheet()
    flow = []
    for para in doc.paragraphs:
        flow.append(Paragraph(para.text, styles["Normal"]))
        flow.append(Spacer(1, 12))
    pdf.build(flow)
    return os.path.exists(output_path)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "👋 أرسل ملف .docx وسأحوّله إلى PDF، مع عرض معلومات عنه.")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    doc = message.document
    filename = doc.file_name or "document.docx"
    chat_id = message.chat.id

    if not filename.lower().endswith(".docx"):
        bot.reply_to(message, "❗ أرسل ملف بصيغة .docx فقط.")
        return

    status = bot.reply_to(message, "⏳ جاري تحميل الملف...")
    start_time = time.time()

    try:
        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, filename)
            with open(input_path, 'wb') as f:
                f.write(downloaded)

            output_pdf = os.path.join(tmpdir, os.path.splitext(filename)[0] + ".pdf")

            bot.edit_message_text("🔄 جاري تحويل النصوص إلى PDF...", chat_id, status.message_id)

            convert_docx_to_pdf_simple(input_path, output_pdf)

            # Calculate elapsed time
            elapsed = time.time() - start_time

            # Get PDF details
            reader = PdfReader(output_pdf)
            num_pages = len(reader.pages)
            pdf_size_mb = os.path.getsize(output_pdf) / (1024*1024)

            bot.edit_message_text("📤 جاري إرسال ملف الـPDF...", chat_id, status.message_id)

            with open(output_pdf, 'rb') as pdf_file:
                bot.send_document(chat_id, pdf_file,
                    caption="✅ تم تحويل الملف بنجاح!")

            # Send details and copyrights
            info_msg = (
                f"📑 تفاصيل الملف\n"
                f"• الحجم: {pdf_size_mb:.2f} MB\n"
                f"• عدد الصفحات: {num_pages}\n"
                f"• الوقت المستغرق: {elapsed:.2f} ثانية\n\n"
                f"{BOT_RIGHTS}"
            )
            bot.send_message(chat_id, info_msg)

    except Exception as e:
        bot.edit_message_text(f"❗ حدث خطأ: {e}", chat_id, status.message_id)

if __name__ == "__main__":
    print("🚀 Bot running...")
    bot.infinity_polling()
