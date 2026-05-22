# -*- coding: utf-8 -*-
"""站点配置"""
import os

# ── 站点元信息（默认英文） ──
SITE_NAME = "Free Short Videos"
SITE_DESCRIPTION = "Watch free short videos online, daily updates of exciting clips"
SITE_URL = "https://seo-video-site.pages.dev"
SITE_KEYWORDS = "free videos, short videos, online video, exciting clips"

# 中文站点名（语言切换用）
SITE_NAME_ZH = "免费短视频在线观看"
SITE_DESCRIPTION_ZH = "海量免费短视频在线观看，每日更新精彩剪辑"
SITE_KEYWORDS_ZH = "免费视频,在线观看,短视频,精彩剪辑"

# 默认语言
DEFAULT_LANG = "en"

# 输出目录
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

# 每页显示的视频数
VIDEOS_PER_PAGE = 30

# 分类名称（英文key → 英文显示名 / 中文显示名）
CATEGORY_NAMES = {
    "animals": ("Animals", "动物"),
    "entertainment": ("Entertainment", "娱乐"),
    "fitness": ("Fitness", "健身"),
    "food": ("Food", "美食"),
    "gaming": ("Gaming", "游戏"),
    "music": ("Music", "音乐"),
    "sports": ("Sports", "体育"),
    "tech": ("Tech", "科技"),
    "travel": ("Travel", "旅行"),
}

# ── UI 多语言字符串 ──
UI_STRINGS = {
    "en": {
        "site_name": SITE_NAME,
        "site_description": SITE_DESCRIPTION,
        "site_keywords": SITE_KEYWORDS,
        "nav_home": "Home",
        "nav_search": "Search",
        "nav_sitemap": "Sitemap",
        "hero_title": SITE_NAME,
        "hero_subtitle": SITE_DESCRIPTION,
        "section_categories": "Categories",
        "section_latest": "Latest Videos",
        "section_related": "Related Videos",
        "video_platform": "Platform",
        "video_category": "Category",
        "video_tags": "Tags",
        "video_not_found": "Video not found",
        "search_title": "Search Videos",
        "search_desc": "Search by video title, tags or category",
        "search_placeholder": "Enter keywords to search...",
        "search_btn": "Search",
        "search_hint": "Enter keywords to start searching",
        "search_no_results": 'No videos found for',
        "search_results": "results found",
        "search_error": "Failed to load video data",
        "search_network_error": "Network error, unable to load video data",
        "pagination_prev": "‹ Prev",
        "pagination_next": "Next ›",
        "page_404_title": "404",
        "page_404_msg": "Page not found",
        "page_404_btn": "Back to Home",
        "footer_text": "Content from the internet, for learning purposes only.",
        "breadcrumb_home": "Home",
        "cat_videos": "Videos",
        "tag_label": "Tag",
        "tag_videos": "related videos",
        "enter_site": "Enter Site",
        "stat_videos": "Videos",
        "stat_categories": "Categories",
        "stat_tags": "Tags",
        "search_results_found": "results found",
        "search_results_format_en": "{count} results found",
        "search_results_format_zh": "找到 {count} 个相关视频",
        "lang_en": "English",
        "lang_zh": "中文",
        "category_all": "All Categories",
    },
    "zh": {
        "site_name": SITE_NAME_ZH,
        "site_description": SITE_DESCRIPTION_ZH,
        "site_keywords": SITE_KEYWORDS_ZH,
        "nav_home": "首页",
        "nav_search": "搜索",
        "nav_sitemap": "站点地图",
        "hero_title": SITE_NAME_ZH,
        "hero_subtitle": SITE_DESCRIPTION_ZH,
        "section_categories": "视频分类",
        "section_latest": "最新视频",
        "section_related": "相关视频推荐",
        "video_platform": "平台",
        "video_category": "分类",
        "video_tags": "标签",
        "video_not_found": "视频未找到",
        "search_title": "搜索视频",
        "search_desc": "输入关键词搜索视频标题、标签或分类",
        "search_placeholder": "输入关键词搜索...",
        "search_btn": "搜索",
        "search_hint": "输入关键词开始搜索",
        "search_no_results": "没有找到与",
        "search_results": "个相关视频",
        "search_error": "加载视频数据失败",
        "search_network_error": "网络错误，无法加载视频数据",
        "pagination_prev": "‹ 上一页",
        "pagination_next": "下一页 ›",
        "page_404_title": "404",
        "page_404_msg": "页面未找到",
        "page_404_btn": "返回首页",
        "footer_text": "内容来自网络，仅供学习交流。",
        "breadcrumb_home": "首页",
        "cat_videos": "个视频",
        "tag_label": "标签",
        "tag_videos": "个相关视频",
        "enter_site": "进入视频站",
        "stat_videos": "精选视频",
        "stat_categories": "视频分类",
        "stat_tags": "热门标签",
        "search_results_found": "个相关视频",
        "lang_en": "English",
        "lang_zh": "中文",
        "category_all": "全部分类",
    },
}

# 分类名查询辅助函数
def cat_name(cat_key: str, lang: str = "en") -> str:
    """获取指定语言的分类显示名"""
    pair = CATEGORY_NAMES.get(cat_key)
    if not pair:
        return cat_key
    return pair[0] if lang == "en" else pair[1]

def get_ui(lang: str = "en") -> dict:
    """获取指定语言的 UI 字符串"""
    return UI_STRINGS.get(lang, UI_STRINGS["en"])

# Google Analytics
ANALYTICS_ID = ""

# Cloudflare Web Analytics Token
CLOUDFLARE_ANALYTICS_TOKEN = ""

# 平台嵌入 URL 模板
EMBED_MAP = {
    "doodstream": {
        "name": "DoodStream",
        "embed_url": "https://playmogo.com/e/{file_code}",
        "watch_url": "https://playmogo.com/d/{file_code}",
    },
    "lulustream": {
        "name": "LuluStream",
        "embed_url": "https://luluvid.com/e/{file_code}",
        "watch_url": "https://luluvid.com/{file_code}",
    },
    "vinovo": {
        "name": "Vinovo",
        "embed_url": "https://vinovo.to/e/{file_code}",
        "watch_url": "https://vinovo.to/d/{file_code}",
    },
    "vidoza": {
        "name": "Vidoza",
        "embed_url": "https://videzz.net/{file_code}",
        "watch_url": "https://videzz.net/{file_code}",
    },
    "upbolt": {
        "name": "UpBolt",
        "embed_url": "https://upbolt.to/e/{file_code}",
        "watch_url": "https://upbolt.to/{file_code}",
    },
}
