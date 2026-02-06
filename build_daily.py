import json
import datetime
import os
import re

# --- 配置 ---
BASE_DIR = "daily_brief"
TEMPLATE_PATH = os.path.join(BASE_DIR, "template.html")
OUTPUT_PATH = os.path.join(BASE_DIR, "index.html")
DATA_PATH = os.path.join(BASE_DIR, "data.json")
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")

WEEKDAY_MAP = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    print("WARNING: No data.json found!")
    return {}


def load_template():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def render_action_item(item):
    priority = item.get("priority", "中")
    if priority == "高":
        color = "#f87171"  # red-400
        bg = "rgba(248, 113, 113, 0.12)"
    elif priority == "低":
        color = "#94a3b8"  # slate-400
        bg = "rgba(148, 163, 184, 0.12)"
    else:
        color = "#fbbf24"  # amber-400
        bg = "rgba(251, 191, 36, 0.12)"

    return f"""
    <div class="flex items-start gap-3">
        <span class="mono text-[10px] px-1.5 py-0.5 rounded" style="color:{color};background-color:{bg};">{priority}优先级</span>
        <div class="flex-1">
            <div class="text-sm text-neutral-200">{item.get('title','')}</div>
            <div class="text-[11px] text-neutral-500 mt-1">{item.get('detail','')}</div>
        </div>
    </div>
    """


def render_signal_item(item):
    return f"""
    <div class="flex items-start gap-3">
        <div class="w-1.5 h-1.5 mt-2 rounded-full bg-blue-400"></div>
        <div class="flex-1">
            <a href="{item.get('url','#')}" target="_blank" class="text-sm text-neutral-300 hover:text-white transition-colors">{item.get('title','')}</a>
            <div class="text-[11px] text-neutral-500 mt-1">{item.get('detail','')} · {item.get('source','')} · {item.get('time','')}</div>
        </div>
    </div>
    """


def render_important_card(item):
    return f"""
    <div class="group relative p-5 rounded-xl transition-all hover:bg-neutral-900" style="background-color:#111111;border:1px solid #262626;">
        <div class="flex items-center justify-between mb-3">
            <span class="mono text-[9px] font-bold text-blue-300/80 uppercase tracking-wider px-1.5 py-0.5 rounded border border-blue-500/20 bg-blue-500/5">{item.get('source','')}</span>
            <span class="mono text-[10px] text-neutral-600">{item.get('time','')}</span>
        </div>
        <a href="{item.get('url','#')}" target="_blank" class="block">
            <h3 class="text-sm font-medium text-neutral-200 group-hover:text-white leading-relaxed transition-colors">{item.get('title','')}</h3>
            <p class="text-[11px] text-neutral-500 mt-2 leading-relaxed">{item.get('summary','')}</p>
        </a>
    </div>
    """


def render_simple_list(item):
    return f"""
    <div class="flex items-start gap-3 py-2 border-b border-neutral-800/50 last:border-0">
        <div class="w-1.5 h-1.5 mt-2 rounded-full bg-neutral-500"></div>
        <div class="flex-1">
            <a href="{item.get('url','#')}" target="_blank" class="text-sm text-neutral-300 hover:text-white transition-colors">{item.get('title','')}</a>
            <div class="text-[11px] text-neutral-500 mt-1">{item.get('summary','')} · {item.get('source','')} · {item.get('time','')}</div>
        </div>
    </div>
    """


def render_theme_tag(tag):
    return f"<span class=\"text-[10px] px-2 py-0.5 rounded border border-neutral-800 text-neutral-300\">{tag}</span>"


def extract_metadata(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        date_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content)
        date_str = date_match.group(1) if date_match else "未知日期"
        hero_match = re.search(r'<h2[^>]*>\s*([^<]+)\s*</h2>', content)
        hero_title = hero_match.group(1).strip() if hero_match else "每日情报"
        return {"date": date_str, "hero": hero_title}
    except Exception:
        return {"date": "未知", "hero": "错误"}


