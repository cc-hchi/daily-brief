import json
import datetime
import os
import shutil
import re

# --- 配置 ---
BASE_DIR = "daily_brief"
TEMPLATE_PATH = os.path.join(BASE_DIR, "template.html")
OUTPUT_PATH = os.path.join(BASE_DIR, "index.html")
DATA_PATH = os.path.join(BASE_DIR, "data.json")
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")

def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    print("WARNING: No data.json found!")
    return {}

def load_template():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()

def render_secondary_item(item):
    return f"""
    <a href="{item['url']}" target="_blank" class="group relative flex flex-col gap-1.5 p-4 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/5 transition-all duration-300">
        <div class="flex items-center justify-between">
            <span class="text-[9px] font-bold tracking-widest text-blue-400 uppercase bg-blue-500/10 px-1.5 py-0.5 rounded">{item['source']}</span>
            <span class="text-[10px] text-gray-600 font-mono group-hover:text-gray-500 transition-colors">{item['time']}</span>
        </div>
        <h4 class="text-sm font-medium text-gray-200 group-hover:text-white leading-snug transition-colors pr-4">
            {item['title']}
        </h4>
        <div class="absolute right-4 top-4 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-white"><path d="M7 17L17 7"></path><path d="M7 7h10v10"></path></svg>
        </div>
    </a>
    """

def render_stock_item(stock):
    trend = stock.get('trend', 'neutral')
    
    # Trend styles
    if trend == 'up':
        bg_class = "bg-emerald-500/10"
        text_class = "text-emerald-400"
        icon = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>'
    elif trend == 'down':
        bg_class = "bg-rose-500/10"
        text_class = "text-rose-400"
        icon = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg>'
    else:
        bg_class = "bg-gray-500/10"
        text_class = "text-gray-400"
        icon = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line></svg>'
    
    return f"""
    <div class="group flex items-center justify-between p-3 rounded-lg hover:bg-white/5 transition-colors border border-transparent hover:border-white/5">
        <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center text-[10px] font-bold text-gray-400 group-hover:text-white transition-colors">
                {stock['symbol'][0]}
            </div>
            <div class="flex flex-col">
                <span class="text-sm font-bold text-gray-200 group-hover:text-white">{stock['symbol']}</span>
                <span class="text-[10px] text-gray-500 font-mono">MARKET</span>
            </div>
        </div>
        
        <div class="flex flex-col items-end">
            <span class="text-sm font-medium text-white font-mono tracking-tight">{stock['price']}</span>
            <div class="flex items-center gap-1 mt-0.5">
                <span class="{text_class}">{icon}</span>
                <span class="text-[10px] font-mono {text_class} {bg_class} px-1.5 py-0.5 rounded-sm">{stock['change']}</span>
            </div>
        </div>
    </div>
    """

def extract_metadata(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        date_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content)
        date_str = date_match.group(1) if date_match else "Unknown Date"
        hero_match = re.search(r'<h2[^>]*>\s*([^<]+)\s*</h2>', content) # Adjusted regex for simpler template
        if not hero_match: # Try with anchor
            hero_match = re.search(r'<h2[^>]*>\s*<a[^>]*>([^<]+)</a>\s*</h2>', content)
        hero_title = hero_match.group(1).strip() if hero_match else "Daily Briefing"
        temp_match = re.search(r'<div class="text-4xl font-light text-white mb-1">([^<]+)</div>', content)
        temp = temp_match.group(1) if temp_match else ""
        return {"date": date_str, "hero": hero_title, "temp": temp}
    except Exception as e:
        return {"date": "Unknown", "hero": "Error", "temp": ""}

