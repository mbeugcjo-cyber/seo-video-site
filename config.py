# -*- coding: utf-8 -*-
"""站点配置"""
import os

SITE_NAME = "免费短视频在线观看"
SITE_DESCRIPTION = "海量免费短视频在线观看，每日更新精彩剪辑"
SITE_URL = "https://seo-video-site.pages.dev"  # 部署到 Cloudflare Pages 后的域名
SITE_KEYWORDS = "免费视频,在线观看,短视频,精彩剪辑"

# 输出目录
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

# 每页显示的视频数（首页/分类页/标签页）
VIDEOS_PER_PAGE = 30

# 英文分类名 → 中文显示名
CATEGORY_NAMES = {
    "animals": "动物",
    "entertainment": "娱乐",
    "fitness": "健身",
    "food": "美食",
    "gaming": "游戏",
    "music": "音乐",
    "sports": "体育",
    "tech": "科技",
    "travel": "旅行",
}

# Google Analytics 4 ID（留空则不加载统计代码）
# 如何获取: 搜索 Google Analytics → 创建 GA4 媒体资源 → 获取 G-XXXXXXXXXX 格式的 ID
ANALYTICS_ID = ""  # 例如 "G-XXXXXXXXXX"

# Cloudflare Web Analytics Token（二选一，留空不启用）
# 在 Cloudflare Dashboard → Web Analytics 获取
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
}