def update_archive_index():
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
    files = sorted([f for f in os.listdir(ARCHIVE_DIR) if f.endswith(".html") and f != "index.html"], reverse=True)

    cards_html = ""
    for f in files:
        file_path = os.path.join(ARCHIVE_DIR, f)
        meta = extract_metadata(file_path)
        cards_html += f"""
        <a href=\"{f}\" class=\"group relative block p-6 bg-white/5 border border-white/10 rounded-xl overflow-hidden hover:border-blue-500/50 hover:bg-white/10 transition-all duration-300\">
            <div class=\"absolute inset-0 bg-gradient-to-r from-blue-500/0 via-blue-500/0 to-blue-500/0 group-hover:from-blue-500/5 group-hover:to-purple-500/5 transition-all\"></div>
            <div class=\"flex justify-between items-start mb-4\">
                <div class=\"flex flex-col\">
                    <span class=\"text-xs font-mono text-blue-300 uppercase tracking-wider\">简报</span>
                    <span class=\"text-xl font-bold text-white mt-1\">{meta['date']}</span>
                </div>
            </div>
            <h3 class=\"text-gray-300 font-medium leading-relaxed group-hover:text-white transition-colors line-clamp-2\">{meta['hero']}</h3>
        </a>
        """

    html = f"""<!DOCTYPE html><html lang=\"zh-CN\" class=\"dark\"><head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"><title>归档</title><script src=\"https://cdn.tailwindcss.com\"></script><style>body{{background-color:#050505;color:#fff;min-height:100vh}}</style></head><body class=\"p-6 md:p-12\"><div class=\"max-w-5xl mx-auto\"><header class=\"mb-12 flex justify-between\"><div><h1 class=\"text-3xl font-bold\">归档时间线</h1></div><a href=\"../index.html\" class=\"text-sm text-gray-500 hover:text-white\">&larr; 返回首页</a></header><div class=\"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6\">{cards_html}</div></div></body></html>"""

    with open(os.path.join(ARCHIVE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


def build():
    data = load_data()
    if not data:
        return

    now = datetime.datetime.now()
    date_cn = now.strftime("%m月%d日")
    date_full = now.strftime("%Y.%m.%d")
    weekday_cn = WEEKDAY_MAP[now.weekday()]
    date_iso = now.strftime("%Y-%m-%d")
    session_id = data.get("session_id", "SESS-GEN")

    html = load_template()
    html = html.replace("{{DATE_CN}}", date_cn)
    html = html.replace("{{DATE_FULL}}", date_full)
    html = html.replace("{{WEEKDAY_CN}}", weekday_cn)
    html = html.replace("{{SESSION_ID}}", session_id)

    weather = data.get("weather", {})
    html = html.replace("{{WEATHER_CITY}}", weather.get("city", "--"))
    html = html.replace("{{WEATHER_TEMP_VAL}}", weather.get("temp", "--"))
    html = html.replace("{{WEATHER_COND}}", weather.get("cond", "--"))

    hero = data.get("hero_news", {})
    html = html.replace("{{HERO_TITLE}}", hero.get("title", "暂无关键事件"))
    html = html.replace("{{HERO_SOURCE}}", hero.get("source", ""))
    html = html.replace("{{HERO_SUMMARY}}", hero.get("summary", ""))
    html = html.replace("{{HERO_TAKEAWAY}}", hero.get("takeaway", ""))
    html = html.replace("{{HERO_URL}}", hero.get("url", "#"))

    themes = data.get("themes", [])
    html = html.replace("{{THEME_TAGS}}", "\n".join([render_theme_tag(t) for t in themes]) or "<span class=\"text-[10px] text-neutral-600\">暂无主题</span>")

    action_list = data.get("actions", [])
    signal_list = data.get("signals", [])
    important_list = data.get("important", [])
    save_list = data.get("save", [])
    ignore_list = data.get("ignore", [])
    agent_news = data.get("agent_news", [])
    tech_news = data.get("tech_news", [])

    html = html.replace("{{ACTION_LIST}}", "\n".join([render_action_item(i) for i in action_list]) or "<div class=\"text-xs text-neutral-600\">暂无需要处理的事项</div>")
    html = html.replace("{{SIGNAL_LIST}}", "\n".join([render_signal_item(i) for i in signal_list]) or "<div class=\"text-xs text-neutral-600\">暂无新增信号</div>")
    html = html.replace("{{IMPORTANT_LIST}}", "\n".join([render_important_card(i) for i in important_list]) or "<div class=\"text-xs text-neutral-600\">暂无重要信息</div>")
    html = html.replace("{{AGENT_NEWS_LIST}}", "\n".join([render_simple_list(i) for i in agent_news]) or "<div class=\"text-xs text-neutral-600\">暂无条目</div>")
    html = html.replace("{{TECH_NEWS_LIST}}", "\n".join([render_simple_list(i) for i in tech_news]) or "<div class=\"text-xs text-neutral-600\">暂无条目</div>")
    html = html.replace("{{SAVE_LIST}}", "\n".join([render_simple_list(i) for i in save_list]) or "<div class=\"text-xs text-neutral-600\">暂无条目</div>")
    html = html.replace("{{IGNORE_LIST}}", "\n".join([render_simple_list(i) for i in ignore_list]) or "<div class=\"text-xs text-neutral-600\">暂无条目</div>")

    index_html = html.replace("{{ARCHIVE_LINK}}", "archive/index.html")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(index_html)

    archive_html = html.replace("{{ARCHIVE_LINK}}", "index.html")
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
    with open(os.path.join(ARCHIVE_DIR, f"{date_iso}.html"), "w", encoding="utf-8") as f:
        f.write(archive_html)

    update_archive_index()
    print(f"Successfully built Dashboard & Archive: {date_iso}")


if __name__ == "__main__":
    build()
