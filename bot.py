import io
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS


TOKEN = os.getenv("TOKEN")


# Template
# --------------------
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("invoice.html")


# Sender Info
# --------------------
SENDER_ADDRESS = "مستربالش ( دارابی )"
SENDER_PHONE = "09021042824"


# Utils
# --------------------
def parse_customers(text: str):
    parts = [p.strip() for p in text.split("✅") if p.strip()]
    customers = []

    for p in parts:
        lines = [l.strip() for l in p.split("\n") if l.strip()]
        if len(lines) < 2:
            continue

        customers.append({
            "address": "<br>".join(lines[:-1]),
            "phone": lines[-1]
        })

    return customers 


def chunk(lst, size):
    """گروه‌بندی ۸تایی برای هر صفحه"""
    return [lst[i:i + size] for i in range(0, len(lst), size)]


# Handler
# --------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    customers = parse_customers(update.message.text)

    if not customers:
        await update.message.reply_text("❌ فرمت پیام اشتباه است")
        return

    pages = chunk(customers, 8) 

    html = template.render(
        pages=pages,
        senderAddress=SENDER_ADDRESS,
        senderPhone=SENDER_PHONE
    )

    pdf_buffer = io.BytesIO()

    css = CSS(string="""
        @page {
            size: A4;
            margin: 0;
        }
    """)

    HTML(string=html).write_pdf(pdf_buffer, stylesheets=[css])
    pdf_buffer.seek(0)

    await update.message.reply_document(
        document=pdf_buffer,
        filename="فاکتورهای امروز.pdf"
    )


# App
# --------------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot running ...")
app.run_polling()
