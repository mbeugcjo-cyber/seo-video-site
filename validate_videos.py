#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""视频源验证脚本 - 检查 CSV 中所有视频 file_code 是否仍然有效

用法:
    python validate_videos.py              # 检查所有视频
    python validate_videos.py --report     # 只输出报告，不逐条显示
    python validate_videos.py --update-csv # 移除失效视频并生成新 CSV
"""

import csv
import os
import sys
import json
import time
import shutil
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
import config

CSV_PATH = os.path.join(os.path.dirname(__file__), 'content', 'videos.csv')
REPORT_PATH = os.path.join(os.path.dirname(__file__), 'output', 'validation_report.json')

# HTTP 请求头（模拟浏览器）
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://www.google.com/',
}


def check_doodstream(file_code: str) -> tuple[bool, str]:
    """检查 DoodStream 视频 - playmogo.com/e/{code}"""
    url = f"https://playmogo.com/e/{file_code}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        text = resp.text.lower()
        # 正常页面包含 player 或 video 相关字样
        if resp.status_code == 200 and ('player' in text or 'video' in text or 'iframe' in text or 'source' in text):
            return (True, f"HTTP {resp.status_code}")
        elif resp.status_code == 404 or 'not found' in text or 'deleted' in text:
            return (False, f"HTTP {resp.status_code} - 视频已删除")
        else:
            return (False, f"HTTP {resp.status_code} - 无法确认")
    except Exception as e:
        return (False, f"连接失败: {e}")


def check_lulustream(file_code: str) -> tuple[bool, str]:
    """检查 LuluStream - luluvid.com/e/{code}"""
    url = f"https://luluvid.com/e/{file_code}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        text = resp.text.lower()
        if resp.status_code == 200 and ('player' in text or 'video' in text or 'jwplayer' in text):
            return (True, f"HTTP {resp.status_code}")
        elif resp.status_code == 404 or 'not found' in text or '404' in text:
            return (False, f"HTTP {resp.status_code} - 视频已删除")
        else:
            return (False, f"HTTP {resp.status_code} - 无法确认")
    except Exception as e:
        return (False, f"连接失败: {e}")


def check_vinovo(file_code: str) -> tuple[bool, str]:
    """检查 Vinovo - vinovo.to/e/{code}"""
    url = f"https://vinovo.to/e/{file_code}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        text = resp.text.lower()
        if resp.status_code == 200 and ('player' in text or 'video' in text):
            return (True, f"HTTP {resp.status_code}")
        elif resp.status_code == 404:
            return (False, f"HTTP {resp.status_code} - 视频已删除")
        else:
            return (False, f"HTTP {resp.status_code} - 无法确认")
    except Exception as e:
        return (False, f"连接失败: {e}")


def check_vidoza(file_code: str) -> tuple[bool, str]:
    """检查 Vidoza - videzz.net/{code}"""
    url = f"https://videzz.net/{file_code}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        text = resp.text.lower()
        if resp.status_code == 200 and ('player' in text or 'video' in text):
            return (True, f"HTTP {resp.status_code}")
        elif resp.status_code == 404:
            return (False, f"HTTP {resp.status_code} - 视频已删除")
        else:
            return (False, f"HTTP {resp.status_code} - 无法确认")
    except Exception as e:
        return (False, f"连接失败: {e}")


# 平台检查函数映射
CHECKERS = {
    'doodstream': check_doodstream,
    'lulustream': check_lulustream,
    'vinovo':     check_vinovo,
    'vidoza':     check_vidoza,
}


def load_csv() -> list[dict]:
    """加载 CSV 中的视频"""
    videos = []
    with open(CSV_PATH, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('title', '').strip() and row.get('file_code', '').strip():
                videos.append(dict(row))
    return videos


def write_csv(videos: list[dict], path: str):
    """写入 CSV"""
    if not videos:
        return
    keys = list(videos[0].keys())
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(videos)


def main():
    if not os.path.exists(CSV_PATH):
        print(f"❌ 未找到 CSV: {CSV_PATH}")
        return 1

    show_detail = '--report' not in sys.argv
    update_csv = '--update-csv' in sys.argv
    verbose = '-v' in sys.argv or '--verbose' in sys.argv

    videos = load_csv()
    print(f"\n{'='*60}")
    print(f"视频源验证工具")
    print(f"共 {len(videos)} 个视频, {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    results = []
    alive = 0
    dead = 0

    for i, v in enumerate(videos):
        title = v.get('title', '').strip()
        platform = v.get('platform', '').strip()
        file_code = v.get('file_code', '').strip()
        slug = v.get('slug', '')

        checker = CHECKERS.get(platform)
        if not checker:
            if show_detail:
                print(f"  [{i+1}/{len(videos)}] ⚠ {title} - 未知平台: {platform}")
            results.append({**v, 'valid': False, 'status': f'未知平台: {platform}'})
            continue

        if show_detail:
            print(f"  [{i+1}/{len(videos)}] {title[:30]:30s} ({platform:12s})... ", end='', flush=True)

        is_valid, status = checker(file_code)

        if verbose and not is_valid:
            # 打印更多调试信息
            url = v.get('watch_url', v.get('embed_url', ''))
            print(f"\n    URL: {url}")

        if show_detail:
            mark = '✅' if is_valid else '❌'
            print(f"{mark} {status}")

        if is_valid:
            alive += 1
        else:
            dead += 1

        results.append({**v, 'valid': is_valid, 'status': status})

        # 请求间隔，避免被封
        time.sleep(1.5)

    # 输出报告
    print(f"\n{'='*60}")
    print(f"验证完成!")
    print(f"  ✅ 有效: {alive}")
    print(f"  ❌ 失效: {dead}")
    print(f"  📊 有效率: {alive/len(videos)*100:.1f}%" if videos else "  📊 无视频")
    print(f"{'='*60}\n")

    if dead > 0:
        print("失效视频:")
        for r in results:
            if not r['valid']:
                print(f"  ❌ [{r['platform']}] {r.get('title','')} (file_code: {r['file_code']})")
        print()

    # 保存报告
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total': len(results),
            'alive': alive,
            'dead': dead,
            'results': results,
        }, f, ensure_ascii=False, indent=2)
    print(f"报告已保存: {REPORT_PATH}")

    # 更新 CSV（移除失效视频）
    if update_csv and dead > 0:
        valid_videos = [r for r in results if r['valid']]
        backup_path = CSV_PATH.replace('.csv', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        shutil.copy2(CSV_PATH, backup_path)
        write_csv(valid_videos, CSV_PATH)
        print(f"\n已备份原文件: {backup_path}")
        print(f"已更新 CSV: 移除了 {dead} 个失效视频, 剩余 {len(valid_videos)} 个")

    return 0 if alive > 0 else 1


if __name__ == '__main__':
    # 安装 requests 如果未安装
    try:
        import requests
    except ImportError:
        print("正在安装 requests...")
        os.system(f"{sys.executable} -m pip install requests -q")
        import requests

    sys.exit(main())
