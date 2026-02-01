import json
import datetime
import random
import os

# --- 配置 ---
TEMPLATE_PATH = "daily_brief/template.html"
OUTPUT_PATH = "daily_brief/index.html"
DATA_PATH = "daily_brief/data.json"

# --- MOCK 用于 Fallback ---
MOCK_DATA = {
    "weather": {"temp": "--", "cond": "--", "advice": "No data"},
    "stocks": [],
    "hero_news": {"title": "No Data", "source": "", "url": "#", "summary": ""},
    "secondary_news": []
}

def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return MOCK_DATA

def load_template():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()

def render_secondary_item(item):
    # 渲染列表项
    return f"""
    <div class="group flex items-start gap-3 p-2 rounded-lg hover:bg-white/5 transition-colors cursor-pointer" onclick="window.open('{item['url']}', '_blank')">
        <div class="mt-1 min-w-[4px] h-[4px] rounded-full bg-blue-500 group-hover:bg-blue-400"></div>
        <div class="flex-1">
            <h4 class="text-sm font-medium text-gray-200 group-hover:text-blue-300 transition-colors leading-snug">
                {item['title']}
            </h4>
            <div class="flex items-center gap-2 mt-1">
                <span class="text-[10px] text-gray-500 font-mono uppercase">{item['source']}</span>
                <span class="text-[10px] text-gray-600">·</span>
                <span class="text-[10px] text-gray-500">{item['time']}</span>
            </div>
        </div>
    </div>
    """

def render_stock_item(stock):
    # 渲染股票行
    color_class = "text-green-400 bg-green-400/10" if stock['trend'] == 'up' else "text-red-400 bg-red-400/10"
    return f"""
    <div class="flex justify-between items-center py-1 border-b border-white/5 last:border-0">
        <span class="font-bold text-sm text-gray-300">{stock['symbol']}</span>
        <div class="flex items-center gap-2">
            <span class="text-xs text-gray-500">{stock['price']}</span>
            <span class="font-mono text-[10px] {color_class} px-1.5 py-0.5 rounded">{stock['change']}</span>
        </div>
    </div>
    """

def build():
    # 1. 准备数据
    data = load_data()
    
    # Time strings
    now = datetime.datetime.now()
    date_str_short = now.strftime("%b %d") 
    date_short = now.strftime("%Y.%m.%d")
    session_id = data.get("session_id", "SESS-GEN")

    # 2. 渲染组件
    secondary_items = data.get("secondary_news", [])
    secondary_html = "\n".join([render_secondary_item(i) for i in secondary_items])
    
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
    html = html.replace("{{STOCK_LIST}}", stocks_html)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Successfully built V2 Dashboard at {OUTPUT_PATH}")

if __name__ == "__main__":
    build()
