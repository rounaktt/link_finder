import asyncio
import httpx
import telebot
import time
import subprocess
import socket
import re

# ✅ Your actual bot token
BOT_TOKEN = "7724913384:AAHH3TQJ7TJ2BuQiXaNPjJ8JxHY0srrVXnc"

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)  # Disable threading for stability

# ASCII Art for Hacker Look
HACKER_BANNER = """ 
🕵️‍♂️ Welcome to Rounak x link finder ????? 
━━━━━━━━━━━━━━━━━━━━━━
🔍 Deep Link Analysis 
📡 Network Recon Tools 
💀 Ethical Hacking Toolkit 
━━━━━━━━━━━━━━━━━━━━━━
"""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, f"```{HACKER_BANNER}```\n👽 Send any URL to analyze its redirects.", parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def show_help(message):
    bot.send_message(message.chat.id, """ 
💀 *Available Commands:*
/redirect <url> - Track all redirects (Auto-detected now!)
/scan <url> - Scan open ports (Basic)
/whois <domain> - Get domain details
/info <url> - Fetch website headers
/ping <host> - Ping a website
━━━━━━━━━━━━━━━━━━━━━━
👽 Send a direct URL for deep analysis!
""", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def detect_and_analyze(message):
    urls = re.findall(r'http[s]?://\S+', message.text)
    if urls:
        for url in urls:
            asyncio.run(get_redirects(message, url))
    else:
        bot.send_message(message.chat.id, "❌ No URL detected. Please send a valid URL.")

async def get_redirects(message, url):
    try:
        loading_msg = bot.send_message(message.chat.id, "🛠 Processing link...\n🔄 Following redirects...")

        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            response = await client.get(url)

            redirect_chain = "**🔗 Redirect Chain:**\n"
            if response.history:
                for r in response.history:
                    redirect_chain += f"➡ `{r.url}` ({r.status_code})\n"
                redirect_chain += f"\n✅ **Final URL:** `{response.url}`"
            else:
                redirect_chain = f"✅ **No Redirects. Final URL:** `{response.url}`"

        bot.edit_message_text(chat_id=message.chat.id, message_id=loading_msg.message_id, text=redirect_chain, parse_mode="Markdown")

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ **Error:** `{e}`", parse_mode="Markdown")

@bot.message_handler(commands=['scan'])
def scan_ports(message):
    domain = message.text.replace("/scan", "").strip()
    if domain:
        bot.send_message(message.chat.id, f"🛠 Scanning `{domain}` for open ports...", parse_mode="Markdown")
        result = run_nmap_scan(domain)
        bot.send_message(message.chat.id, f"🕵️ **Port Scan Result:**\n```{result}```", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ Usage: `/scan <url>`", parse_mode="Markdown")

def run_nmap_scan(domain):
    try:
        result = subprocess.run(["nmap", "-F", domain], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

@bot.message_handler(commands=['whois'])
def whois_lookup(message):
    domain = message.text.replace("/whois", "").strip()
    if domain:
        bot.send_message(message.chat.id, f"🕵️ Fetching WHOIS data for `{domain}`...", parse_mode="Markdown")
        result = run_whois(domain)
        bot.send_message(message.chat.id, f"🌍 **WHOIS Info:**\n```{result}```", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ Usage: `/whois <domain>`", parse_mode="Markdown")

def run_whois(domain):
    try:
        result = subprocess.run(["whois", domain], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

@bot.message_handler(commands=['info'])
def fetch_headers(message):
    url = message.text.replace("/info", "").strip()
    if url:
        asyncio.run(get_headers(message, url))
    else:
        bot.send_message(message.chat.id, "❌ Usage: `/info <url>`", parse_mode="Markdown")

async def get_headers(message, url):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            headers = "\n".join([f"🔹 {k}: `{v}`" for k, v in response.headers.items()])
        bot.send_message(message.chat.id, f"📡 **Website Headers:**\n{headers}", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ **Error:** `{e}`", parse_mode="Markdown")

@bot.message_handler(commands=['ping'])
def ping_host(message):
    host = message.text.replace("/ping", "").strip()
    if host:
        bot.send_message(message.chat.id, f"📡 Pinging `{host}`...", parse_mode="Markdown")
        result = run_ping(host)
        bot.send_message(message.chat.id, f"🛰 **Ping Result:**\n```{result}```", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ Usage: `/ping <host>`", parse_mode="Markdown")

def run_ping(host):
    try:
        result = subprocess.run(["ping", "-c", "4", host], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

bot.polling()
