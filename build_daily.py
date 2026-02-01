import json
import datetime
import os
import shutil

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
    # 使用 block 让整个区域可点
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

def update_archive_index():
    # 生成 archive/index.html 索引页
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
        
    files = sorted([f for f in os.listdir(ARCHIVE_DIR) if f.endswith(".html") and f != "index.html"], reverse=True)
    
    list_html = ""
    for f in files:
        name = f.replace(".html", "")
        list_html += f'<li><a href="{f}" class="text-blue-400 hover:underline">{name}</a></li>'
        
    html = f"""
    <!DOCTYPE html>
    <html class="dark" style="background:#000; color:#fff; font-family:sans-serif; padding:20px;">
    <head><title>Archive</title></head>
    <body>
        <h1>Briefing Archive</h1>
        <ul style="line-height:2;">{list_html}</ul>
        <div style="margin-top:20px;"><a href="../index.html" style="color:#666;">&larr; Back to Today</a></div>
    </body>
    </html>
    """
    with open(os.path.join(ARCHIVE_DIR, "index.html"), "w") as f:
        f.write(html)

def build():
    data = load_data()
    if not data:
        return # Do not build empty page
    
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
    
    html = html.replace("{{SECONDARY_NEWS_LIST}}", secondary_html)
    html = html.replace("{{STOCK_LIST}}", stocks_html)

    # 1. 写入主页
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
        
    # 2. 写入归档
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
    archive_path = os.path.join(ARCHIVE_DIR, f"{date_iso}.html")
    # 为了归档页面的相对路径正确（例如CSS引用），这里需要一点处理，或者简单地让 archive 页面的 link 都是绝对路径
    # 由于我们用了 tailwind CDN，这点没问题。唯一问题是 archive/index.html 回主页的链接。
    # 这里的简单做法是直接复制。
    shutil.copy(OUTPUT_PATH, archive_path)
    
    # 3. 更新归档索引
    update_archive_index()
    
    print(f"Successfully built Dashboard & Archive: {date_iso}")

if __name__ == "__main__":
    build()
