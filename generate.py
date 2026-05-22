#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEO 视频承接站 - 静态站点生成器

用法:
    python generate.py              # 生成所有页面
    python generate.py --serve      # 生成后启动本地 HTTP 服务器预览

数据来源: content/videos.csv
输出目录: output/
"""
import csv, os, sys, html, json, shutil, datetime, hashlib, math
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape
from urllib.parse import urlparse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 确保 jinja2 可用
try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("请先安装依赖: pip install jinja2")
    sys.exit(1)

# 加载配置
sys.path.insert(0, os.path.dirname(__file__))
import config

# ── 工具函数 ────────────────────────────────────────────

def slugify(text: str) -> str:
    """将中文标题转为拼音式 slug"""
    import re
    s = text.lower().strip()
    # 保留中文、字母、数字，其他转为连字符
    s = re.sub(r'[^\w一-鿿-]', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')


def load_videos(csv_path: str) -> list[dict]:
    """从 CSV 加载视频列表，返回增强后的 dict 列表"""
    if not os.path.exists(csv_path):
        print(f"⚠ 未找到视频数据: {csv_path}")
        return []

    videos = []
    with open(csv_path, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get('title', '').strip()
            platform = row.get('platform', '').strip()
            file_code = row.get('file_code', '').strip()
            if not title or not platform or not file_code:
                continue

            # 获取平台配置
            platform_config = config.EMBED_MAP.get(platform)
            if not platform_config:
                print(f"⚠ 未知平台 '{platform}'，跳过: {title}")
                continue

            slug = row.get('slug', '').strip() or slugify(title)
            category = row.get('category', '').strip() or '未分类'
            tags_raw = row.get('tags', '').strip()
            tags = [t.strip() for t in tags_raw.split(',') if t.strip()] if tags_raw else []
            description = row.get('description', '').strip() or f"在线观看{title}高清免费视频"
            thumbnail = row.get('thumbnail', '').strip()

            videos.append({
                'title': title,
                'slug': slug,
                'platform': platform,
                'platform_name': platform_config['name'],
                'file_code': file_code,
                'embed_url': platform_config['embed_url'].format(file_code=file_code),
                'watch_url': platform_config['watch_url'].format(file_code=file_code),
                'category': category,
                'tags': tags,
                'description': description,
                'thumbnail': thumbnail,
                'date': row.get('date', '').strip() or datetime.date.today().isoformat(),
            })

    # 去重（相同 slug 只保留最后一个）
    seen = set()
    unique = []
    for v in videos:
        if v['slug'] not in seen:
            seen.add(v['slug'])
            unique.append(v)
    return unique


def build_related(videos: list[dict], current: dict, max_count: int = 8) -> list[dict]:
    """找出同分类的相关视频（排除当前视频）"""
    same_cat = [v for v in videos if v['category'] == current['category'] and v['slug'] != current['slug']]
    if len(same_cat) >= max_count:
        return same_cat[:max_count]
    # 不足则补充其他视频
    others = [v for v in videos if v['slug'] != current['slug'] and v not in same_cat]
    return same_cat + others[:max_count - len(same_cat)]


def write_html(filepath: str, content: str):
    """安全写入 HTML 文件"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def thumb_gradient(slug: str) -> str:
    """从 slug 生成确定性渐变色 CSS"""
    h = hashlib.md5(slug.encode()).hexdigest()
    def _c(offset):
        return f'#{h[offset:offset+2]}{h[offset+2:offset+4]}{h[offset+4:offset+6]}'
    return f'linear-gradient(135deg, {_c(0)}, {_c(6)})'


def cat_display(cat: str) -> str:
    """英文分类名 → 中文显示名"""
    names = getattr(config, 'CATEGORY_NAMES', {})
    return names.get(cat, cat)


def paginate(items: list, per_page: int):
    """将列表分页，返回 [(page_num, page_items, total_pages), ...]"""
    total = len(items)
    total_pages = max(1, math.ceil(total / per_page))
    pages = []
    for p in range(1, total_pages + 1):
        start = (p - 1) * per_page
        end = start + per_page
        pages.append((p, items[start:end], total_pages))
    return pages


