import io
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
import jdatetime
import os

TOKEN = os.getenv("TOKEN")

# بارگذاری تمپلیت
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("invoice.html")

invoice_counter = 750  # شماره شروع فاکتور

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global invoice_counter

    text = update.message.text.strip()
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    if len(lines) < 4:
        await update.message.reply_text("❌ نام، شماره تماس، کدپستی و آدرس لازم است")
        return

    name = lines[0]
    phone = lines[1]
    plate = lines[2]
    address = "<br>".join(lines[3:])

    if not phone.isdigit():
        await update.message.reply_text("❌ شماره تماس معتبر نیست")
        return

    if not plate.isdigit():
        await update.message.reply_text("❌ کدپستی معتبر نیست")
        return

    invoice_counter += 1

    data = {
        "invoiceNumber": invoice_counter,
        "date": jdatetime.datetime.now().strftime("%Y/%m/%d"),
        "senderName": "مستر بالش",
        "senderPhone": "0902xxxxxxx",
        "customerName": name,
        "customerPhone": phone,
        "customerPlate": plate,
        "customerAddress": address
    }

    html = template.render(**data)

    # ایجاد PDF در حافظه بدون ذخیره روی دیسک
    pdf_buffer = io.BytesIO()
    css = CSS(string='''
        @page { size: 70mm 90mm; margin: 5px; } body { margin: 0; padding: 0; }
    ''')
    HTML(string=html).write_pdf(pdf_buffer, stylesheets=[css])
    pdf_buffer.seek(0)  # برگشت به ابتدای بافر

    # ارسال مستقیم PDF به تلگرام
    await update.message.reply_document(document=pdf_buffer, filename=f"فاکتور-{invoice_counter}-({name}).pdf")

# راه‌اندازی بات
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot running ...")
app.run_polling()
