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
    <div class="group relative p-5 rounded-xl transition-all hover:bg-neutral-900" style="background-color: #111111; border: 1px solid #262626; border-color: #262626;">
        <div class="flex items-center justify-between mb-3">
            <span class="mono text-[9px] font-bold text-blue-400/80 uppercase tracking-wider px-1.5 py-0.5 rounded border border-blue-500/20 bg-blue-500/5">{item['source']}</span>
            <span class="mono text-[10px] text-neutral-600 group-hover:text-neutral-500 transition-colors">{item['time']}</span>
        </div>
        <a href="{item['url']}" target="_blank" class="block">
            <h3 class="text-sm font-medium text-neutral-300 group-hover:text-white leading-relaxed transition-colors">
                {item['title']}
            </h3>
        </a>
        <div class="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity -translate-x-2 group-hover:translate-x-0 duration-300">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-neutral-500"><path d="M5 12h14"></path><path d="M12 5l7 7-7 7"></path></svg>
        </div>
    </div>
    """

def render_stock_item(stock):
    trend = stock.get('trend', 'neutral')
    
    if trend == 'up':
        color = "#10b981" # emerald-500
        bg_color = "rgba(16, 185, 129, 0.1)"
        arrow = "↑"
    elif trend == 'down':
        color = "#f43f5e" # rose-500
        bg_color = "rgba(244, 63, 94, 0.1)"
        arrow = "↓"
    else:
        color = "#737373" # neutral-500
        bg_color = "rgba(115, 115, 115, 0.1)"
        arrow = "-"
    
import random

def generate_sparkline(width=60, height=20, color="#10b981", trend="up"):
    # Generate 7 points
    points = []
    step = width / 6
    
    # Start point
    start_y = random.randint(5, 15)
    points.append((0, start_y))
    
    current_y = start_y
    for i in range(1, 6):
        # Random walk
        delta = random.randint(-5, 5)
        current_y = max(2, min(height-2, current_y + delta))
        points.append((i * step, current_y))
    
    # End point guided by trend
    if trend == 'up':
        end_y = random.randint(2, 8) # Higher (smaller y)
    elif trend == 'down':
        end_y = random.randint(12, 18) # Lower (larger y)
    else:
        end_y = random.randint(5, 15)
        
    points.append((width, end_y))
    
    # Build path d string
    d = f"M {points[0][0]} {points[0][1]}"
    for p in points[1:]:
        d += f" L {p[0]} {p[1]}"
        
    return f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="{d}" /></svg>'

def render_stock_item(stock):
    trend = stock.get('trend', 'neutral')
    
    if trend == 'up':
        color = "#10b981" # emerald-500
        bg_color = "rgba(16, 185, 129, 0.1)"
        arrow = "↑"
    elif trend == 'down':
        color = "#f43f5e" # rose-500
        bg_color = "rgba(244, 63, 94, 0.1)"
        arrow = "↓"
    else:
        color = "#737373" # neutral-500
        bg_color = "rgba(115, 115, 115, 0.1)"
        arrow = "-"
    
    sparkline = generate_sparkline(width=60, height=20, color=color, trend=trend)

    return f"""
    <div class="flex items-center justify-between py-2 border-b border-neutral-800/50 last:border-0 group">
        <div class="flex flex-col">
            <span class="text-xs font-bold text-gray-200">{stock['symbol']}</span>
            <span class="mono text-[10px] text-neutral-500">{stock['price']}</span>
        </div>
        <div class="flex items-center gap-4">
            <div class="hidden sm:block opacity-50 group-hover:opacity-100 transition-opacity">
                {sparkline}
            </div>
            <div class="mono text-[10px] px-1.5 py-0.5 rounded flex items-center gap-1 min-w-[60px] justify-end" style="color: {color}; background-color: {bg_color};">
                <span>{arrow}</span>
                <span>{stock['change']}</span>
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

def render_hn_item(item):
    return f"""
    <div class="flex items-start gap-3 py-2 border-b border-neutral-800/50 last:border-0 group">
        <div class="mt-1 min-w-[24px] text-center">
            <span class="block text-[10px] font-bold text-orange-500 bg-orange-500/10 rounded px-1">{item['points']}</span>
        </div>
        <a href="{item['url']}" target="_blank" class="text-sm text-neutral-300 hover:text-white leading-snug transition-colors">
            {item['title']}
        </a>
    </div>
    """

def render_github_item(item):
    return f"""
    <div class="flex items-center justify-between py-2 border-b border-neutral-800/50 last:border-0">
        <div>
            <div class="text-sm font-medium text-neutral-200">{item['repo']}</div>
            <div class="text-[10px] text-neutral-500">{item['lang']}</div>
        </div>
        <div class="flex items-center gap-1 text-[10px] text-neutral-400">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg>
            {item['stars']}
        </div>
    </div>
    """

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
    
    # New Sections
    hn_items = data.get("hacker_news", [])
    hn_html = "\n".join([render_hn_item(i) for i in hn_items])
    
    gh_items = data.get("github_trending", [])
    gh_html = "\n".join([render_github_item(i) for i in gh_items])

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
    
    html = html.replace("{{SECONDARY_NEWS_BLOCKS}}", secondary_html)
    html = html.replace("{{STOCK_LIST}}", stocks_html)
    
    # Inject new sections (placeholder injection points need to be added to template first, 
    # but we will just append them for now or assume specific tags if we edited template.
    # Actually, let's replace a specific marker or area.
    # Since we haven't updated template.html to have {{HN_LIST}} yet, we need to do that next.
    # But this script writes the strings.
    html = html.replace("{{HN_LIST}}", hn_html)
    html = html.replace("{{GH_LIST}}", gh_html)

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