def generate_thumbnails(videos: list[dict], out_dir: str) -> int:
    """用 Pillow 为没有缩略图的视频生成渐变缩略图"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("  ⚠ Pillow 未安装，跳过缩略图生成")
        return 0

    thumb_dir = os.path.join(out_dir, 'static', 'thumbnails')
    os.makedirs(thumb_dir, exist_ok=True)
    generated = 0

    # 尝试加载中文字体
    font = None
    for font_path in [
        'C:/Windows/Fonts/msyh.ttc',    # Microsoft YaHei
        'C:/Windows/Fonts/msyhbd.ttc',   # Microsoft YaHei Bold
        'C:/Windows/Fonts/simhei.ttf',   # SimHei
        'C:/Windows/Fonts/yahei.ttf',    # YaHei fallback
    ]:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, 26)
                break
            except:
                continue
    if font is None:
        font = ImageFont.load_default()

    for v in videos:
        # 已经有缩略图的跳过
        if v.get('thumbnail'):
            continue

        # 已经有文件则跳过
        thumb_path = os.path.join(thumb_dir, f"{v['slug']}.jpg")
        thumb_url = f"/static/thumbnails/{v['slug']}.jpg"
        if os.path.exists(thumb_path):
            v['thumbnail'] = thumb_url
            continue

        # 从 slug 取色
        h = hashlib.md5(v['slug'].encode()).hexdigest()
        def _rgb(offset):
            return (int(h[offset:offset+2], 16), int(h[offset+2:offset+4], 16), int(h[offset+4:offset+6], 16))
        c1, c2 = _rgb(0), _rgb(6)

        # 创建渐变图片 640x360
        img = Image.new('RGB', (640, 360))
        draw = ImageDraw.Draw(img)
        for y in range(360):
            ratio = y / 360
            r = int(c1[0] * (1-ratio) + c2[0] * ratio)
            g = int(c1[1] * (1-ratio) + c2[1] * ratio)
            b = int(c1[2] * (1-ratio) + c2[2] * ratio)
            draw.line([(0, y), (640, y)], fill=(r, g, b))

        # 绘制标题（自动换行）
        title = v['title']
        lines = []
        for i in range(0, len(title), 10):
            lines.append(title[i:i+10])

        y_pos = 180 - (len(lines) * 18)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            x = (640 - tw) // 2
            # 阴影 + 文字
            draw.text((x+2, y_pos+2), line, fill=(0, 0, 0, 160), font=font)
            draw.text((x, y_pos), line, fill=(255, 255, 255), font=font)
            y_pos += 36

        img.save(thumb_path, 'JPEG', quality=80)
        v['thumbnail'] = thumb_url
        generated += 1

    return generated


# ── 主生成逻辑 ──────────────────────────────────────────

def generate():
    out_dir = config.OUTPUT_DIR
    site_url = config.SITE_URL.rstrip('/')

    # 初始化 Jinja2
    env = Environment(
        loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
        autoescape=True,
    )

    # 传递给所有模板的全局变量
    cat_names = getattr(config, 'CATEGORY_NAMES', {})
    globals = {
        'site_name': config.SITE_NAME,
        'site_description': config.SITE_DESCRIPTION,
        'site_url': site_url,
        'site_keywords': config.SITE_KEYWORDS,
        'analytics_id': getattr(config, 'ANALYTICS_ID', ''),
        'cloudflare_analytics_token': getattr(config, 'CLOUDFLARE_ANALYTICS_TOKEN', ''),
        'cat_names': cat_names,
    }

    # 加载视频数据
    csv_path = os.path.join(os.path.dirname(__file__), 'content', 'videos.csv')
    videos = load_videos(csv_path)
    print(f"加载 {len(videos)} 个视频")

    # 提取所有视频平台的域名（用于 preconnect 预连接）
    embed_domains = set()
    for v in videos:
        try:
            domain = urlparse(v['embed_url']).hostname
            if domain:
                embed_domains.add(domain)
        except Exception:
            pass
    globals['embed_domains'] = sorted(embed_domains)

    # 为每个视频添加缩略图渐变色
    for v in videos:
        v['thumb_gradient'] = thumb_gradient(v['slug'])

    # 先生成缩略图（确保 v['thumbnail'] 在页面渲染前已赋值）
    print("生成缩略图...")
    n_thumbs = generate_thumbnails(videos, out_dir)
    print(f"  生成 {n_thumbs} 个缩略图")

    if not videos:
        print("⚠ 没有视频数据，生成空站点")
        # 仍然生成首页和 robots.txt

    # 按分类统计
    cat_counts = {}
    for v in videos:
        cat_counts[v['category']] = cat_counts.get(v['category'], 0) + 1
    categories = sorted(cat_counts.items())  # [(cat, count), ...]

    # ── 1. 首页（分页）──
    per_page = config.VIDEOS_PER_PAGE
    sorted_videos = list(reversed(videos))  # 最新优先
    home_pages = paginate(sorted_videos, per_page)
    print(f"生成首页（共 {len(home_pages)} 页）...")
    tmpl_home = env.get_template('index.html')
    for page_num, page_videos, total_pages in home_pages:
        if page_num == 1:
            out_path = os.path.join(out_dir, 'index.html')
        else:
            out_path = os.path.join(out_dir, 'page', str(page_num), 'index.html')
        html_out = tmpl_home.render(
            **globals,
            videos=page_videos,
            categories=categories,
            page=page_num,
            total_pages=total_pages,
        )
        write_html(out_path, html_out)

    # ── 2. 视频详情页 ──
    print(f"生成 {len(videos)} 个视频详情页...")
    for v in videos:
        related = build_related(videos, v)
        tmpl = env.get_template('video.html')
        html_out = tmpl.render(**globals, video=v, related=related)
        write_html(os.path.join(out_dir, 'watch', v['slug'], 'index.html'), html_out)

    # ── 3. 分类页（分页）──
    print(f"生成 {len(categories)} 个分类页...")
    tmpl_cat = env.get_template('category.html')
    for cat, _ in categories:
        cat_videos = [v for v in videos if v['category'] == cat]
        cat_pages = paginate(cat_videos, per_page)
        for page_num, page_videos, total_pages in cat_pages:
            if page_num == 1:
                out_path = os.path.join(out_dir, 'genre', cat, 'index.html')
            else:
                out_path = os.path.join(out_dir, 'genre', cat, 'page', str(page_num), 'index.html')
            html_out = tmpl_cat.render(
                **globals, category=cat, videos=page_videos,
                page=page_num, total_pages=total_pages,
            )
            write_html(out_path, html_out)

    # ── 4. 标签页（分页）──
    tag_groups = {}
    for v in videos:
        for tag in v['tags']:
            tag_groups.setdefault(tag, []).append(v)
    print(f"生成 {len(tag_groups)} 个标签页...")
    tmpl_tag = env.get_template('tag.html')
    for tag, tag_videos in tag_groups.items():
        tag_pages = paginate(tag_videos, per_page)
        for page_num, page_videos, total_pages in tag_pages:
            if page_num == 1:
                out_path = os.path.join(out_dir, 'tag', tag, 'index.html')
            else:
                out_path = os.path.join(out_dir, 'tag', tag, 'page', str(page_num), 'index.html')
            html_out = tmpl_tag.render(
                **globals, tag=tag, videos=page_videos,
                page=page_num, total_pages=total_pages,
            )
            write_html(out_path, html_out)

    # ── 5. Sitemap（含 lastmod + 分页）──
    print("生成 sitemap.xml...")
    today_str = datetime.date.today().isoformat()

    def _sitemap_url(loc: str, priority: str, lastmod: str = ""):
        parts = [f'<loc>{xml_escape(loc)}</loc>']
        if lastmod:
            parts.append(f'<lastmod>{lastmod}</lastmod>')
        parts.append(f'<priority>{priority}</priority>')
        return f'<url>{"".join(parts)}</url>'

    sitemap_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    sitemap_parts.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    # 首页（含分页）
    for p in range(1, len(home_pages) + 1):
        url = f'{site_url}/' if p == 1 else f'{site_url}/page/{p}/'
        sitemap_parts.append(_sitemap_url(url, '1.0', today_str))

    # 搜索页
    sitemap_parts.append(_sitemap_url(f'{site_url}/search/', '0.5', today_str))

    # 分类页（含分页）
    for cat, _ in categories:
        cat_vids = [v for v in videos if v['category'] == cat]
        cat_pgs = paginate(cat_vids, per_page)
        for p in range(1, len(cat_pgs) + 1):
            url = f'{site_url}/genre/{cat}/' if p == 1 else f'{site_url}/genre/{cat}/page/{p}/'
            sitemap_parts.append(_sitemap_url(url, '0.8', today_str))

    # 标签页（含分页）
    for tag in tag_groups:
        tag_vids = tag_groups[tag]
        tag_pgs = paginate(tag_vids, per_page)
        for p in range(1, len(tag_pgs) + 1):
            url = f'{site_url}/tag/{tag}/' if p == 1 else f'{site_url}/tag/{tag}/page/{p}/'
            sitemap_parts.append(_sitemap_url(url, '0.6', today_str))

    # 视频页
    for v in videos:
        sitemap_parts.append(_sitemap_url(
            f'{site_url}/watch/{v["slug"]}/', '0.9', today_str))

    sitemap_parts.append('</urlset>')
    write_html(os.path.join(out_dir, 'sitemap.xml'), '\n'.join(sitemap_parts))

    # ── 6. RSS Feed ──
    print("生成 rss.xml...")
    rss_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    rss_parts.append('<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">')
    rss_parts.append('<channel>')
    rss_parts.append(f'  <title>{xml_escape(config.SITE_NAME)}</title>')
    rss_parts.append(f'  <link>{xml_escape(site_url)}/</link>')
    rss_parts.append(f'  <description>{xml_escape(config.SITE_DESCRIPTION)}</description>')
    rss_parts.append(f'  <language>zh-CN</language>')
    rss_parts.append(f'  <lastBuildDate>{datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>')
    rss_parts.append(f'  <atom:link href="{xml_escape(site_url)}/rss.xml" rel="self" type="application/rss+xml"/>')
    for v in reversed(videos):
        rss_parts.append('  <item>')
        rss_parts.append(f'    <title>{xml_escape(v["title"])}</title>')
        rss_parts.append(f'    <link>{xml_escape(site_url)}/watch/{v["slug"]}/</link>')
        rss_parts.append(f'    <guid>{xml_escape(site_url)}/watch/{v["slug"]}/</guid>')
        rss_parts.append(f'    <description>{xml_escape(v["description"])}</description>')
        rss_parts.append(f'    <category>{xml_escape(cat_display(v["category"]))}</category>')
        rss_parts.append(f'    <pubDate>{v["date"]}</pubDate>')
        rss_parts.append('  </item>')
    rss_parts.append('</channel>')
    rss_parts.append('</rss>')
    write_html(os.path.join(out_dir, 'rss.xml'), '\n'.join(rss_parts))

    # ── 7. robots.txt ──
    print("生成 robots.txt...")
    robots = f"""User-agent: *
