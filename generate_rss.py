import os
import re
from datetime import datetime
from xml.etree import ElementTree as ET
from xml.dom import minidom

# ---------------------- 配置项（只改这2处！）----------------------
GITHUB_USERNAME = "L-030119"  # 改：比如你的账号是abc123，就填"abc123"
REPO_NAME = "my-private-rss"            # 改：你的仓库名（截图里是my-private-rss，不用动）
ARTICLES_FOLDER = "articles"         # 不用改
RSS_FILE_PATH = "my-rss.xml"         # 不用改
# -------------------------------------------------------------

# 格式化XML（让生成的XML更易读）
def prettify_xml(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")

# 从md文件名/内容提取信息
def get_article_info(md_file_path):
    # 1. 提取文件名中的日期和标题（比如：20251217_文章1.md → 日期2025-12-17，标题文章1）
    file_name = os.path.basename(md_file_path)
    date_str = re.findall(r"(\d{8})", file_name)
    title = re.sub(r"\d{8}_|\.md", "", file_name)
    
    # 2. 读取md文件内容
    with open(md_file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    
    # 3. 生成发布时间（RFC822格式，Obsidian RSS插件识别）
    if date_str:
        date = datetime.strptime(date_str[0], "%Y%m%d")
        pub_date = date.strftime("%a, %d %b %Y 12:00:00 GMT")  # 固定时间12点，可改
    else:
        pub_date = datetime.now().strftime("%a, %d %b %Y 12:00:00 GMT")
    
    # 4. 生成文章的Raw地址（供Obsidian点击访问）
    raw_url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/main/{ARTICLES_FOLDER}/{file_name}"
    
    # 5. 生成摘要（取前200字，可改）
    summary = content[:200] + "..." if len(content) > 200 else content
    
    return {
        "title": title,
        "content": content,
        "summary": summary,
        "pub_date": pub_date,
        "raw_url": raw_url,
        "guid": raw_url  # 用Raw地址做唯一标识，避免重复抓取
    }

# 主函数：生成RSS文件
def generate_rss():
    # 1. 读取现有RSS模板
    tree = ET.parse(RSS_FILE_PATH)
    root = tree.getroot()
    channel = root.find("channel")
    
    # 清空现有<item>（避免重复）
    for item in channel.findall("item"):
        channel.remove(item)
    
    # 2. 遍历articles文件夹下的所有md文件
    md_files = [f for f in os.listdir(ARTICLES_FOLDER) if f.endswith(".md")]
    md_files.sort(reverse=True)  # 按文件名倒序（新文章在前）
    
    for md_file in md_files:
        md_path = os.path.join(ARTICLES_FOLDER, md_file)
        info = get_article_info(md_path)
        
        # 3. 生成<item>节点
        item = ET.SubElement(channel, "item")
        
        title_elem = ET.SubElement(item, "title")
        title_elem.text = info["title"]
        
        link_elem = ET.SubElement(item, "link")
        link_elem.text = info["raw_url"]
        
        description_elem = ET.SubElement(item, "description")
        # 用CDATA包裹内容，避免XML解析错误
        description_elem.text = ET.CDATA(f"""
            <p>摘要：{info["summary"]}</p>
            <p>完整内容：<a href="{info["raw_url"]}">点击查看</a></p>
            <hr>
            <pre>{info["content"]}</pre>
        """)
        
        pubdate_elem = ET.SubElement(item, "pubDate")
        pubdate_elem.text = info["pub_date"]
        
        guid_elem = ET.SubElement(item, "guid")
        guid_elem.text = info["guid"]
    
    # 4. 保存格式化后的XML
    with open(RSS_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(prettify_xml(root))
    
    print(f"✅ RSS生成成功！共处理 {len(md_files)} 篇文章")

if __name__ == "__main__":
    # 检查articles文件夹是否存在
    if not os.path.exists(ARTICLES_FOLDER):
        os.makedirs(ARTICLES_FOLDER)
        print(f"📁 已创建{ARTICLES_FOLDER}文件夹，请先放入md文章")
    else:
        generate_rss()
