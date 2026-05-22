#!/usr/bin/env python3
"""打包站点并打开 Cloudflare 部署页面，用户手动拖拽上传"""
import io, json, os, sys, zipfile, webbrowser, subprocess

OUTPUT_DIR = r"C:\Users\sg067\Desktop\seo-site-generator\output"
PROJECT_NAME = "seo-video-site"
ACCOUNT_ID = "6fd26b9b0b90a6037772e5aa62a191af"

def create_zip() -> tuple[bytes, int]:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, fnames in os.walk(OUTPUT_DIR):
            for fname in fnames:
                filepath = os.path.join(root, fname)
                rel = os.path.relpath(filepath, OUTPUT_DIR).replace("\\", "/")
                zf.write(filepath, rel)
    data = buf.getvalue()
    n = len(zipfile.ZipFile(io.BytesIO(data), "r").namelist())
    return data, n

def main():
    zip_bytes, n_files = create_zip()
    print(f"打包完成: {len(zip_bytes)/1024:.1f} KB, {n_files} 个文件")

    # 保存 zip 到桌面
    zip_path = os.path.join(os.path.dirname(OUTPUT_DIR), "deploy.zip")
    with open(zip_path, "wb") as f:
        f.write(zip_bytes)
    print(f"已保存: {zip_path}")

    # 打开 Cloudflare 部署页面
    url = f"https://dash.cloudflare.com/{ACCOUNT_ID}/pages/view/{PROJECT_NAME}"
    print(f"\n{'='*60}")
    print("请手动部署:")
    print(f"1. 浏览器已打开 Cloudflare 部署页面")
    print(f"2. 点击「创建部署」按钮")
    print(f"3. 拖拽以下文件到上传区域:")
    print(f"   {zip_path}")
    print(f"{'='*60}\n")

    # 尝试用系统默认浏览器打开
    try:
        webbrowser.open(url)
    except:
        subprocess.Popen(["cmd", "/c", "start", url], shell=True)

    input("部署完成后按 Enter 退出...")

if __name__ == "__main__":
    main()