Allow: /
Sitemap: {site_url}/sitemap.xml
"""
    write_html(os.path.join(out_dir, 'robots.txt'), robots)

    # Cloudflare Pages _redirects: /page/1/ → /
    redirects = "/page/1/* /:splat 301"
    write_html(os.path.join(out_dir, '_redirects'), redirects)

    # ── 8. 404 页面 ──
    print("生成 404.html...")
    tmpl_404 = env.get_template('404.html')
    html_404 = tmpl_404.render(**globals)
    write_html(os.path.join(out_dir, '404.html'), html_404)

    # ── 9. 搜索页（纯前端搜索，使用 videos.json）──
    print("生成搜索页...")
    tmpl_search = env.get_template('search.html')
    html_search = tmpl_search.render(**globals)
    write_html(os.path.join(out_dir, 'search', 'index.html'), html_search)

    # ── 10. 导出视频映射 JSON（供自动化工具使用） ──
    mapping = []
    for v in videos:
        mapping.append({
            'slug': v['slug'],
            'title': v['title'],
            'platform': v['platform'],
            'file_code': v['file_code'],
            'category': v['category'],
            'tags': v['tags'],
            'embed_url': v['embed_url'],
            'watch_url': v['watch_url'],
        })
    mapping_path = os.path.join(out_dir, 'videos.json')
    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump({'videos': mapping, 'site_url': site_url}, f, ensure_ascii=False, indent=2)
    print(f"导出视频映射: {mapping_path}")

    # ── 11. 复制静态文件（CSS 压缩）──
    print("复制静态文件...")
    static_src = os.path.join(os.path.dirname(__file__), 'static')
    css_path = os.path.join(static_src, 'style.css')
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    # 简单 CSS 压缩：去除注释 + 多余空白
    import re
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    css_content = re.sub(r'\s+', ' ', css_content)
    css_content = re.sub(r'\s*([{};,:])\s*', r'\1', css_content)
    css_content = css_content.strip()
    with open(os.path.join(out_dir, 'style.css'), 'w', encoding='utf-8') as f:
        f.write(css_content)

    # ── 统计 ──
    all_page_files = []
    for root, _dirs, fnames in os.walk(out_dir):
        for f in fnames:
            if f == 'index.html':
                all_page_files.append(os.path.relpath(os.path.join(root, f), out_dir))
    print(f"\n{'='*50}")
    print(f"[OK] 生成完成!")
    print(f"   视频: {len(videos)}")
    print(f"   分类: {len(categories)}")
    print(f"   标签: {len(tag_groups)}")
    print(f"   HTML 页面: {len(all_page_files)}")
    print(f"   RSS: rss.xml")
    print(f"   输出目录: {out_dir}")
    print(f"{'='*50}")


# ── 本地预览服务器 ─────────────────────────────────────

def serve():
    """启动本地 HTTP 服务器预览生成的站点"""
    out_dir = config.OUTPUT_DIR
    port = 8000
    import http.server
    handler = http.server.SimpleHTTPRequestHandler

    os.chdir(out_dir)
    print(f"预览服务器: http://localhost:{port}")
    print(f"输出目录: {out_dir}")
    print("按 Ctrl+C 停止")
    http.server.HTTPServer(("", port), handler).serve_forever()


# ── 入口 ────────────────────────────────────────────────

if __name__ == "__main__":
    if "--serve" in sys.argv:
        generate()
        serve()
    else:
        generate()
