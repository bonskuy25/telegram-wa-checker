# bot_cekwa.py
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://127.0.0.1:5000/cekbio")  # default ke mock lokal

def format_single_result(number: str, data: dict) -> str:
    status = data.get("status", "not_registered")
    if status == "with_bio":
        bio = data.get("bio", "(tidak ada)")
        text = (
            f"🔍 *Hasil Cek Nomor WhatsApp*\n"
            f"───────────────────────\n"
            f"📞 Nomor: `{number}`\n"
            f"📱 Status: Terdaftar ✅\n"
            f"💬 Bio: {bio}\n\n"
            f"✅ *Cek selesai boskuu!*\n"
            f"📊 Total dicek: 1\n"
            f"📱 Terdaftar dengan bio: 1\n"
            f"📱 Terdaftar tanpa bio: 0\n"
            f"🚫 Tidak terdaftar: 0"
        )
    elif status == "no_bio":
        text = (
            f"🔍 *Hasil Cek Nomor WhatsApp*\n"
            f"───────────────────────\n"
            f"📞 Nomor: `{number}`\n"
            f"📱 Status: Terdaftar ✅\n"
            f"💬 Bio: (Tidak ada bio)\n\n"
            f"✅ *Cek selesai boskuu!*\n"
            f"📊 Total dicek: 1\n"
            f"📱 Terdaftar dengan bio: 0\n"
            f"📱 Terdaftar tanpa bio: 1\n"
            f"🚫 Tidak terdaftar: 0"
        )
    else:
        text = (
            f"🔍 *Hasil Cek Nomor WhatsApp*\n"
            f"───────────────────────\n"
            f"📞 Nomor: `{number}`\n"
            f"📱 Status: Tidak terdaftar ❌\n\n"
            f"✅ *Cek selesai boskuu!*\n"
            f"📊 Total dicek: 1\n"
            f"📱 Terdaftar dengan bio: 0\n"
            f"📱 Terdaftar tanpa bio: 0\n"
            f"🚫 Tidak terdaftar: 1"
        )
    return text

def format_bulk_result(results: list, summary: dict) -> str:
    total = summary.get("total", 0)
    with_bio = summary.get("with_bio", 0)
    no_bio = summary.get("no_bio", 0)
    not_reg = summary.get("not_registered", 0)

    header = (
        f"✅ *Cek selesai boskuu!*\n"
        f"📊 Total dicek: {total}\n"
        f"📱 Terdaftar dengan bio: {with_bio}\n"
        f"📱 Terdaftar tanpa bio: {no_bio}\n"
        f"🚫 Tidak terdaftar: {not_reg}\n\n"
    )

    lines = []
    for r in results:
        num = r.get("number", "")
        st = r.get("status", "not_registered")
        if st == "with_bio":
            bio = r.get("bio", "")
            lines.append(f"• `{num}` — ✅ Terdaftar (bio: {bio})")
        elif st == "no_bio":
            lines.append(f"• `{num}` — ✅ Terdaftar (tanpa bio)")
        else:
            lines.append(f"• `{num}` — ❌ Tidak terdaftar")
    body = "\n".join(lines)
    return "🔍 *Hasil Bulk Cek WhatsApp*\n───────────────────────\n" + header + body

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hai boskuu!\n\n"
        "Gunakan:\n"
        "`/cek <nomor>` — cek 1 nomor\n"
        "`/cekbulk <nomor1> <nomor2> ...` — cek banyak nomor sekaligus\n\n"
        "Contoh: `/cek 6281234567890`",
        parse_mode="Markdown"
    )

async def cek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Gunakan format: `/cek <nomor>`", parse_mode="Markdown")
        return
    nomor = context.args[0]
    try:
        resp = requests.post(API_URL, json={"number": nomor}, timeout=15)
        data = resp.json()
        text = format_single_result(nomor, data)
    except Exception as e:
        text = f"❌ Error saat koneksi ke API: {e}"
    await update.message.reply_text(text, parse_mode="Markdown")

async def cekbulk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Gunakan format: `/cekbulk <nomor1> <nomor2> ...`", parse_mode="Markdown")
        return
    numbers = context.args
    try:
        resp = requests.post(API_URL.replace("/cekbio", "/cekbulk"), json={"numbers": numbers}, timeout=20)
        data = resp.json()
        text = format_bulk_result(data.get("results", []), data.get("summary", {}))
    except Exception as e:
        text = f"❌ Error saat koneksi ke API: {e}"
    await update.message.reply_text(text, parse_mode="Markdown")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN environment variable belum diset.")
        exit(1)

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cek", cek))
    app.add_handler(CommandHandler("cekbulk", cekbulk))

    print("🚀 Bot Cek WA berjalan...")
    app.run_polling()
