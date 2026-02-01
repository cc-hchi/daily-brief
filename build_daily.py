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
    # 使用标准的 <a> 标签，确保可点击
    return f"""
    <a href="{item['url']}" target="_blank" class="block group flex items-start gap-3 p-3 rounded-lg hover:bg-white/5 transition-colors no-underline">
        <div class="mt-1.5 min-w-[4px] h-[4px] rounded-full bg-blue-500 group-hover:bg-blue-400"></div>
        <div class="flex-1">
            <h4 class="text-sm font-medium text-gray-200 group-hover:text-blue-300 transition-colors leading-snug">
                {item['title']}
            </h4>
            <div class="flex items-center gap-2 mt-1.5">
                <span class="text-[10px] text-gray-500 font-mono uppercase">{item['source']}</span>
                <span class="text-[10px] text-gray-600">·</span>
                <span class="text-[10px] text-gray-500">{item['time']}</span>
            </div>
        </div>
    </a>
    """

def render_stock_item(stock):
    trend = stock.get('trend', 'neutral')
    color_class = "text-green-400 bg-green-400/10" if trend == 'up' else ("text-red-400 bg-red-400/10" if trend == 'down' else "text-gray-400 bg-gray-400/10")
    
    return f"""
    <div class="flex justify-between items-center py-1 border-b border-white/5 last:border-0">
        <span class="font-bold text-sm text-gray-300">{stock['symbol']}</span>
        <div class="flex items-center gap-2">
            <span class="text-xs text-gray-500">{stock['price']}</span>
            <span class="font-mono text-[10px] {color_class} px-1.5 py-0.5 rounded">{stock['change']}</span>
        </div>
    </div>
    """