def update_archive_index():
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
    files = sorted([f for f in os.listdir(ARCHIVE_DIR) if f.endswith(".html") and f != "index.html"], reverse=True)
    
    cards_html = ""
    for f in files:
        file_path = os.path.join(ARCHIVE_DIR, f)
        meta = extract_metadata(file_path)
        cards_html += f"""
        <a href="{f}" class="group relative block p-6 bg-white/5 border border-white/10 rounded-xl overflow-hidden hover:border-blue-500/50 hover:bg-white/10 transition-all duration-300">
            <div class="absolute inset-0 bg-gradient-to-r from-blue-500/0 via-blue-500/0 to-blue-500/0 group-hover:from-blue-500/5 group-hover:to-purple-500/5 transition-all"></div>
            <div class="flex justify-between items-start mb-4">
                <div class="flex flex-col">
                    <span class="text-xs font-mono text-blue-400 uppercase tracking-wider">BRIEFING</span>
                    <span class="text-xl font-bold text-white mt-1">{meta['date']}</span>
                </div>
                <div class="text-2xl opacity-50">{meta['temp']}</div>
            </div>
            <h3 class="text-gray-300 font-medium leading-relaxed group-hover:text-white transition-colors line-clamp-2">{meta['hero']}</h3>
        </a>
        """

    html = f"""<!DOCTYPE html><html lang="zh-CN" class="dark"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Archive</title><script src="https://cdn.tailwindcss.com"></script><style>body{{background-color:#050505;color:#fff;min-height:100vh}}</style></head><body class="p-6 md:p-12"><div class="max-w-5xl mx-auto"><header class="mb-12 flex justify-between"><div><h1 class="text-3xl font-bold">Timeline</h1></div><a href="../index.html" class="text-sm text-gray-500 hover:text-white">&larr; Back</a></header><div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">{cards_html}</div></div></body></html>"""
    
    with open(os.path.join(ARCHIVE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def build():
    data = load_data()
    if not data: return 
    
    now = datetime.datetime.now()
    date_str_short = now.strftime("%b %d") 
    date_short = now.strftime("%Y.%m.%d")
    date_iso = now.strftime("%Y-%m-%d")
    session_id = data.get("session_id", "SESS-GEN")

    secondary_items = data.get("secondary_news", [])
    secondary_html = "\n".join([render_secondary_item(i) for i in secondary_items])
    stock_items = data.get("stocks", [])
    stocks_html = "\n".join([render_stock_item(s) for s in stock_items])

    html = load_template()
    html = html.replace("{{DATE_STR_SHORT}}", date_str_short)
    html = html.replace("{{DATE_SHORT}}", date_short)
    html = html.replace("{{SESSION_ID}}", session_id)
    
    weather = data.get("weather", {})
    html = html.replace("{{WEATHER_TEMP_VAL}}", weather.get("temp", "--"))
    html = html.replace("{{WEATHER_COND}}", weather.get("cond", "--"))
    html = html.replace("{{WEATHER_ADVICE}}", weather.get("advice", ""))
    
    hero = data.get("hero_news", {})
    html = html.replace("{{HERO_TITLE}}", hero.get("title", "Waiting..."))
    html = html.replace("{{HERO_SOURCE}}", hero.get("source", ""))
    html = html.replace("{{HERO_SUMMARY}}", hero.get("summary", ""))
    html = html.replace("{{HERO_URL}}", hero.get("url", "#"))
    
    # CSS Aurora Gradient handles the hero visual now.
    
    html = html.replace("{{SECONDARY_NEWS_LIST}}", secondary_html)
    html = html.replace("{{STOCK_LIST}}", stocks_html)

    # 1. 生成主页 (index.html)
    # 主页在根目录，去 Archive 需要进一层
    index_html = html.replace("{{ARCHIVE_LINK}}", "archive/index.html")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(index_html)
        
    # 2. 生成归档页 (archive/YYYY-MM-DD.html)
    # 归档页在 archive/ 目录下，History 就在同级 (或者上一级再回来，其实就是同级的 index.html)
    # 所以链接应该是 "index.html" (指向 archive/index.html)
    archive_html = html.replace("{{ARCHIVE_LINK}}", "index.html")
    
    if not os.path.exists(ARCHIVE_DIR): os.makedirs(ARCHIVE_DIR)
    # 直接写入，不再 copy
    with open(os.path.join(ARCHIVE_DIR, f"{date_iso}.html"), "w", encoding="utf-8") as f:
        f.write(archive_html)

    update_archive_index()
    print(f"Successfully built Dashboard & Archive: {date_iso}")

if __name__ == "__main__":
    build()
