import os
from datetime import datetime

# 配置（改成你的信息）
GITHUB_USERNAME = "L-030119"
REPO_NAME = "my-private-rss"
ARTICLES_FOLDER = "articles"  # 这里是articles文件夹的相对路径
RSS_FILE = "my-rss.xml"

def get_articles():
    # 检查articles文件夹是否存在（已存在则跳过创建）
    if not os.path.exists(ARTICLES_FOLDER):
        os.makedirs(ARTICLES_FOLDER)
        print("⚠️ 已创建articles文件夹，请放入md文章")
        return []
    
    # 读取已有的md文章
    articles = []
    for filename in os.listdir(ARTICLES_FOLDER):
        if filename.endswith(".md"):
            # 从文件名提取标题和日期（比如20251218_测试1文章.md）
            if "_" in filename:
                date_str, title = filename.split("_", 1)
                title = title.replace(".md", "")
                # 解析日期
                try:
                    pub_date = datetime.strptime(date_str, "%Y%m%d").strftime("%a, %d %b %Y 00:00:00 GMT")
                except:
                    pub_date = datetime.now().strftime("%a, %d %b %Y 00:00:00 GMT")
                # 文章链接
                link = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/main/{ARTICLES_FOLDER}/{filename}"
                # 读取文章内容作为描述
                with open(os.path.join(ARTICLES_FOLDER, filename), "r", encoding="utf-8") as f:
                    content = f.read().strip()
                articles.append({
                    "title": title,
                    "link": link,
                    "description": content,
                    "pub_date": pub_date,
                    "guid": link
                })
    return articles

def generate_rss(articles):
    # RSS模板
    rss_header = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>我的私人RSS库</title>
    <link>https://github.com/{GITHUB_USERNAME}/{REPO_NAME}</link>
    <description>我的文章集合</description>
    <language>zh-CN</language>
    <lastBuildDate>{datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")}</lastBuildDate>
"""
    rss_items = ""
    for article in articles:
        rss_items += f"""
    <item>
      <title>{article['title']}</title>
      <link>{article['link']}</link>
      <description><![CDATA[{article['description']}]]></description>
      <pubDate>{article['pub_date']}</pubDate>
      <guid>{article['guid']}</guid>
    </item>
"""
    rss_footer = """
  </channel>
</rss>
"""
    # 写入RSS文件
    with open(RSS_FILE, "w", encoding="utf-8") as f:
        f.write(rss_header + rss_items + rss_footer)
    print(f"✅ RSS生成成功！共处理 {len(articles)} 篇文章")

if __name__ == "__main__":
    articles = get_articles()
    if articles:
        generate_rss(articles)
    else:
        print("ℹ️ 目前没有可处理的md文章")