def extract_metadata(file_path):
    """
    从归档的 HTML 文件中提取元数据（日期、头条标题），
    以便在列表页展示更丰富的信息。
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # 提取日期 (假设格式 Feb 02)
        date_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content)
        date_str = date_match.group(1) if date_match else "Unknown Date"
        
        # 提取头条 (Hero Title)
        # 匹配 <h2 ...><a ...>Title</a></h2>
        hero_match = re.search(r'<h2[^>]*>\s*<a[^>]*>([^<]+)</a>\s*</h2>', content)
        hero_title = hero_match.group(1) if hero_match else "Daily Briefing"
        
        # 提取天气 (可选)
        temp_match = re.search(r'<div class="text-3xl font-bold text-white">([^<]+)</div>', content)
        temp = temp_match.group(1) if temp_match else ""

        return {
            "date": date_str,
            "hero": hero_title,
            "temp": temp
        }
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return {"date": "Unknown", "hero": "Error reading file", "temp": ""}

def update_archive_index():
    # 生成 archive/index.html 索引页 - Top Tier Design
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
        
    files = sorted([f for f in os.listdir(ARCHIVE_DIR) if f.endswith(".html") and f != "index.html"], reverse=True)
    
    cards_html = ""
    for f in files:
        file_path = os.path.join(ARCHIVE_DIR, f)
        meta = extract_metadata(file_path)
        
        full_date = f.replace(".html", "")
        
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
            
            <h3 class="text-gray-300 font-medium leading-relaxed group-hover:text-white transition-colors line-clamp-2">
                {meta['hero']}
            </h3>
            
            <div class="mt-6 flex items-center text-xs text-gray-500 font-mono group-hover:text-blue-400 transition-colors">
                <span>ACCESS ARCHIVE</span>
                <svg class="w-3 h-3 ml-2 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
            </div>
        </a>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN" class="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Archive · Intelligence</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
        <script>
            tailwind.config = {{
                darkMode: 'class',
                theme: {{
                    extend: {{
                        fontFamily: {{
                            sans: ['Inter', 'sans-serif'],
                            mono: ['JetBrains Mono', 'monospace'],
                        }}
                    }}
                }}
            }}
        </script>
        <style>
            body {{
                background-color: #050505;
                background-image: radial-gradient(circle at 50% 0%, #111 0%, #000 70%);
                min-height: 100vh;
            }}
        </style>
    </head>
    <body class="text-gray-200 antialiased p-6 md:p-12">
        <div class="max-w-5xl mx-auto">
            <header class="mb-12 flex items-center justify-between">
                <div>
                    <h1 class="text-3xl md:text-4xl font-extrabold text-white tracking-tight">Timeline</h1>
                    <p class="text-gray-500 mt-2 text-sm">Intelligence Archive</p>
                </div>
                <a href="../index.html" class="px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-sm font-medium hover:bg-white/10 hover:text-white transition-colors">
                    &larr; Back to Today
                </a>
            </header>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {cards_html}
            </div>
            
            <footer class="mt-20 text-center text-xs text-gray-600 font-mono">
                SECURE ARCHIVE · ENCRYPTED CONNECTION
            </footer>
        </div>
    </body>
    </html>
    """
    
    with open(os.path.join(ARCHIVE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def build():
    data = load_data()
    if not data:
        return 
    
    now = datetime.datetime.now()
    date_str_short = now.strftime("%b %d") 
    date_short = now.strftime("%Y.%m.%d")
    date_iso = now.strftime("%Y-%m-%d")
    session_id = data.get("session_id", "SESS-GEN")

    # 渲染列表
    secondary_items = data.get("secondary_news", [])
    secondary_html = "\n".join([render_secondary_item(i) for i in secondary_items])
    
    stock_items = data.get("stocks", [])
    stocks_html = "\n".join([render_stock_item(s) for s in stock_items])

    # 替换模板
    html = load_template()
    html = html.replace("{{DATE_STR_SHORT}}", date_str_short)
    html = html.replace("{{DATE_SHORT}}", date_short)
    html = html.replace("{{SESSION_ID}}", session_id)
    
    weather = data.get("weather", {})
    html = html.replace("{{WEATHER_TEMP_VAL}}", weather.get("temp", "--"))
    html = html.replace("{{WEATHER_COND}}", weather.get("cond", "--"))
    html = html.replace("{{WEATHER_ADVICE}}", weather.get("advice", ""))
    
    hero = data.get("hero_news", {})
    html = html.replace("{{HERO_TITLE}}", hero.get("title", "Waiting for data..."))
    html = html.replace("{{HERO_SOURCE}}", hero.get("source", ""))
    html = html.replace("{{HERO_SUMMARY}}", hero.get("summary", ""))
    html = html.replace("{{HERO_URL}}", hero.get("url", "#"))
    
    # 图片逻辑
    # 使用确定的静态 URL 以保证加载
    keyword = hero.get("image_keyword", "technology")
    
    if "dna" in keyword.lower() or "bio" in keyword.lower():
        # DNA 螺旋 (Picsum / 这里的 ID 是示例，为了稳我们用随机种子)
        # image_url = "https://picsum.photos/seed/dna/800/600"
        # 或者用一个确定能访问的图 (比如 Wikimedia Commons 的高质量图，或者 GitHub 上的资源)
        # 既然 Unsplash 挂了，我们用一个完全不同的策略：
        # 使用 Polination AI (通常没被墙)
        image_url = "https://image.pollinations.ai/prompt/DNA%20helix%20dark%20cinematic%20tech?width=1024&height=768&nologo=true"
    elif "chip" in keyword.lower() or "nvidia" in keyword.lower():
        image_url = "https://image.pollinations.ai/prompt/microchip%20processor%20glowing%20blue%20dark?width=1024&height=768&nologo=true"
    else:
        image_url = "https://image.pollinations.ai/prompt/abstract%20dark%20technology%20mesh?width=1024&height=768&nologo=true"

    html = html.replace("{{HERO_IMAGE_URL}}", image_url)
    
    html = html.replace("{{SECONDARY_NEWS_LIST}}", secondary_html)
    html = html.replace("{{STOCK_LIST}}", stocks_html)

    # 1. 写入主页
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
        
    # 2. 写入归档
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
    archive_path = os.path.join(ARCHIVE_DIR, f"{date_iso}.html")
    shutil.copy(OUTPUT_PATH, archive_path)
    
    # 3. 更新归档索引
    update_archive_index()
    
    print(f"Successfully built Dashboard & Archive: {date_iso}")

if __name__ == "__main__":
    build()
