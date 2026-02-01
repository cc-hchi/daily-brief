import json
import datetime
import random
import os

# --- 配置 ---
TEMPLATE_PATH = "daily_brief/template.html"
OUTPUT_PATH = "daily_brief/index.html"
DATA_PATH = "daily_brief/data.json"

def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return MOCK_DATA  # Fallback to mock if no real data

def build():
    # 1. 准备数据
    data = load_data()
    
    # Time strings
    now = datetime.datetime.now()
    date_str_short = now.strftime("%b %d") 
    date_short = now.strftime("%Y.%m.%d")
    session_id = data.get("session_id", "SESS-GEN")

    # 2. 渲染组件
    # Secondary News
    secondary_items = data.get("secondary_news", [])
    secondary_html = "\n".join([render_secondary_item(i) for i in secondary_items])
    
    # Stocks
    stock_items = data.get("stocks", [])
    stocks_html = "\n".join([render_stock_item(s) for s in stock_items])

    # 3. 替换模板变量
    html = load_template()
    html = html.replace("{{DATE_STR_SHORT}}", date_str_short)
    html = html.replace("{{DATE_SHORT}}", date_short)
    html = html.replace("{{SESSION_ID}}", session_id)
    
    # Weather
    weather = data.get("weather", {})
    html = html.replace("{{WEATHER_TEMP_VAL}}", weather.get("temp", "--"))
    html = html.replace("{{WEATHER_COND}}", weather.get("cond", "--"))
    html = html.replace("{{WEATHER_ADVICE}}", weather.get("advice", ""))
    
    # Hero News
    hero = data.get("hero_news", {})
    html = html.replace("{{HERO_TITLE}}", hero.get("title", "No Headline"))
    html = html.replace("{{HERO_SOURCE}}", hero.get("source", "System"))
    html = html.replace("{{HERO_SUMMARY}}", hero.get("summary", ""))
    html = html.replace("{{HERO_URL}}", hero.get("url", "#"))
    
    # Inject Lists
    html = html.replace("{{SECONDARY_NEWS_LIST}}", secondary_html)
    
    # Inject Stocks (Simple replace for now, aiming for v2.1 dynamic injection later)
    # Note: In a real implementation we would use a proper template engine like Jinja2.
    # For now, we assume the layout is fixed.

    
    # Hack: Replace the hardcoded stock placeholder
    # 实际项目中我会用更优雅的 Jinja2 模板引擎
    stock_section_start = '<!-- Placeholder Stocks - Will be dynamic -->'
    stock_section_end = '<div class="text-[10px] text-gray-500 mt-2">REAL-TIME / PRE-MARKET</div>'
    
    # 简单的字符串替换来插入动态股票数据
    # 为了稳健，我们暂时只替换天气和新闻。股票数据展示在 V2.1 完善。
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Successfully built V2 Dashboard at {OUTPUT_PATH}")

if __name__ == "__main__":
    build()
