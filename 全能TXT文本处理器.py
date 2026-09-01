# -*- coding: utf-8 -*-
"""
全能TXT文本处理器 2.1

以 1.0 版为基底优化，并整合旧版（txtchanger6.0 / txtuser）的实用功能。

2.0 修复/新增：
  1. 修复 "ansi" 编码名不合法导致读写报错的问题（映射为系统默认编码）
  2. 修复编辑框手动修改不同步的问题：单文件视图下编辑会自动同步回内存缓存
  3. 保存到原文件：按每个文件实际读取编码写回，并自动生成一次 .bak 备份
  4. 新增 查找替换 标签页（修复旧版查找定位错乱的缺陷），支持正则/全字匹配/
     批量替换所有文件
  5. 新增 文件上移/下移（调整合并顺序）、批量命名、合并文件
  6. 新增 真正的章节分割：按"第X章"拆分为独立文件
  7. 新增 去重行、大小写转换、添加前缀/后缀
  8. 未安装 tkinterdnd2 时自动降级为无拖放模式

2.1 新增：
  9. 批量操作改为后台线程执行（队列+轮询更新UI），大文件/多文件不再卡死界面
 10. 新增文本处理：段首缩进/去除缩进、全角字母数字转半角、中文间标点统一、
     去除HTML标签
 11. 新增内容提取：邮箱 / URL / 手机号（结果窗口支持复制、另存）
 12. 拖放支持文件夹（自动展开其中的 .txt 文件）
 13. 快捷键：Ctrl+S 保存到原文件，Ctrl+Shift+S 另存为，Ctrl+F 跳到查找页
 14. 记住编码选择与窗口大小（processor_settings.json）

2.2 新增：
 15. 界面升级：扁平化浅色主题、卡片式分组、主色操作按钮、悬停反馈、
     编辑区右键菜单（撤销/重做/剪贴板/全选）、任务执行时自动禁用相关按钮、
     文件列表计数、状态栏显示文件编码与大小、窗口顶部标题栏与忙碌指示

2.3 新增：
 16. 章节分割升级：内置多种章节标题规则（第X章/卷/回/节/集/篇、序章楔子番外、Chapter X），
     支持自定义正则；分割前可预览章节列表与字数，分割后自动生成"章节索引.txt"
 17. 新增小说清洗：广告词过滤（关键词列表可保存/从文件导入，删除含关键词的行）、
     章节去重（内容完全相同或同标题正文高度相似的章节自动剔除，保留靠前章节）
 18. 新增排版整理：压缩连续空行、清理行首尾空白
 19. 保存新增换行符选项（默认/LF/CRLF）；.bak 备份改为按字节复制，原样保留原始换行

2.4 新增：
 20. 新增 TXT→EPUB 导出：按章节规则自动分章，打包为 EPUB3 电子书（纯标准库实现，零依赖）
 21. 新增 章节重排：按标题编号（中文/阿拉伯数字）升序整理乱序章节，开头内容保持最前
 22. 查找替换新增"标记全部"：预览区一次性高亮所有匹配项

2.5 新增：
 23. EPUB 导出支持 封面图（jpg/png/gif）与 作者名（作者名随设置记忆）
 24. 新增 命令行模式（不启动界面），便于脚本化批量处理：
     split / epub / dedup / sort / adfilter / convert 子命令；
     不带参数运行仍是图形界面。示例：
     python 全能TXT文本处理器.py epub 小说.txt --out 小说.epub --author 某某 --cover cover.jpg
     python 全能TXT文本处理器.py dedup 小说.txt --in-place

2.6 新增：
 25. 新增「生成报告」：单文件 HTML 可视化统计报告（内嵌 CSS + SVG 图表，离线可用）——
     概览卡片（字数/章节/阅读时长/对话占比）、章节字数分布图、高频汉字 Top30（剔除虚词）、
     高频双字组合、标点使用统计；柱状图悬停可看数值
 26. EPUB 正文排版升级：衬线字体栈 + 两端对齐
 27. CLI 新增 stats 子命令：默认打印 JSON 统计概览（便于脚本/其他程序消费），--out 生成 HTML 报告

2.7 新增：
 28. 新增 十六进制查看：弹窗显示文件开头字节的 hex 转储，附"编码体检"（BOM/UTF-8 合法性/GBK 兜底），
     排查乱码根源；CLI 同步提供 hex 子命令
 29. 新增 比较文件：选中恰好两个文件生成彩色 HTML 差异报告（红删绿增）并用浏览器打开；
     CLI 提供 diff 子命令（--out 生成 HTML）

2.8 新增（工程补强）：
 30. 批量操作可撤销：每次批量修改前自动快照（上限 5 步），「撤销上一步」一键恢复内存内容
 31. 大文件流式转码：CLI convert 对超过 8MB 的文件走增量解码/编码，内存占用与文件大小无关
 32. 检查更新：标题栏按钮联网对比 GitHub latest release，发现新版可直达发布页；CLI version --check
 33. CI 加固：发布前强制跑单元测试（测试不过不发版），新增 push/PR 触发的 ci.yml

2.9 新增（作者向）：
 34. 新增 Word 导出：按章节规则分章打包为 .docx（OOXML 最小结构，纯标准库零依赖），
     书名/作者/章节标题分级排版，正文首行缩进；CLI docx 子命令
 35. 新增 EPUB→TXT 反向导入：解析 spine 顺序提取全文（CLI epub2txt 子命令），格式闭环
 36. 统计报告新增「章节节奏提示」：中位章字数基准线（分布图叠加黄色虚线）、
     最长/最短章、异常短章（低于中位 40%）与连续短章段（水更/断更嫌疑）
 37. 统计报告新增「人物出场曲线」：按章节统计指定人名出现次数的多折线图（GUI 报告时询问人名，
     CLI stats --names）

2.10 新增：
 38. 新增 敏感词检查：自定义词表（随设置记忆/可从文件导入），定位所有包含敏感词的行
     （大小写不敏感，只读分析不修改内容），结果弹窗支持复制/另存；CLI sensitive 子命令

2.11 新增：
 39. 深色主题：标题栏右侧设置区主题下拉切换（浅色/深色，重启生效），全套控件配色适配
 40. 跨平台发布：CI 同步构建 Windows/Linux/macOS 三平台单文件程序，测试通过才发版
 41. Web 工作台：CLI serve 启动本地浏览器操作台（仅监听 127.0.0.1，零依赖 http.server）——
     本地打开/上传 TXT → 在线编辑 → 全部文本处理/小说清洗 → 下载/写回，
     并可在线导出 EPUB/DOCX/章节 ZIP/统计报告

所有处理仅修改内存，需手动"保存到原文件"或"另存为新文件"才会写盘。
运行依赖：tkinterdnd2（可选，pip install tkinterdnd2，用于拖放）
"""

import argparse
import codecs
import difflib
import html
import json
import math
import os
import posixpath
import queue
import re
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
import uuid
import webbrowser
import zipfile
from collections import Counter
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

# 默认窗口标题
_APP_VERSION = "2.11"
DEFAULT_TITLE = f"全能TXT文本处理器 {_APP_VERSION}"

# ------------------------------ 界面主题配色（可切换浅色/深色） ------------------------------
_THEMES = {
    "浅色": {"COLOR_BG": "#EEF1F5", "COLOR_CARD": "#FFFFFF", "COLOR_BORDER": "#D9DEE7",
            "COLOR_PRIMARY": "#2563EB", "COLOR_PRIMARY_D": "#1D4ED8", "COLOR_PRIMARY_L": "#DBEAFE",
            "COLOR_TEXT": "#1F2937", "COLOR_MUTED": "#6B7280", "COLOR_DISABLE": "#9CA3AF",
            "COLOR_HEADER_SUB": "#BFDBFE", "COLOR_TAB_BG": "#E2E7EF",
            "COLOR_BTN_PRESSED": "#E5E7EB", "COLOR_BTN_HOVER": "#F3F4F6",
            "COLOR_BTN_DISABLE_BG": "#F9FAFB",
            "COLOR_SCROLLBAR": "#CBD5E1", "COLOR_SCROLLBAR_HOVER": "#94A3B8"},
    "深色": {"COLOR_BG": "#0F172A", "COLOR_CARD": "#1E293B", "COLOR_BORDER": "#334155",
            "COLOR_PRIMARY": "#3B82F6", "COLOR_PRIMARY_D": "#2563EB", "COLOR_PRIMARY_L": "#1E3A8A",
            "COLOR_TEXT": "#E2E8F0", "COLOR_MUTED": "#94A3B8", "COLOR_DISABLE": "#64748B",
            "COLOR_HEADER_SUB": "#93C5FD", "COLOR_TAB_BG": "#172033",
            "COLOR_BTN_PRESSED": "#334155", "COLOR_BTN_HOVER": "#273449",
            "COLOR_BTN_DISABLE_BG": "#172033",
            "COLOR_SCROLLBAR": "#475569", "COLOR_SCROLLBAR_HOVER": "#64748B"},
}


def _apply_palette(name):
    """把主题色写入模块级 COLOR_* 常量。需在构建界面前调用；运行中切换需重启。"""
    palette = _THEMES.get(name) or _THEMES["浅色"]
    globals().update(palette)


# 默认色板（浅色）——启动时会按设置覆盖
COLOR_BG        = "#EEF1F5"   # 页面背景
COLOR_CARD      = "#FFFFFF"   # 卡片背景
COLOR_BORDER    = "#D9DEE7"   # 边框
COLOR_PRIMARY   = "#2563EB"   # 主色（标题栏/主按钮/选中）
COLOR_PRIMARY_D = "#1D4ED8"   # 主色（悬停加深）
COLOR_PRIMARY_L = "#DBEAFE"   # 主色浅（列表选中背景）
COLOR_TEXT      = "#1F2937"   # 主文字
COLOR_MUTED     = "#6B7280"   # 次要文字
COLOR_DISABLE   = "#9CA3AF"   # 禁用文字
COLOR_HEADER_SUB = "#BFDBFE"  # 标题栏副标题
COLOR_TAB_BG    = "#E2E7EF"   # 标签页未选中背景
COLOR_BTN_PRESSED = "#E5E7EB"
COLOR_BTN_HOVER   = "#F3F4F6"
COLOR_BTN_DISABLE_BG = "#F9FAFB"
COLOR_SCROLLBAR = "#CBD5E1"
COLOR_SCROLLBAR_HOVER = "#94A3B8"

# 全角字母/数字 -> 半角 转换表（不动中文标点，避免破坏中文文本）
_FULLWIDTH_TABLE = {}
for _code in range(0xFF10, 0xFF1A):   # ０-９
    _FULLWIDTH_TABLE[_code] = chr(_code - 0xFF10 + 0x30)
for _code in range(0xFF21, 0xFF3B):   # Ａ-Ｚ
    _FULLWIDTH_TABLE[_code] = chr(_code - 0xFF21 + 0x41)
for _code in range(0xFF41, 0xFF5B):   # ａ-ｚ
    _FULLWIDTH_TABLE[_code] = chr(_code - 0xFF41 + 0x61)
_FULLWIDTH_TABLE[0x3000] = " "        # 全角空格

# 内容提取正则
_EXTRACT_PATTERNS = {
    "邮箱地址": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "URL链接": r"(?:https?://|www\.)[^\s，。；、！？：\"'（）【】《》<>]+",
    "手机号": r"(?<!\d)1[3-9]\d{9}(?!\d)",
}

# 内置章节标题规则（名称 -> 正则；行首锚定避免正文提及"第X章"被误切，
# 切分时用 finditer 定位，不含捕获组）
_CHAPTER_PRESETS = {
    "第X章": r"(?:^|\n)\s*第[一二三四五六七八九十百千万\d]+章",
    "第X章/卷/回/节/集/篇": r"(?:^|\n)\s*第[一二三四五六七八九十百千万\d]+[章卷回节集篇]",
    "第X章+序章/楔子/番外": r"(?:^|\n)\s*(?:第[一二三四五六七八九十百千万\d]+[章卷回节集篇]|序章|楔子|引子|番外[一二三四五六七八九十\d]*)",
    "Chapter X（英文）": r"(?:^|\n)\s*(?:Chapter|CHAPTER)\s+\d+",
}


def split_chapters_by_pattern(content, pattern):
    """按章节标题正则切分文本（finditer 定位，兼容含/不含捕获组的任意正则）。
    标题取匹配所在的整行（如"第一章 起点"），正文从标题行之后开始。
    返回 [(标题或 None, 正文), ...]；标题为 None 表示第一章之前的开头内容。"""
    matches = list(pattern.finditer(content))
    if not matches:
        return [(None, content)]
    blocks = []
    if matches[0].start() > 0:
        blocks.append((None, content[:matches[0].start()]))
    for i, m in enumerate(matches):
        # 标题取匹配所在整行（含前导换行，如"第一章 起点"）；从匹配结束处找行尾，
        # 因为行首锚定的匹配从上一行的 \n 开始
        line_end = content.find("\n", m.end())
        if line_end == -1:
            line_end = len(content)
        title = content[m.start():line_end].strip()
        body_start = max(line_end + 1, m.end())
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        blocks.append((title, content[body_start:end]))
    return blocks


def normalize_chapter_title(title):
    """归一化章节标题：去空白与常见分隔符，用于同标题判断"""
    return re.sub(r"[\s：:．.。\-—_~～]+", "", title or "")


def dedup_chapter_blocks(blocks, similarity_threshold=0.9):
    """章节去重：正文完全相同直接剔除；标题相同且正文相似度达到阈值时剔除靠后的章节。
    返回 (去重后的 blocks, 被剔除标题列表)。"""
    kept = []
    removed = []
    seen_bodies = set()      # 归一化正文 -> 完全重复判定
    title_bodies = {}        # 归一化标题 -> 首次出现的归一化正文（用于同标题相似比较）
    for title, body in blocks:
        norm_body = re.sub(r"\s+", "", body)
        if title is None or not norm_body:
            kept.append((title, body))
            continue
        if norm_body in seen_bodies:
            removed.append(f"{title}（内容完全重复）")
            continue
        key = normalize_chapter_title(title)
        prev = title_bodies.get(key)
        if prev is not None:
            # 超长章节截断比较，避免 O(n) 全文比对耗时
            ratio = difflib.SequenceMatcher(None, prev[:20000], norm_body[:20000]).ratio()
            if ratio >= similarity_threshold:
                removed.append(f"{title}（同标题，正文相似度 {ratio:.0%}）")
                continue
        seen_bodies.add(norm_body)
        title_bodies[key] = norm_body
        kept.append((title, body))
    return kept, removed


def rebuild_text_from_blocks(blocks):
    """把章节块重新拼接为文本（章节间空行分隔，标题独立成行）"""
    return "\n\n".join(
        f"{t}\n\n{b.strip()}" if t is not None else b.strip()
        for t, b in blocks if b.strip())


def filter_ad_lines(text, keywords, whole_line=False):
    """删除包含任一关键词的行（whole_line=True 时仅删除整行恰好等于关键词的行）。
    返回 (新文本, 删除行数)。"""
    kws = [k for k in (keywords or []) if k]
    if not kws:
        return text, 0
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    removed = 0
    out = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped and (stripped in kws if whole_line else any(k in stripped for k in kws)):
            removed += 1
        else:
            out.append(line)
    return "\n".join(out), removed


def compress_blank_lines(text):
    """把连续空行（含纯空白行）压缩为一个空行，并去掉开头空行"""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    out = []
    blank = False
    for line in text.split("\n"):
        if line.strip():
            blank = False
            out.append(line)
        elif not blank:
            blank = True
            out.append("")
    while out and out[0] == "":
        out.pop(0)
    return "\n".join(out)


def strip_line_edges(text):
    """清理每行首尾的空白（半角/全角空格、制表符）"""
    return "\n".join(line.strip(" \t　") for line in text.split("\n"))


# ------------------------------ 章节排序 ------------------------------
_CN_DIGITS = {"零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
              "六": 6, "七": 7, "八": 8, "九": 9}
_CN_UNITS = {"十": 10, "百": 100, "千": 1000, "万": 10000}


def chinese_num_to_int(s):
    """中文数字（含'两'）或阿拉伯数字 -> int；解析失败返回 None"""
    s = (s or "").strip()
    if not s:
        return None
    if s.isdigit():
        return int(s)
    total, section, num = 0, 0, 0   # total=万位以上累计, section=万以内累计, num=当前位
    for ch in s:
        if ch in _CN_DIGITS:
            num = _CN_DIGITS[ch]
        elif ch == "两":
            num = 2
        elif ch in _CN_UNITS:
            unit = _CN_UNITS[ch]
            if unit == 10000:
                section = (section + num) * unit if (section + num) else unit
                total += section
                section, num = 0, 0
            else:
                section += (num or 1) * unit
                num = 0
        else:
            return None
    return total + section + num


def chapter_sort_key(title):
    """章节标题 -> 排序键：开头内容最前，有编号的按编号，无编号的（番外等）排最后"""
    if title is None:
        return (0, 0, "")
    m = re.search(r"第([零一二三四五六七八九十百千万两\d]+)[章卷回节集篇]", title)
    if m:
        n = chinese_num_to_int(m.group(1))
        if n is not None:
            return (1, n, title)
    # 仅当标题以数字开头（如 "12 xxx"）才按数字排序，避免"番外1"被当成第1章
    m = re.match(r"\d+", title.strip())
    if m:
        return (1, int(m.group()), title)
    return (2, 0, title)


def sort_chapter_blocks(blocks):
    """按章节编号升序稳定重排（开头内容保持在最前）"""
    return sorted(blocks, key=lambda tb: chapter_sort_key(tb[0]))


# ------------------------------ EPUB 导出 ------------------------------
def text_to_xhtml_paragraphs(text):
    """纯文本 -> XHTML 段落（每个非空行一个 <p>，内容做 HTML 转义）"""
    lines = [line.strip() for line in
             text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    return "".join(f"<p>{html.escape(line)}</p>" for line in lines if line)


def chapter_xhtml(title, body):
    """单个章节的 XHTML 页面"""
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<!DOCTYPE html>\n"
        '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh">\n<head>\n'
        f"<title>{html.escape(title)}</title>\n"
        '<link rel="stylesheet" type="text/css" href="style.css"/>\n'
        "</head>\n<body>\n"
        f"<h2>{html.escape(title)}</h2>\n"
        + text_to_xhtml_paragraphs(body)
        + "\n</body>\n</html>"
    )


_EPUB_CSS = (
    "body { margin: 5% 8%; line-height: 1.9; text-align: justify;\n"
    "  font-family: 'Noto Serif CJK SC', 'Source Han Serif SC', 'SimSun', serif; }\n"
    "h2 { text-align: center; margin: 1.6em 0 1.2em; font-size: 1.25em; }\n"
    "p { text-indent: 2em; margin: 0.35em 0; }\n"
)


_COVER_MEDIA_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                      ".png": "image/png", ".gif": "image/gif"}


def build_epub(epub_path, book_title, chapters, author="", cover=None, cover_ext=".jpg"):
    """把章节列表打包为 EPUB3 电子书。chapters: [(标题, 正文纯文本)]。
    author: 作者名（可空）；cover: 封面图片字节（可空），cover_ext 决定图片类型。零依赖。"""
    book_uuid = uuid.uuid4()
    modified = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    container_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
        "  <rootfiles>\n"
        '    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n'
        "  </rootfiles>\n"
        "</container>"
    )

    manifest_items, spine_items, nav_lis, ncx_points = [], [], [], []
    cover_media = _COVER_MEDIA_TYPES.get(cover_ext.lower())
    if cover and cover_media:
        cover_fname = "cover" + cover_ext.lower()
        manifest_items.append(
            f'<item id="cover-image" href="{cover_fname}" media-type="{cover_media}" '
            'properties="cover-image"/>')
        manifest_items.append(
            '<item id="cover-page" href="cover.xhtml" media-type="application/xhtml+xml"/>')
        # 封面页放在 spine 首位
        spine_items.append('<itemref idref="cover-page" linear="yes"/>')

    for i, (title, _body) in enumerate(chapters, 1):
        fname = f"chapter_{i:03d}.xhtml"
        esc_title = html.escape(title)
        manifest_items.append(
            f'<item id="ch{i}" href="{fname}" media-type="application/xhtml+xml"/>')
        spine_items.append(f'<itemref idref="ch{i}"/>')
        nav_lis.append(f"<li><a href=\"{fname}\">{esc_title}</a></li>")
        ncx_points.append(
            f'<navPoint id="np{i}" playOrder="{i}"><navLabel><text>{esc_title}</text></navLabel>'
            f'<content src="{fname}"/></navPoint>')

    creator_line = f"    <dc:creator>{html.escape(author)}</dc:creator>\n" if author else ""
    cover_image_meta = ('    <meta name="cover" content="cover-image"/>\n'
                        if cover and cover_media else "")

    content_opf = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">\n'
        '  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        f"    <dc:identifier id=\"bookid\">urn:uuid:{book_uuid}</dc:identifier>\n"
        f"    <dc:title>{html.escape(book_title)}</dc:title>\n"
        + creator_line +
        "    <dc:language>zh</dc:language>\n"
        f"    <meta property=\"dcterms:modified\">{modified}</meta>\n"
        + cover_image_meta +
        "  </metadata>\n"
        "  <manifest>\n"
        '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>\n'
        '    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>\n'
        '    <item id="css" href="style.css" media-type="text/css"/>\n'
        "    " + "\n    ".join(manifest_items) + "\n"
        "  </manifest>\n"
        '  <spine toc="ncx">\n'
        "    " + "\n    ".join(spine_items) + "\n"
        "  </spine>\n"
        "</package>"
    )

    nav_xhtml = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<!DOCTYPE html>\n"
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh">\n'
        "<head><title>目录</title></head>\n"
        '<body><nav epub:type="toc" id="toc"><h1>目录</h1><ol>\n'
        + "\n".join(nav_lis)
        + "\n</ol></nav></body>\n</html>"
    )

    toc_ncx = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\n'
        "<head>\n"
        f"  <meta name=\"dtb:uid\" content=\"urn:uuid:{book_uuid}\"/>\n"
        '  <meta name="dtb:depth" content="1"/>\n'
        "</head>\n"
        "<docTitle><text>" + html.escape(book_title) + "</text></docTitle>\n"
        '<navMap>\n' + "\n".join(ncx_points) + "\n</navMap>\n</ncx>"
    )

    with zipfile.ZipFile(epub_path, "w") as z:
        # mimetype 必须是首个条目且不压缩（EPUB 规范）
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip")
        z.writestr("META-INF/container.xml", container_xml, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", content_opf, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/style.css", _EPUB_CSS, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/nav.xhtml", nav_xhtml, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/toc.ncx", toc_ncx, zipfile.ZIP_DEFLATED)
        if cover and cover_media:
            cover_page = (
                '<?xml version="1.0" encoding="utf-8"?>\n'
                "<!DOCTYPE html>\n"
                '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh">\n'
                "<head><title>封面</title>"
                "<style>body{margin:0;padding:0;text-align:center}"
                "img{max-width:100%;height:auto}</style></head>\n"
                f'<body><img src="cover{cover_ext.lower()}" alt="cover"/></body>\n</html>'
            )
            z.writestr("OEBPS/cover.xhtml", cover_page, zipfile.ZIP_DEFLATED)
            z.writestr("OEBPS/cover" + cover_ext.lower(), cover)
        for i, (title, body) in enumerate(chapters, 1):
            z.writestr(f"OEBPS/chapter_{i:03d}.xhtml",
                       chapter_xhtml(title, body), zipfile.ZIP_DEFLATED)


# ------------------------------ DOCX 导出与 EPUB 导入 ------------------------------
def _docx_para(text, bold=False, center=False, indent=False, size=None):
    """单个 OOXML 段落。size 单位为半磅（w:sz），如 32 = 16pt。"""
    props = []
    if bold:
        props.append("<w:b/>")
    if size:
        props.append(f'<w:sz w:val="{size}"/>')
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    ppr_parts = []
    if center:
        ppr_parts.append('<w:jc w:val="center"/>')
    if indent:
        ppr_parts.append('<w:ind w:firstLine="480"/>')  # 首行缩进两个字符（24pt=480 缇）
    ppr = f"<w:pPr>{''.join(ppr_parts)}</w:pPr>" if ppr_parts else ""
    # XML 不允许的控制字符去除（保留制表符）
    clean = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return (f"<w:p>{ppr}<w:r>{rpr}<w:t xml:space=\"preserve\">"
            f"{html.escape(clean)}</w:t></w:r></w:p>")


def build_docx(docx_path, book_title, chapters, author=""):
    """把章节列表打包为 .docx（Word 2007+ OOXML）。chapters: [(标题, 正文纯文本)]。
    仅用标准库 zipfile 手写最小结构，零依赖。"""
    body_parts = [_docx_para(book_title, bold=True, center=True, size=44)]
    if author:
        body_parts.append(_docx_para(author, center=True, size=24))
    for title, text in chapters:
        body_parts.append(_docx_para(title, bold=True, size=30))
        for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
            if line.strip():
                body_parts.append(_docx_para(line.strip(), indent=True))
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>" + "".join(body_parts) + "<w:sectPr/></w:body></w:document>"
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/>'
        "</Relationships>"
    )
    with zipfile.ZipFile(docx_path, "w") as z:
        z.writestr("[Content_Types].xml", content_types, zipfile.ZIP_DEFLATED)
        z.writestr("_rels/.rels", rels, zipfile.ZIP_DEFLATED)
        z.writestr("word/document.xml", document_xml, zipfile.ZIP_DEFLATED)


def extract_text_from_epub(epub_path):
    """解析 EPUB 电子书，提取书名与章节文本。返回 (书名, [(标题或None, 纯文本)])。
    纯标准库实现，不依赖第三方解析器。"""
    with zipfile.ZipFile(epub_path) as z:
        container = z.read("META-INF/container.xml").decode("utf-8", errors="replace")
        opf_m = re.search(r'full-path="([^"]+)"', container)
        if not opf_m:
            raise ValueError("container.xml 中未找到 OPF 路径")
        opf_path = opf_m.group(1)
        opf = z.read(opf_path).decode("utf-8", errors="replace")
        title_m = re.search(r"<dc:title[^>]*>(.*?)</dc:title>", opf, re.S)
        title = html.unescape(title_m.group(1)).strip() if title_m else \
            os.path.splitext(os.path.basename(epub_path))[0]
        # manifest：id -> href（属性顺序不定，逐标签分别提取）
        items = {}
        for tag in re.findall(r"<item\b[^>]*>", opf):
            mid = re.search(r'\bid="([^"]+)"', tag)
            mhref = re.search(r'\bhref="([^"]+)"', tag)
            if mid and mhref:
                items[mid.group(1)] = mhref.group(1)
        opf_dir = posixpath.dirname(opf_path)
        chapters = []
        for idref in re.findall(r'<itemref\b[^>]*idref="([^"]+)"', opf):
            href = items.get(idref)
            if not href:
                continue
            full = posixpath.normpath(posixpath.join(opf_dir, href) if opf_dir else href)
            if full not in z.namelist():
                continue
            xhtml = z.read(full).decode("utf-8", errors="replace")
            body_m = re.search(r"<body[^>]*>(.*)</body>", xhtml, re.S | re.I)
            body = body_m.group(1) if body_m else xhtml
            head_m = re.search(r"<h[1-6][^>]*>(.*?)</h[1-6]>", body, re.S | re.I)
            chap_title = None
            if head_m:
                chap_title = re.sub(r"<[^>]+>", "", head_m.group(1)).strip() or None
                # 标题已单独提取，从正文里去掉，避免 chapters_to_txt 重复
                body = body[:head_m.start()] + body[head_m.end():]
            text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", body, flags=re.S | re.I)
            text = html.unescape(re.sub(r"<[^>]+>", "\n", text))
            lines = [line.strip() for line in text.splitlines()]
            text = "\n".join(line for line in lines if line)
            if text:
                chapters.append((chap_title, text))
        return title, chapters


def chapters_to_txt(chapters):
    """[(标题或None, 正文)] -> 单个 TXT 字符串（标题独立成行，章节间空行分隔）"""
    parts = []
    for title, text in chapters:
        text = text.strip()
        if not text:
            continue
        parts.append(f"{title}\n\n{text}" if title else text)
    return "\n\n".join(parts) + ("\n" if parts else "")


def system_ansi():
    """当前系统的 ANSI 编码名（Windows 为 mbcs）"""
    return "mbcs" if sys.platform.startswith("win") else "cp1252"


def display_to_codec(display):
    """界面编码显示名 -> 实际 Python 编码名（修复 ansi 不合法的问题）"""
    return system_ansi() if display == "ansi" else display


def read_text_smart(path, chosen_display):
    """按选定编码读取文件，失败时自动尝试常见备选编码。
    返回 (内容, 实际使用的编码名)，写回时按此编码保存以保持原样。"""
    chosen = display_to_codec(chosen_display)
    if chosen in ("utf-8", "utf-8-sig"):
        # utf-8-sig 可同时正确读取带/不带 BOM 的 UTF-8 文件
        candidates = ["utf-8-sig", "gbk", "utf-16", system_ansi()]
    else:
        candidates = [chosen, "utf-8-sig", "gbk", "utf-16", system_ansi()]
    # 去重，保持顺序
    seen = set()
    candidates = [c for c in candidates if not (c in seen or seen.add(c))]

    last_err = None
    for enc in candidates:
        try:
            with open(path, "r", encoding=enc) as f:
                content = f.read()
            # UTF-8 文件：根据是否有 BOM 决定记录的编码，写回时保持原样
            if enc in ("utf-8", "utf-8-sig"):
                with open(path, "rb") as bf:
                    has_bom = bf.read(3) == b"\xef\xbb\xbf"
                enc = "utf-8-sig" if has_bom else "utf-8"
            return content, enc
        except (UnicodeDecodeError, UnicodeError) as e:
            last_err = e
        except LookupError:
            continue  # 当前平台不支持的编码，尝试下一个
    raise last_err if last_err else OSError("无法识别文件编码")


# ------------------------------ 文本统计与可视化报告 ------------------------------
# 报告为单文件 HTML（内嵌 CSS + SVG 图表），纯标准库生成，离线可用
_CJK_STOPCHARS = set(
    "的了是我不他她在有和就都不人一这也要上说没有来着到去看好对过自吗里后大之中为个你什么地得着那还吧")
_DIALOGUE_QUOTES = "“”\"「『"


def compute_text_stats(text):
    """文本基础统计：字数、行数、对话行占比、预计阅读时长等"""
    lines = text.split("\n")
    nonempty = [line for line in lines if line.strip()]
    cjk_count = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    dialogue = sum(1 for line in nonempty if any(q in line for q in _DIALOGUE_QUOTES))
    return {
        "total_chars": len(text),
        "chars_no_space": len(re.sub(r"\s", "", text)),
        "cjk_chars": cjk_count,
        "lines": len(lines),
        "nonempty_lines": len(nonempty),
        "dialogue_lines": dialogue,
        "reading_minutes": max(1, round(cjk_count / 500)),
    }


def top_cjk_unigrams(text, top=30):
    """高频汉字 Top N（剔除常见虚词，让结果更有信息量）"""
    cnt = Counter(ch for ch in text
                  if "\u4e00" <= ch <= "\u9fff" and ch not in _CJK_STOPCHARS)
    return cnt.most_common(top)


def top_cjk_bigrams(text, top=15):
    """相邻汉字二元组合 Top N（粗粒度高频词，如人名/地名/口头禅）"""
    cnt = Counter()
    prev = ""
    for ch in text:
        if "\u4e00" <= ch <= "\u9fff":
            if prev:
                cnt[prev + ch] += 1
            prev = ch
        else:
            prev = ""
    return cnt.most_common(top)


def bucket_series(items, max_bars=100):
    """把 [(标签, 数值)] 聚合到最多 max_bars 个桶（取平均），供图表降采样。
    返回 [(新标签, 平均值)]。"""
    if len(items) <= max_bars:
        return list(items)
    bucket_size = math.ceil(len(items) / max_bars)
    out = []
    for start in range(0, len(items), bucket_size):
        group = items[start:start + bucket_size]
        label = (f"{start + 1}-{start + len(group)}" if len(group) > 1 else f"{start + 1}")
        out.append((label, round(sum(v for _, v in group) / len(group))))
    return out


def svg_vbars(items, width=880, height=260, color="#2563EB", median=None):
    """纵向柱状图 SVG（矩形内嵌 <title> 提供原生悬停提示，可叠加中位虚线）"""
    if not items:
        return ""
    n = len(items)
    pad_l, pad_b, pad_t = 10, 24, 16
    plot_w, plot_h = width - pad_l * 2, height - pad_b - pad_t
    vmax = max(v for _, v in items) or 1
    slot = plot_w / n
    bar_w = max(2, min(40, slot * 0.72))
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
             f'viewBox="0 0 {width} {height}" role="img">']
    step = max(1, math.ceil(n / 16))
    for i, (label, v) in enumerate(items):
        x = pad_l + i * slot + (slot - bar_w) / 2
        h = plot_h * v / vmax
        y = pad_t + plot_h - h
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" '
                     f'rx="2" fill="{color}" class="bar"><title>{html.escape(str(label))}：{v}</title></rect>')
        if i % step == 0:
            short = html.escape(str(label))[:8]
            parts.append(f'<text x="{x + bar_w / 2:.1f}" y="{height - 7}" font-size="10" '
                         f'text-anchor="middle" fill="#6B7280">{short}</text>')
    parts.append(f'<line x1="{pad_l}" y1="{pad_t + plot_h}" x2="{width - pad_l}" '
                 f'y2="{pad_t + plot_h}" stroke="#D9DEE7"/>')
    if median:
        y = pad_t + plot_h * (1 - min(1, median / vmax))
        parts.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{width - pad_l}" y2="{y:.1f}" '
                     f'stroke="#F59E0B" stroke-dasharray="6 4"/>')
        parts.append(f'<text x="{width - pad_l}" y="{y - 4:.1f}" font-size="10" text-anchor="end" '
                     f'fill="#F59E0B">中位 {median:,.0f}</text>')
    parts.append("</svg>")
    return "".join(parts)


_LINE_COLORS = ["#2563EB", "#DC2626", "#059669", "#D97706",
                "#7C3AED", "#DB2777", "#0891B2", "#65A30D"]


def svg_line_chart(series, width=880, height=300):
    """多折线图 SVG。series: [(名称, [逐章数值...])]；自动绘制图例与横轴刻度。"""
    series = [(name, list(vals)) for name, vals in series if vals]
    if not series:
        return ""
    n = max(len(vals) for _, vals in series)
    vmax = max((max(vals) for _, vals in series), default=0) or 1
    pad_l, pad_b, top = 10, 24, 40  # top：图例区高度
    plot_w, plot_h = width - pad_l * 2, height - pad_b - top
    slot = plot_w / max(1, n - 1)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
             f'viewBox="0 0 {width} {height}" role="img">']
    # 图例
    lx = pad_l
    for idx, (name, _) in enumerate(series):
        color = _LINE_COLORS[idx % len(_LINE_COLORS)]
        parts.append(f'<rect x="{lx}" y="6" width="12" height="12" rx="2" fill="{color}"/>')
        parts.append(f'<text x="{lx + 16}" y="16" font-size="12" fill="#1F2937">{html.escape(name)}</text>')
        lx += 26 + len(name) * 13
    # 折线与数据点（悬浮提示挂在数据点上）
    for idx, (name, vals) in enumerate(series):
        color = _LINE_COLORS[idx % len(_LINE_COLORS)]
        pts = []
        for i, v in enumerate(vals):
            x = pad_l + i * slot
            y = top + plot_h * (1 - v / vmax)
            pts.append(f"{x:.1f},{y:.1f}")
        parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" '
                     f'points="{" ".join(pts)}"/>')
        for i, v in enumerate(vals):
            x, y = pts[i].split(",")
            parts.append(f'<circle cx="{x}" cy="{y}" r="2.5" fill="{color}">'
                         f'<title>{html.escape(name)} · 第{i + 1}章：{v}</title></circle>')
    # 横轴
    axis_y = top + plot_h
    parts.append(f'<line x1="{pad_l}" y1="{axis_y}" x2="{width - pad_l}" '
                 f'y2="{axis_y}" stroke="#D9DEE7"/>')
    step = max(1, math.ceil(n / 12))
    for i in range(0, n, step):
        x = pad_l + i * slot
        parts.append(f'<text x="{x:.1f}" y="{height - 6}" font-size="10" '
                     f'text-anchor="middle" fill="#6B7280">{i + 1}</text>')
    parts.append("</svg>")
    return "".join(parts)


def count_name_per_chapter(chapter_blocks, names):
    """统计人名在每章正文中的出现次数。
    chapter_blocks: [(标题或None, 正文)]；返回 [(人名, [每章次数...])]"""
    bodies = [b for _, b in chapter_blocks if b.strip()]
    return [(name, [body.count(name) for body in bodies]) for name in names]


def svg_hbars(items, width=880, color="#2563EB"):
    """横向条形图 SVG（用于字频等标签较长的场景）"""
    if not items:
        return ""
    row_h = 26
    height = len(items) * row_h + 12
    label_w, val_w = 130, 70
    bar_x, bar_max = label_w + 10, width - label_w - 10 - val_w
    vmax = max(v for _, v in items) or 1
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
             f'viewBox="0 0 {width} {height}" role="img">']
    for i, (label, v) in enumerate(items):
        y = 8 + i * row_h
        bh = row_h - 9
        short = html.escape(str(label))[:6]
        bar_w = max(2, bar_max * v / vmax)
        parts.append(f'<text x="0" y="{y + bh * 0.85:.1f}" font-size="13" fill="#1F2937">{short}</text>')
        parts.append(f'<rect x="{bar_x}" y="{y}" width="{bar_w:.1f}" height="{bh}" rx="3" '
                     f'fill="{color}" class="bar"><title>{html.escape(str(label))}：{v} 次</title></rect>')
        parts.append(f'<text x="{bar_x + bar_w + 6:.1f}" y="{y + bh * 0.85:.1f}" font-size="12" '
                     f'fill="#6B7280">{v}</text>')
    parts.append("</svg>")
    return "".join(parts)


_REPORT_CSS = """
:root { --primary:#2563EB; --bg:#EEF1F5; --card:#FFFFFF; --border:#D9DEE7;
        --text:#1F2937; --muted:#6B7280; }
* { box-sizing: border-box; }
body { margin: 0; padding: 28px 20px 40px; background: var(--bg); color: var(--text);
       font-family: "Microsoft YaHei UI", "PingFang SC", "Noto Sans CJK SC", sans-serif; }
.wrap { max-width: 960px; margin: 0 auto; }
h1 { font-size: 22px; margin: 0 0 4px; }
.meta { color: var(--muted); font-size: 12px; margin-bottom: 20px; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
         gap: 12px; margin-bottom: 20px; }
.card { background: var(--card); border: 1px solid var(--border); border-radius: 10px;
        padding: 14px 16px; }
.card .num { font-size: 24px; font-weight: 700; color: var(--primary); }
.card .lab { font-size: 12px; color: var(--muted); margin-top: 2px; }
section { background: var(--card); border: 1px solid var(--border); border-radius: 10px;
          padding: 18px 20px; margin-bottom: 20px; }
section h2 { font-size: 15px; margin: 0 0 12px; color: var(--primary); }
section p.desc { font-size: 12px; color: var(--muted); margin: -6px 0 12px; }
svg { width: 100%; height: auto; display: block; }
.bar:hover { opacity: 0.75; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
td, th { padding: 7px 10px; border-bottom: 1px solid var(--border); text-align: left; }
th { color: var(--muted); font-weight: 500; }
footer { text-align: center; color: var(--muted); font-size: 12px; margin-top: 8px; }
"""


def build_text_report(text, book_title, pattern, names=None):
    """生成完整 HTML 统计报告字符串（pattern 用于识别章节；names 为可选追踪人名）"""
    stats = compute_text_stats(text)
    blocks = split_chapters_by_pattern(text, pattern)
    chapter_items = [(t, len(b.strip())) for t, b in blocks if t is not None]
    shown = bucket_series(chapter_items)
    unigrams = top_cjk_unigrams(text, 30)
    bigrams = top_cjk_bigrams(text, 15)

    # 章节节奏：中位数与异常短章（不足 6 章时不做节奏判断）
    median = None
    rhythm_html = ""
    if len(chapter_items) >= 6:
        svals = sorted(v for _, v in chapter_items)
        median = (svals[len(svals) // 2] + svals[(len(svals) - 1) // 2]) / 2
        threshold = median * 0.4
        shorts = [(t, v) for t, v in chapter_items if v < threshold]
        runs, run = [], []
        for idx, (_, v) in enumerate(chapter_items):
            if v < threshold:
                run.append(idx + 1)
            elif len(run) >= 3:
                runs.append(run)
                run = []
        if len(run) >= 3:
            runs.append(run)
        longest = max(chapter_items, key=lambda tv: tv[1])
        shortest = min(chapter_items, key=lambda tv: tv[1])
        run_text = "、".join(
            f"第{r[0]}-{r[-1]}章（连续 {len(r)} 章）" if len(r) > 1 else f"第{r[0]}章"
            for r in runs) or "无"
        rhythm_rows = (
            f"<tr><td>中位章字数</td><td>{median:,.0f}</td></tr>"
            f"<tr><td>最长章</td><td>{html.escape(longest[0])}（{longest[1]:,} 字）</td></tr>"
            f"<tr><td>最短章</td><td>{html.escape(shortest[0])}（{shortest[1]:,} 字）</td></tr>"
            f"<tr><td>异常短章（低于中位 40%）</td><td>{len(shorts)} 章</td></tr>"
            f"<tr><td>连续短章嫌疑（疑似水更/断更）</td><td>{html.escape(run_text)}</td></tr>")
        rhythm_html = ('<section><h2>章节节奏提示</h2>'
                       '<p class="desc">以中位章字数为基准检测异常波动，供节奏自查参考</p>'
                       f"<table>{rhythm_rows}</table></section>")

    # 人物出场曲线
    names_html = ""
    if names:
        series = count_name_per_chapter(blocks, names)
        if any(sum(vals) for _, vals in series):
            names_html = ('<section><h2>人物出场曲线</h2>'
                          '<p class="desc">按章节统计人名出现次数（悬停数据点查看详情）</p>'
                          + svg_line_chart(series) + "</section>")

    def card(num, lab):
        return f'<div class="card"><div class="num">{num}</div><div class="lab">{lab}</div></div>'

    overview = "".join([
        card(f"{stats['chars_no_space']:,}", "总字数（不含空白）"),
        card(f"{stats['cjk_chars']:,}", "中文字符"),
        card(f"{stats['nonempty_lines']:,}", "非空行"),
        card(str(len(chapter_items)) or "—", "章节数"),
        card(f"{stats['reading_minutes']} 分钟", "预计阅读时长（500字/分）"),
        card(f"{stats['dialogue_lines'] / max(1, stats['nonempty_lines']):.0%}", "对话行占比"),
    ])

    puncts = {p: text.count(p) for p in "。，！？；：""''……——"}
    punct_rows = "".join(
        f"<tr><td>{html.escape(p)}</td><td>{n:,}</td></tr>"
        for p, n in sorted(puncts.items(), key=lambda kv: -kv[1])[:8])

    chapter_section = (
        '<section><h2>章节字数分布</h2>'
        + (f'<p class="desc">共 {len(chapter_items)} 章，每格为约 {math.ceil(len(chapter_items) / 100)} 章的平均字数</p>'
           if len(chapter_items) > 100 else
           (f'<p class="desc">共 {len(chapter_items)} 章</p>' if chapter_items else
            '<p class="desc">未识别到章节标题</p>'))
        + (svg_vbars(shown, median=median) if shown else "")
        + "</section>")

    uni_svg = svg_hbars(unigrams)
    bi_rows = "".join(
        f"<tr><td>{html.escape(w)}</td><td>{n:,}</td></tr>" for w, n in bigrams)

    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>{html.escape(book_title)} · 统计报告</title>
<style>{_REPORT_CSS}</style>
</head>
<body>
<div class="wrap">
  <h1>{html.escape(book_title)} · 文本统计报告</h1>
  <div class="meta">生成于 {time.strftime("%Y-%m-%d %H:%M")} · 共 {stats['total_chars']:,} 字符</div>
  <div class="cards">{overview}</div>
  {chapter_section}
  {names_html}
  {rhythm_html}
  <section><h2>高频汉字 Top {len(unigrams)}</h2>
    <p class="desc">已剔除"的了是在"等虚词，反映用字偏好</p>
    {uni_svg}</section>
  <section><h2>高频双字组合 Top {len(bigrams)}</h2>
    <p class="desc">相邻汉字组合，通常对应人名、地名、口头禅</p>
    <table><tr><th>组合</th><th>出现次数</th></tr>{bi_rows}</table></section>
  <section><h2>标点使用</h2>
    <table><tr><th>标点</th><th>次数</th></tr>{punct_rows}</table></section>
  <footer>全能TXT文本处理器 {_APP_VERSION} 本地生成 · 数据未离开本机</footer>
</div>
</body>
</html>"""


# ------------------------------ 十六进制查看与文件比较 ------------------------------
_HEX_VIEW_BYTES = 65536  # 十六进制查看默认最多显示的字节数


def hex_dump(data, width=16):
    """字节串 -> 十六进制转储文本（偏移量 | 十六进制 | ASCII，不可见字符显示为·）"""
    lines = []
    for off in range(0, len(data), width):
        chunk = data[off:off + width]
        hexpart = " ".join(f"{b:02X}" for b in chunk)
        asciipart = "".join(chr(b) if 32 <= b < 127 else "·" for b in chunk)
        lines.append(f"{off:08X}  {hexpart:<{width * 3 - 1}}  {asciipart}")
    return "\n".join(lines)


def detect_encoding_hints(data):
    """对文件头字节做编码体检，返回提示列表（帮助判断乱码根源）"""
    hints = []
    if data.startswith(b"\xef\xbb\xbf"):
        hints.append("带 UTF-8 BOM")
    elif data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        hints.append("带 UTF-16 BOM")
    try:
        data.decode("utf-8")
        hints.append("是合法 UTF-8")
    except UnicodeDecodeError:
        hints.append("不是合法 UTF-8（可能为 GBK/ANSI 或文件损坏）")
        try:
            data.decode("gbk")
            hints.append("可按 GBK 解码")
        except UnicodeDecodeError:
            hints.append("也无法按 GBK 解码")
    return hints


_DIFF_CSS = """
body { margin: 24px; background: #EEF1F5; color: #1F2937;
       font-family: Consolas, "Courier New", monospace; font-size: 13px; }
h1 { font-family: "Microsoft YaHei UI", sans-serif; font-size: 18px; }
.meta { font-family: "Microsoft YaHei UI", sans-serif; color: #6B7280;
        font-size: 12px; margin-bottom: 16px; }
.card { background: #FFFFFF; border: 1px solid #D9DEE7; border-radius: 10px;
        padding: 12px 0; overflow-x: auto; }
div.line { padding: 1px 14px; white-space: pre; }
.add { background: #E6F4EA; color: #1A7F37; }
.del { background: #FDE8E8; color: #C0392B; }
.info { background: #DBEAFE; color: #1D4ED8; font-weight: bold; }
footer { font-family: "Microsoft YaHei UI", sans-serif; text-align: center;
         color: #6B7280; font-size: 12px; margin-top: 12px; }
"""


def unified_diff_html(title_a, title_b, a_text, b_text, context=3):
    """两段文本的行级差异 -> 彩色 HTML 报告（删除行红底、新增行绿底）"""
    diff_lines = list(difflib.unified_diff(
        a_text.splitlines(), b_text.splitlines(),
        fromfile=title_a, tofile=title_b, lineterm="", n=context))
    rows = []
    changed = added = removed = 0
    for line in diff_lines:
        if line.startswith("---") or line.startswith("+++"):
            continue
        esc = html.escape(line)
        if line.startswith("@@"):
            rows.append(f'<div class="line info">{esc}</div>')
        elif line.startswith("-"):
            removed += 1
            rows.append(f'<div class="line del">{esc}</div>')
        elif line.startswith("+"):
            added += 1
            rows.append(f'<div class="line add">{esc}</div>')
        else:
            rows.append(f'<div class="line">{esc or " "}</div>')
    changed = added + removed
    meta = (f"{html.escape(title_a)} vs {html.escape(title_b)} · "
            f"+{added} 行 / -{removed} 行（共 {changed} 处变动）")
    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>文件对比：{html.escape(title_a)} vs {html.escape(title_b)}</title>
<style>{_DIFF_CSS}</style>
</head>
<body>
<h1>文件对比报告</h1>
<div class="meta">{meta}</div>
<div class="card">{"".join(rows) or '<div class="line">两个文件内容完全一致</div>'}</div>
<footer>全能TXT文本处理器 2.7 本地生成 · 数据未离开本机</footer>
</body>
</html>"""


# ------------------------------ 工程补强：撤销 / 更新检查 / 流式转码 ------------------------------
_UNDO_LIMIT = 5                    # 撤销栈上限（步）
_STREAM_THRESHOLD = 8 * 1024 * 1024  # 超过该字节数的文件转码走流式（8MB）


def push_undo_snapshot(stack, label, contents, keys, limit=_UNDO_LIMIT):
    """把 keys 指定文件的当前内容快照压入撤销栈（超出上限丢弃最旧的）。
    返回是否成功入栈。"""
    snapshot = {k: contents[k] for k in keys if k in contents}
    if not snapshot:
        return False
    stack.append({"label": label, "snapshot": snapshot})
    while len(stack) > limit:
        stack.pop(0)
    return True


def version_tuple(tag):
    """"v2.10" -> (2, 10)，用于版本号大小比较"""
    return tuple(int(x) for x in re.findall(r"\d+", str(tag))[:3]) or (0,)


_UPDATE_API = "https://api.github.com/repos/Croesus-K/paper-worker/releases/latest"


def check_update_from_github(timeout=8):
    """查询 GitHub latest release。返回 (tag_name, html_url)；网络失败抛异常。"""
    request = urllib.request.Request(
        _UPDATE_API,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "paper-worker"})
    with urllib.request.urlopen(request, timeout=timeout) as resp:
        data = json.load(resp)
    return data.get("tag_name", ""), data.get("html_url", "")


def _detect_source_encoding(path):
    """从文件头（最多 1MB）探测源编码：BOM 优先，其次 UTF-8 合法性、GBK 兜底"""
    with open(path, "rb") as f:
        head = f.read(1024 * 1024)
    if head.startswith(codecs.BOM_UTF8):
        return "utf-8-sig"
    if head.startswith(codecs.BOM_UTF16_LE) or head.startswith(codecs.BOM_UTF16_BE):
        return "utf-16"
    try:
        head.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        pass
    try:
        head.decode("gbk")
        return "gbk"
    except UnicodeDecodeError:
        return system_ansi()


def convert_file_stream(src, dst, target_encoding, chunk_size=1024 * 1024):
    """流式转码大文件：先探测源编码，再增量解码/编码写入，内存占用与文件大小无关。
    返回 (源编码, 是否出现无法解码字节)。探测仅基于头部 1MB，中段混入其他编码的
    字节会以 U+FFFD 替换并在返回值中提示。"""
    src_enc = _detect_source_encoding(src)
    replaced = False
    decoder = codecs.getincrementaldecoder(src_enc)(errors="replace")
    encoder = codecs.getincrementalencoder(target_encoding)()
    with open(src, "rb") as fin, open(dst, "wb") as fout:
        while True:
            chunk = fin.read(chunk_size)
            if not chunk:
                break
            text = decoder.decode(chunk)
            if "\ufffd" in text:
                replaced = True
            fout.write(encoder.encode(text))
        tail = decoder.decode(b"", True)  # 冲刷多字节残留（可疑尾字节在此阶段才产出）
        if "\ufffd" in tail:
            replaced = True
        fout.write(encoder.encode(tail))
    return src_enc, replaced


# ------------------------------ 敏感词检查 ------------------------------
def find_sensitive_hits(text, keywords):
    """敏感词定位（大小写不敏感的包含匹配，只读不改内容）。
    返回 [(行号(1基), 关键词, 该行内容)]，按行号排序；同行多次命中分别计入。"""
    hits = []
    for kw in dict.fromkeys(k for k in keywords if k):
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        for m in pattern.finditer(text):
            line_start = text.rfind("\n", 0, m.start()) + 1
            line_end = text.find("\n", m.end())
            if line_end == -1:
                line_end = len(text)
            hits.append((text.count("\n", 0, m.start()) + 1, kw,
                         text[line_start:line_end].strip()))
    hits.sort(key=lambda h: h[0])
    return hits


def summarize_sensitive_hits(hits, keywords):
    """按关键词聚合命中：返回 [(关键词, 出现次数, [去重行号...])]，保持词表原顺序。"""
    order = {kw: i for i, kw in enumerate(dict.fromkeys(k for k in keywords if k))}
    agg = {kw: {"count": 0, "lines": []} for kw in order}
    for lineno, kw, _line in hits:
        if kw in agg:
            agg[kw]["count"] += 1
            if lineno not in agg[kw]["lines"]:
                agg[kw]["lines"].append(lineno)
    return [(kw, info["count"], info["lines"])
            for kw, info in sorted(agg.items(), key=lambda kv: order[kv[0]])]


def format_sensitive_report(results, keywords):
    """results: [(文件名, [(关键词, 次数, [行号...])])] -> 文本报告（GUI 弹窗与 CLI 共用）"""
    n_keywords = len({k for k in keywords if k})
    lines = [f"敏感词检查报告 · {time.strftime('%Y-%m-%d %H:%M')}", ""]
    grand_total = 0
    for fname, agg in results:
        hit_items = [(kw, cnt, linenos) for kw, cnt, linenos in agg if cnt]
        file_total = sum(cnt for _, cnt, _ in hit_items)
        grand_total += file_total
        lines.append(f"═══ {fname} ═══")
        if not hit_items:
            lines.append("未命中任何敏感词")
        else:
            lines.append(f"命中 {len(hit_items)}/{n_keywords} 个词，共 {file_total} 处")
            for kw, cnt, linenos in hit_items:
                shown = "、".join(str(n) for n in linenos[:20]) + ("…" if len(linenos) > 20 else "")
                lines.append(f"  【{kw}】{cnt} 处 —— 第 {shown} 行")
            missed = [kw for kw, cnt, _ in agg if not cnt]
            if missed:
                lines.append(f"  未命中：{'、'.join(missed)}")
        lines.append("")
    lines.append(f"合计：{grand_total} 处命中")
    return "\n".join(lines)


class TextProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(DEFAULT_TITLE)
        self.root.geometry("1240x860")
        self.root.resizable(True, True)

        # 主题需在构建界面前确定（运行中切换主题需重启生效）
        theme_name = "浅色"
        try:
            with open(self._settings_path, "r", encoding="utf-8") as f:
                saved = json.load(f).get("theme")
            if saved in _THEMES:
                theme_name = saved
        except Exception:
            pass
        _apply_palette(theme_name)
        self.theme_var = tk.StringVar(value=theme_name)

        # 高DPI适配
        self.enable_high_dpi()

        # 字体配置
        self.font_config()

        # 应用扁平化主题
        self.setup_theme()

        # 数据存储
        self.file_list = []            # 已加载的文件路径列表
        self.file_contents = {}        # 文件内容缓存 {文件路径: 内容}
        self.file_encodings = {}       # 每个文件实际读取时使用的编码 {文件路径: 编码名}
        self.current_view_files = []   # 当前编辑区显示的文件（单文件时编辑会同步回缓存）
        self.current_encoding = "utf-8"  # 默认编码（界面显示名）
        self._sync_job = None          # 编辑同步的定时任务
        self.last_find_pos = 0         # 查找位置（字符偏移量）
        self.ad_filter_words = []      # 广告过滤关键词列表（持久化）
        self.ad_whole_line = False     # 广告过滤：整行完全匹配才删除
        self.epub_author = ""          # EPUB 导出作者名（持久化）
        self.newline_var = tk.StringVar(value="默认")  # 保存时的换行符模式
        self._undo_stack = []          # 批量操作撤销栈（仅内存内容，不影响磁盘）
        self.sensitive_words = []      # 敏感词检查词表（持久化）
        self._task_done_callback = None  # 任务完成后的附加回调（如打开结果窗口）

        # 界面控件注册
        self.task_buttons = []         # 任务执行期间需要禁用的按钮

        # 后台任务框架
        self._busy = False
        self.task_queue = queue.Queue()
        self._task_thread = None
        self._task_errors = []
        self._task_done_msg = ""
        self._task_done_title = "完成"
        self._task_was_empty = False

        # 界面构建
        self.create_widgets()

        # 应用保存的设置（编码、窗口大小）
        self.apply_settings()

        # 启用拖放功能
        self.enable_drag_and_drop()

        # 关闭窗口时保存设置
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _push_undo(self, label, target_files):
        """批量修改前调用：快照受影响文件的内存内容（主线程调用）"""
        return push_undo_snapshot(self._undo_stack, label, self.file_contents, target_files)

    def undo_last_batch(self):
        """撤销上一次批量操作（恢复内存内容，不改动磁盘文件）"""
        if self._busy_guard():
            return
        if not self._undo_stack:
            messagebox.showinfo("提示", "没有可撤销的批量操作")
            return
        entry = self._undo_stack[-1]
        n = len(entry["snapshot"])
        if not messagebox.askyesno(
                "确认撤销",
                f"撤销「{entry['label']}」？\n将恢复 {n} 个文件的内存内容（磁盘文件不受影响）。"):
            return
        self._undo_stack.pop()
        self.file_contents.update(entry["snapshot"])
        self.show_selected_file_content()
        left = f"（还可撤销 {len(self._undo_stack)} 步）" if self._undo_stack else "（已到最早一步）"
        self.status_var.set(f"已撤销「{entry['label']}」{left}")

    # ------------------------------ 环境适配 ------------------------------
    def enable_high_dpi(self):
        """高DPI显示适配"""
        if sys.platform.startswith('win'):
            try:
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
                self.root.tk.call('tk', 'scaling', 1.5)
            except Exception as e:
                print(f"高DPI适配失败：{e}")
        elif sys.platform.startswith('darwin'):
            self.root.tk.call('tk', 'scaling', 2.0)
        else:
            self.root.tk.call('tk', 'scaling', 1.2)

    def font_config(self):
        """统一字体配置"""
        system_fonts = ['Microsoft YaHei UI', 'Heiti TC', 'WenQuanYi Micro Hei', 'SimHei', 'Arial', 'sans-serif']
        font_face = "SimHei"  # 默认字体
        for font in system_fonts:
            if font in self.root.call("font", "families"):
                font_face = font
                break
        self.text_font = (font_face, 11)
        self.listbox_font = (font_face, 10)
        self.status_font = (font_face, 9)
        self.root.option_add("*Font", self.text_font)

    def setup_theme(self):
        """应用扁平化浅色主题（基于 clam，逐项配置并安全降级）"""
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        face = self.text_font[0]
        small = (face, 10)

        def cfg(name, **kw):
            try:
                style.configure(name, **kw)
            except tk.TclError:
                pass

        def mp(name, **kw):
            try:
                style.map(name, **kw)
            except tk.TclError:
                pass

        self.root.configure(bg=COLOR_BG)

        # 通用默认
        cfg(".", background=COLOR_CARD, foreground=COLOR_TEXT, bordercolor=COLOR_BORDER,
            lightcolor=COLOR_CARD, darkcolor=COLOR_CARD, troughcolor=COLOR_CARD,
            fieldbackground=COLOR_CARD, selectbackground=COLOR_PRIMARY_L,
            selectforeground=COLOR_TEXT, font=small)

        # 页面容器（浅灰背景）
        style.configure("Page.TFrame", background=COLOR_BG)

        # 分组卡片（白底 + 描边 + 主色标题）
        cfg("Card.TLabelframe", background=COLOR_CARD, bordercolor=COLOR_BORDER,
            relief="solid", borderwidth=1)
        cfg("Card.TLabelframe.Label", background=COLOR_CARD, foreground=COLOR_PRIMARY,
            font=(face, 10, "bold"))

        # 按钮
        cfg("TButton", background=COLOR_CARD, foreground=COLOR_TEXT, bordercolor=COLOR_BORDER,
            focuscolor=COLOR_PRIMARY, padding=(8, 4), relief="flat")
        mp("TButton",
           background=[("pressed", COLOR_BTN_PRESSED), ("active", COLOR_BTN_HOVER),
                       ("disabled", COLOR_BTN_DISABLE_BG)],
           foreground=[("disabled", COLOR_DISABLE)],
           bordercolor=[("active", COLOR_PRIMARY)])

        # 主操作按钮（实心主色）
        cfg("Primary.TButton", background=COLOR_PRIMARY, foreground="#FFFFFF",
            bordercolor=COLOR_PRIMARY)
        mp("Primary.TButton",
           background=[("pressed", COLOR_PRIMARY_D), ("active", COLOR_PRIMARY_D),
                       ("disabled", "#93C5FD")],
           foreground=[("disabled", "#EFF6FF")],
           bordercolor=[("active", COLOR_PRIMARY_D)])

        # 标签 / 复选框
        cfg("TLabel", background=COLOR_CARD, foreground=COLOR_TEXT)
        cfg("Muted.TLabel", background=COLOR_CARD, foreground=COLOR_MUTED, font=(face, 9))
        cfg("TCheckbutton", background=COLOR_CARD, foreground=COLOR_TEXT, focuscolor=COLOR_PRIMARY)
        mp("TCheckbutton", background=[("active", COLOR_CARD)],
           foreground=[("disabled", COLOR_DISABLE)])

        # 输入框 / 下拉框
        cfg("TEntry", padding=5, bordercolor=COLOR_BORDER, lightcolor=COLOR_BORDER,
            insertcolor=COLOR_TEXT)
        mp("TEntry", bordercolor=[("focus", COLOR_PRIMARY)],
           lightcolor=[("focus", COLOR_PRIMARY)])
        cfg("TCombobox", padding=4, bordercolor=COLOR_BORDER, lightcolor=COLOR_BORDER,
            arrowcolor=COLOR_TEXT, fieldbackground=COLOR_CARD, background=COLOR_CARD,
            arrowsize=13)
        mp("TCombobox", bordercolor=[("focus", COLOR_PRIMARY)],
           fieldbackground=[("readonly", COLOR_CARD)],
           arrowcolor=[("active", COLOR_PRIMARY)])

        # 进度条 / 滚动条 / 分隔线
        cfg("Horizontal.TProgressbar", background=COLOR_PRIMARY, troughcolor=COLOR_BORDER,
            bordercolor=COLOR_CARD, lightcolor=COLOR_PRIMARY, darkcolor=COLOR_PRIMARY)
        cfg("TScrollbar", background=COLOR_SCROLLBAR, troughcolor=COLOR_CARD,
            bordercolor=COLOR_CARD, arrowcolor=COLOR_MUTED, relief="flat")
        mp("TScrollbar", background=[("active", COLOR_SCROLLBAR_HOVER)])
        cfg("TSeparator", background=COLOR_BORDER)

        # 标签页
        cfg("TNotebook", background=COLOR_BG, bordercolor=COLOR_BORDER, tabmargins=(6, 6, 6, 0))
        cfg("TNotebook.Tab", padding=(18, 7), background=COLOR_TAB_BG, foreground=COLOR_MUTED,
            font=(face, 10, "bold"))
        mp("TNotebook.Tab", background=[("selected", COLOR_CARD)],
           foreground=[("selected", COLOR_PRIMARY)])

    def _style_input_widget(self, widget, font=None):
        """统一 tk 输入控件（Text/Listbox）的扁平外观：白底、描边、聚焦主色。
        不同控件的选项集合不同，逐项配置并容错。"""
        options = {
            "bg": COLOR_CARD,
            "fg": COLOR_TEXT,
            "relief": "flat",
            "selectbackground": COLOR_PRIMARY_L,
            "selectforeground": COLOR_TEXT,
            "highlightthickness": 1,
            "highlightbackground": COLOR_BORDER,
            "highlightcolor": COLOR_PRIMARY,
            "insertbackground": COLOR_TEXT,
            "padx": 6,
            "pady": 4,
        }
        for key, value in options.items():
            try:
                widget.configure(**{key: value})
            except tk.TclError:
                pass  # 控件不支持该选项（如 Listbox 无 padx/insertbackground）
        if font:
            widget.configure(font=font)

    def _action_button(self, parent, text, command, style="TButton", side=tk.LEFT):
        """创建任务按钮：注册到 task_buttons，后台任务执行期间自动禁用"""
        btn = ttk.Button(parent, text=text, command=command, style=style)
        btn.pack(side=side, padx=3, pady=2)
        self.task_buttons.append(btn)
        return btn

    def _update_list_count(self):
        """刷新文件列表标题中的计数"""
        if hasattr(self, "list_group"):
            self.list_group.configure(text=f"已加载文件列表（{len(self.file_list)}）")

    @staticmethod
    def _system_ansi():
        return system_ansi()

    @classmethod
    def _display_to_codec(cls, display):
        return display_to_codec(display)

    def _read_text(self, path, chosen_display):
        return read_text_smart(path, chosen_display)

    # ------------------------------ 设置持久化 ------------------------------
    @property
    def _settings_path(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "processor_settings.json")

    def apply_settings(self):
        """启动时应用保存的设置（编码、窗口大小）"""
        settings = {}
        try:
            with open(self._settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except Exception:
            return
        enc = settings.get("encoding")
        if enc in ("utf-8", "gbk", "gb2312", "utf-16", "ansi"):
            self.encode_var.set(enc)
            self.current_encoding = enc
        geometry = settings.get("geometry")
        if geometry:
            try:
                self.root.geometry(geometry)
            except Exception:
                pass
        newline_mode = settings.get("newline_mode")
        if newline_mode in ("默认", "LF (Unix)", "CRLF (Windows)"):
            self.newline_var.set(newline_mode)
        theme = settings.get("theme")
        if theme in _THEMES:
            self.theme_var.set(theme)
        words = settings.get("ad_filter_words")
        if isinstance(words, list):
            self.ad_filter_words = [str(w) for w in words if str(w).strip()]
        self.ad_whole_line = bool(settings.get("ad_whole_line", False))
        self.epub_author = str(settings.get("epub_author", ""))
        words = settings.get("sensitive_words")
        if isinstance(words, list):
            self.sensitive_words = [str(w) for w in words if str(w).strip()]

    def save_settings(self):
        """保存设置（编码、窗口大小、换行符、广告过滤词、EPUB 作者名、敏感词表）"""
        try:
            with open(self._settings_path, "w", encoding="utf-8") as f:
                json.dump({
                    "encoding": self.encode_var.get(),
                    "geometry": self.root.geometry(),
                    "newline_mode": self.newline_var.get(),
                    "theme": self.theme_var.get(),
                    "ad_filter_words": self.ad_filter_words,
                    "ad_whole_line": self.ad_whole_line,
                    "epub_author": self.epub_author,
                    "sensitive_words": self.sensitive_words,
                }, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _on_close(self):
        """关闭窗口：任务处理中需确认；保存设置"""
        if self._busy and not messagebox.askyesno(
                "确认", "任务仍在后台处理中，退出可能中断文件写入，确定退出吗？"):
            return
        self.save_settings()
        self.root.destroy()

    # ------------------------------ 界面构建 ------------------------------
    def create_widgets(self):
        """构建完整界面"""
        face = self.text_font[0]

        # 顶部标题栏（主色横幅）
        header = tk.Frame(self.root, bg=COLOR_PRIMARY)
        header.pack(side=tk.TOP, fill=tk.X)
        header_inner = tk.Frame(header, bg=COLOR_PRIMARY)
        header_inner.pack(fill=tk.X, padx=14, pady=8)
        tk.Label(header_inner, text="全能TXT文本处理器", bg=COLOR_PRIMARY, fg="#FFFFFF",
                 font=(face, 15, "bold")).pack(side=tk.LEFT)
        tk.Label(header_inner, text=f"v{_APP_VERSION} · 仅修改内存 · 手动保存", bg=COLOR_PRIMARY,
                 fg=COLOR_HEADER_SUB, font=(face, 9)).pack(side=tk.LEFT, padx=(10, 0), pady=(4, 0))
        # 检查更新（标题栏右侧扁平小按钮）
        tk.Button(header_inner, text="检查更新", command=self.check_update,
                  bg=COLOR_PRIMARY, fg="#FFFFFF", relief="flat", bd=0,
                  activebackground=COLOR_PRIMARY_D, activeforeground="#FFFFFF",
                  font=(face, 9), cursor="hand2").pack(side=tk.RIGHT, padx=(0, 12))
        self.busy_label = tk.Label(header_inner, text="", bg=COLOR_PRIMARY, fg="#FDE68A",
                                   font=(face, 10, "bold"))
        self.busy_label.pack(side=tk.RIGHT)

        # 标签页
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(expand=1, fill="both", padx=8, pady=8)

        process_tab = ttk.Frame(self.tab_control, style="Page.TFrame")
        self.tab_control.add(process_tab, text="文件处理")
        find_tab = ttk.Frame(self.tab_control, style="Page.TFrame")
        self.tab_control.add(find_tab, text="查找替换")

        self.build_process_tab(process_tab)
        self.build_find_replace_tab(find_tab)

        # 快捷键
        self.root.bind("<Control-s>", lambda e: self.save_to_original_files())
        self.root.bind("<Control-S>", lambda e: self.save_as_new_file())
        self.root.bind("<Control-f>", self._focus_find_tab)

        # 状态栏（上边线 + 扁平底栏）
        self.status_var = tk.StringVar(
            value="就绪 | 支持多选文件/拖放（支持文件夹） | 处理仅修改内存，需手动保存"
        )
        ttk.Separator(self.root, orient="horizontal").pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            bg=COLOR_CARD,
            fg=COLOR_MUTED,
            anchor=tk.W,
            font=self.status_font,
            padx=10,
            pady=4
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def _focus_find_tab(self, event=None):
        """Ctrl+F：跳到查找替换标签页并聚焦查找框"""
        self.tab_control.select(1)
        self.find_entry.focus_set()

    def check_update(self):
        """联网检查 GitHub latest release（后台线程，结果回主线程弹窗）"""
        self.status_var.set("正在检查更新…")

        def worker():
            try:
                tag, url = check_update_from_github()
                self.root.after(0, lambda: self._show_update_result(tag, url))
            except Exception as e:
                self.root.after(0, lambda: self._show_update_result(None, str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _show_update_result(self, tag, extra):
        """展示检查更新结果（主线程）"""
        if tag is None:
            self.status_var.set("检查更新失败")
            messagebox.showwarning("检查更新", f"无法连接 GitHub：{extra}\n请检查网络或代理设置。")
            return
        if version_tuple(tag) > version_tuple(_APP_VERSION):
            self.status_var.set(f"发现新版本 {tag}")
            if messagebox.askyesno("发现新版本",
                                   f"最新版本：{tag}\n当前版本：{_APP_VERSION}\n\n是否打开发布页下载？"):
                webbrowser.open(extra)
        else:
            self.status_var.set(f"已是最新版本（{_APP_VERSION}）")
            messagebox.showinfo("检查更新", f"已是最新版本（{_APP_VERSION}）")

    def build_process_tab(self, parent):
        """构建文件处理标签页"""
        main_frame = ttk.Frame(parent, style="Page.TFrame", padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ------------------------------ 左侧文件管理面板 ------------------------------
        left_frame = ttk.Frame(main_frame, style="Page.TFrame", width=360)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 6), pady=0)
        left_frame.pack_propagate(False)

        # 文件操作组
        file_ops_group = ttk.LabelFrame(left_frame, text="文件操作（支持多选/拖放）",
                                        style="Card.TLabelframe")
        file_ops_group.pack(fill=tk.X, pady=(0, 8))

        btn_frame1 = ttk.Frame(file_ops_group)
        btn_frame1.pack(fill=tk.X, pady=(6, 2))
        self._action_button(btn_frame1, "添加文件", self.add_files, style="Primary.TButton")
        self._action_button(btn_frame1, "移除选中", self.remove_selected_files)
        self._action_button(btn_frame1, "清空列表", self.clear_file_list)

        # 顺序调整（用于控制合并顺序）
        order_frame = ttk.Frame(file_ops_group)
        order_frame.pack(fill=tk.X, pady=2)
        ttk.Label(order_frame, text="顺序", style="Muted.TLabel", width=4).pack(side=tk.LEFT, padx=(2, 4))
        self._action_button(order_frame, "上移", lambda: self.move_file(-1))
        self._action_button(order_frame, "下移", lambda: self.move_file(1))

        # 编码选择
        encode_frame = ttk.Frame(file_ops_group)
        encode_frame.pack(fill=tk.X, pady=(2, 8))
        ttk.Label(encode_frame, text="文件编码：").pack(side=tk.LEFT, padx=2)
        self.encode_var = tk.StringVar(value="utf-8")
        encode_combo = ttk.Combobox(
            encode_frame,
            textvariable=self.encode_var,
            values=["utf-8", "gbk", "gb2312", "utf-16", "ansi"],
            state="readonly",
            width=10
        )
        encode_combo.pack(side=tk.LEFT, padx=5)
        encode_combo.bind("<<ComboboxSelected>>", self.on_encoding_change)

        # 文件工具组（底部锚定，优先分配空间）
        file_tools_group = ttk.LabelFrame(left_frame, text="文件工具", style="Card.TLabelframe")
        file_tools_group.pack(side=tk.BOTTOM, fill=tk.X)

        tools_btn_frame = ttk.Frame(file_tools_group)
        tools_btn_frame.pack(fill=tk.X, pady=(6, 2))
        self._action_button(tools_btn_frame, "合并文件", self.merge_files)
        self._action_button(tools_btn_frame, "分割章节", self.split_chapters)
        self._action_button(tools_btn_frame, "批量命名", self.batch_rename)

        tools_btn_frame2 = ttk.Frame(file_tools_group)
        tools_btn_frame2.pack(fill=tk.X, pady=(2, 2))
        self._action_button(tools_btn_frame2, "导出EPUB", self.export_epub)
        self._action_button(tools_btn_frame2, "导出DOCX", self.export_docx)

        tools_btn_frame3 = ttk.Frame(file_tools_group)
        tools_btn_frame3.pack(fill=tk.X, pady=(2, 6))
        self._action_button(tools_btn_frame3, "十六进制查看", self.show_hex_viewer)
        self._action_button(tools_btn_frame3, "比较文件", self.compare_files)

        # 文件列表（吃剩余空间，小窗口时缩列表而不是裁按钮）
        self.list_group = ttk.LabelFrame(left_frame, text="已加载文件列表（0）",
                                         style="Card.TLabelframe")
        self.list_group.pack(fill=tk.BOTH, expand=True)

        list_scroll = ttk.Scrollbar(self.list_group)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(
            self.list_group,
            yscrollcommand=list_scroll.set,
            selectmode=tk.EXTENDED,
            activestyle=tk.NONE,
            exportselection=False
        )
        self._style_input_widget(self.file_listbox, font=self.listbox_font)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        list_scroll.config(command=self.file_listbox.yview)

        # 绑定列表选择事件
        self.file_listbox.bind('<<ListboxSelect>>', self.show_selected_file_content)

        # ------------------------------ 右侧文本编辑与处理面板 ------------------------------
        right_frame = ttk.Frame(main_frame, style="Page.TFrame")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(6, 0), pady=0)

        # 文本编辑区（pack 移到固定卡片之后：窗口变小时缩编辑区，不裁按钮）
        text_group = ttk.LabelFrame(right_frame, text="文本内容预览/编辑（右键：撤销/剪贴板/全选）",
                                    style="Card.TLabelframe")

        text_y_scroll = ttk.Scrollbar(text_group)
        text_y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text_x_scroll = ttk.Scrollbar(text_group, orient=tk.HORIZONTAL)
        text_x_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.text_area = tk.Text(
            text_group,
            wrap=tk.NONE,
            undo=True  # 启用撤销功能
        )
        self._style_input_widget(self.text_area)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=6, pady=(6, 2))
        text_y_scroll.config(command=self.text_area.yview)
        text_x_scroll.config(command=self.text_area.xview)

        # 编辑内容自动同步（修复：手动编辑不回写缓存的问题）
        self.text_area.bind("<<Modified>>", self._on_editor_modified)

        # 编辑区右键菜单
        self._build_editor_menu()

        # 文本处理功能组（按用途分行）
        process_group = ttk.LabelFrame(right_frame, text="文本处理功能（仅修改内存）",
                                       style="Card.TLabelframe")

        process_rows = [
            ("历史", [
                ("撤销上一步", self.undo_last_batch),
            ]),
            ("排版", [
                ("合并非标点后换行", lambda: self.process_selected_files(self.merge_unwanted_newlines, "合并非标点后换行")),
                ("句号后强制换行", lambda: self.process_selected_files(self.force_newline_after_period, "句号后强制换行")),
                ("段首缩进", lambda: self.process_selected_files(self.add_paragraph_indent, "段首缩进")),
                ("去除段首缩进", lambda: self.process_selected_files(self.remove_paragraph_indent, "去除段首缩进")),
            ]),
            ("清理", [
                ("去除空行", lambda: self.process_selected_files(self.remove_empty_lines, "去除空行")),
                ("去除所有空格", lambda: self.process_selected_files(self.remove_all_spaces, "去除所有空格")),
                ("去除重复行", lambda: self.process_selected_files(self.remove_duplicate_lines, "去除重复行")),
                ("去除日期信息", lambda: self.process_selected_files(self.remove_date_info, "去除日期信息")),
                ("去除HTML标签", lambda: self.process_selected_files(self.strip_html_tags, "去除HTML标签")),
            ]),
            ("小说", [
                ("过滤广告行", self.process_filter_ad_lines),
                ("章节去重", self.process_dedup_chapters),
                ("章节重排", self.process_sort_chapters),
                ("压缩连续空行", lambda: self.process_selected_files(compress_blank_lines, "压缩连续空行")),
                ("清理行首尾空白", lambda: self.process_selected_files(strip_line_edges, "清理行首尾空白")),
            ]),
            ("转换", [
                ("转大写", lambda: self.process_selected_files(self.to_uppercase, "转大写")),
                ("转小写", lambda: self.process_selected_files(self.to_lowercase, "转小写")),
                ("全角转半角", lambda: self.process_selected_files(self.fullwidth_to_halfwidth, "全角转半角")),
                ("中文标点统一", lambda: self.process_selected_files(self.unify_cjk_punctuation, "中文标点统一")),
                ("添加前缀", self.process_add_prefix),
                ("添加后缀", self.process_add_suffix),
            ]),
        ]
        for row_tag, buttons in process_rows:
            row = ttk.Frame(process_group)
            row.pack(fill=tk.X, pady=2, padx=4)
            ttk.Label(row, text=row_tag, style="Muted.TLabel", width=5).pack(side=tk.LEFT)
            for text, cmd in buttons:
                self._action_button(row, text, cmd)

        # 内容提取组
        extract_group = ttk.LabelFrame(right_frame, text="内容提取与检查（结果显示在弹出窗口）",
                                       style="Card.TLabelframe")

        extract_btn_frame = ttk.Frame(extract_group)
        extract_btn_frame.pack(fill=tk.X, pady=6, padx=4)
        ttk.Label(extract_btn_frame, text="提取/检查", style="Muted.TLabel", width=5).pack(side=tk.LEFT)
        ttk.Button(extract_btn_frame, text="邮箱", command=self.extract_emails).pack(side=tk.LEFT, padx=3, pady=2)
        ttk.Button(extract_btn_frame, text="URL", command=self.extract_urls).pack(side=tk.LEFT, padx=3, pady=2)
        ttk.Button(extract_btn_frame, text="手机号", command=self.extract_phones).pack(side=tk.LEFT, padx=3, pady=2)
        ttk.Button(extract_btn_frame, text="敏感词", command=self.check_sensitive_words).pack(side=tk.LEFT, padx=3, pady=2)

        # 保存与统计组（含进度条）
        save_group = ttk.LabelFrame(right_frame, text="保存与统计", style="Card.TLabelframe")

        btn_frame4 = ttk.Frame(save_group)
        btn_frame4.pack(fill=tk.X, pady=(6, 2), padx=4)
        ttk.Button(btn_frame4, text="统计字数", command=self.count_text_words).pack(side=tk.LEFT, padx=3, pady=2)
        self._action_button(btn_frame4, "生成报告", self.generate_report)
        self._action_button(btn_frame4, "保存到原文件", self.save_to_original_files, style="Primary.TButton")
        self._action_button(btn_frame4, "另存为新文件", self.save_as_new_file)

        progress_frame = ttk.Frame(save_group)
        progress_frame.pack(fill=tk.X, pady=(2, 2), padx=4)
        ttk.Label(progress_frame, text="进度", style="Muted.TLabel", width=5).pack(side=tk.LEFT)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode="determinate"
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)

        # 换行符选项（影响"保存到原文件/另存为新文件"的写盘格式）+ 主题切换
        newline_frame = ttk.Frame(save_group)
        newline_frame.pack(fill=tk.X, pady=(2, 2), padx=4)
        ttk.Label(newline_frame, text="换行符", style="Muted.TLabel", width=5).pack(side=tk.LEFT)
        newline_combo = ttk.Combobox(
            newline_frame, textvariable=self.newline_var,
            values=["默认", "LF (Unix)", "CRLF (Windows)"], state="readonly", width=14)
        newline_combo.pack(side=tk.LEFT, padx=3)
        ttk.Label(newline_frame, text="（保存到原文件/另存时生效）",
                  style="Muted.TLabel").pack(side=tk.LEFT, padx=3)

        theme_frame = ttk.Frame(save_group)
        theme_frame.pack(fill=tk.X, pady=(2, 8), padx=4)
        ttk.Label(theme_frame, text="主题", style="Muted.TLabel", width=5).pack(side=tk.LEFT)
        theme_combo = ttk.Combobox(
            theme_frame, textvariable=self.theme_var,
            values=list(_THEMES), state="readonly", width=14)
        theme_combo.pack(side=tk.LEFT, padx=3)
        ttk.Label(theme_frame, text="（切换后重启程序生效）",
                  style="Muted.TLabel").pack(side=tk.LEFT, padx=3)

        # 固定卡片底部锚定（pack 顺序决定视觉顺序：保存最底、处理贴住编辑区）
        save_group.pack(side=tk.BOTTOM, fill=tk.X)
        extract_group.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 8))
        process_group.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 8))

        # 编辑区最后分配剩余空间
        text_group.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def build_find_replace_tab(self, parent):
        """构建查找替换标签页（修复旧版查找定位错乱的缺陷）"""
        main_frame = ttk.Frame(parent, style="Page.TFrame", padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 查找与替换输入区
        find_frame = ttk.LabelFrame(main_frame, text="查找与替换", style="Card.TLabelframe")
        find_frame.pack(fill=tk.X, pady=(0, 8))
        find_frame.columnconfigure(1, weight=1)

        ttk.Label(find_frame, text="查找内容:").grid(row=0, column=0, padx=8, pady=(8, 5), sticky=tk.W)
        self.find_entry = ttk.Entry(find_frame)
        self.find_entry.grid(row=0, column=1, padx=8, pady=(8, 5), sticky=tk.EW)
        self.find_entry.bind('<Return>', lambda e: self.find_next())

        ttk.Label(find_frame, text="替换为:").grid(row=1, column=0, padx=8, pady=5, sticky=tk.W)
        self.replace_entry = ttk.Entry(find_frame)
        self.replace_entry.grid(row=1, column=1, padx=8, pady=5, sticky=tk.EW)

        # 选项区
        options_frame = ttk.LabelFrame(main_frame, text="选项", style="Card.TLabelframe")
        options_frame.pack(fill=tk.X, pady=(0, 8))

        self.case_sensitive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="区分大小写", variable=self.case_sensitive_var).pack(side=tk.LEFT, padx=10, pady=6)

        self.whole_word_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="全字匹配", variable=self.whole_word_var).pack(side=tk.LEFT, padx=10, pady=6)

        self.use_regex_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="使用正则", variable=self.use_regex_var).pack(side=tk.LEFT, padx=10, pady=6)

        # 按钮区
        button_frame = ttk.Frame(main_frame, style="Page.TFrame")
        button_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Button(button_frame, text="查找下一个", command=self.find_next, style="Primary.TButton").pack(side=tk.LEFT, padx=3)
        ttk.Button(button_frame, text="替换", command=self.replace_current).pack(side=tk.LEFT, padx=3)
        ttk.Button(button_frame, text="全部替换", command=self.replace_all_in_preview).pack(side=tk.LEFT, padx=3)
        ttk.Button(button_frame, text="标记全部", command=self.mark_all_matches).pack(side=tk.LEFT, padx=3)
        self._action_button(button_frame, "批量替换所有文件", self.batch_replace_files).pack_configure(padx=(12, 3))
        ttk.Button(button_frame, text="从文件加载", command=self.load_text_from_file).pack(side=tk.LEFT, padx=3)
        ttk.Button(button_frame, text="载入编辑区内容", command=self.load_from_editor).pack(side=tk.LEFT, padx=3)
        ttk.Button(button_frame, text="清除", command=self.clear_find_replace).pack(side=tk.RIGHT, padx=3)

        # 预览区
        preview_frame = ttk.LabelFrame(main_frame, text="文本预览", style="Card.TLabelframe")
        preview_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar_y = ttk.Scrollbar(preview_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.preview_text = tk.Text(
            preview_frame,
            wrap=tk.NONE,
        )
        self._style_input_widget(self.preview_text)
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        scrollbar_y.config(command=self.preview_text.yview)
        scrollbar_x.config(command=self.preview_text.xview)

    def _build_editor_menu(self):
        """编辑区右键菜单：撤销/重做/剪贴板/全选/清空"""
        menu = tk.Menu(self.text_area, tearoff=0, font=self.status_font)
        menu.add_command(label="撤销", command=self._editor_undo)
        menu.add_command(label="重做", command=self._editor_redo)
        menu.add_separator()
        menu.add_command(label="剪切", command=lambda: self.text_area.event_generate("<<Cut>>"))
        menu.add_command(label="复制", command=lambda: self.text_area.event_generate("<<Copy>>"))
        menu.add_command(label="粘贴", command=lambda: self.text_area.event_generate("<<Paste>>"))
        menu.add_command(label="全选", command=lambda: self.text_area.event_generate("<<SelectAll>>"))
        menu.add_separator()
        menu.add_command(label="清空编辑区", command=self._editor_clear)

        def popup(event):
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        self.text_area.bind("<Button-3>", popup)

    def _editor_undo(self):
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass

    def _editor_redo(self):
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            pass

    def _editor_clear(self):
        if messagebox.askyesno("确认", "确定清空编辑区内容吗？\n（单文件视图下将同步清空该文件的内存缓存）"):
            self.text_area.delete("1.0", tk.END)

    # ------------------------------ 后台任务框架 ------------------------------
    def _busy_guard(self):
        """有任务处理中时返回 True 并提示（用于阻止并发任务）"""
        if self._busy:
            self.status_var.set("有任务正在后台处理中，请稍候...")
            return True
        return False

    def _start_task(self, worker, done_title="完成"):
        """启动后台任务：worker 只做计算/IO，通过队列与主线程通信"""
        if self._busy_guard():
            return
        self._busy = True
        self._task_errors = []
        self._task_done_msg = ""
        self._task_done_title = done_title
        self.task_queue = queue.Queue()

        def safe_worker():
            try:
                worker()
            except Exception as e:
                self.task_queue.put(("error", f"任务异常：{str(e)}"))
                self.task_queue.put(("done_msg", "任务已终止"))

        self._task_thread = threading.Thread(target=safe_worker, daemon=True)
        self._task_thread.start()
        self.status_var.set("任务处理中...")
        # 禁用任务相关按钮，显示忙碌指示
        for btn in self.task_buttons:
            try:
                btn.state(["disabled"])
            except tk.TclError:
                pass
        self.busy_label.config(text="● 处理中…")
        self.status_label.config(fg=COLOR_PRIMARY)
        self.root.after(100, self._poll_task)

    def _poll_task(self):
        """主线程轮询任务队列，刷新进度/状态"""
        self._drain_queue()
        if self._task_thread is not None and self._task_thread.is_alive():
            self.root.after(100, self._poll_task)
        else:
            self._finish_task()

    def _drain_queue(self):
        """取出队列中的所有消息并处理（仅主线程调用）"""
        try:
            while True:
                kind, payload = self.task_queue.get_nowait()
                if kind == "progress":
                    self.progress_var.set(payload)
                elif kind == "status":
                    self.status_var.set(payload)
                elif kind == "error":
                    self._task_errors.append(str(payload))
                elif kind == "add_file":
                    path, content, enc = payload
                    if path not in self.file_list:
                        self.file_list.append(path)
                        self.file_listbox.insert(tk.END, os.path.basename(path))
                        self.file_contents[path] = content
                        self.file_encodings[path] = enc
                elif kind == "done_msg":
                    self._task_done_msg = payload
                elif kind == "done_title":
                    self._task_done_title = payload
        except queue.Empty:
            pass
        self._update_list_count()

    def _finish_task(self):
        """任务结束：收尾消息、恢复按钮、刷新显示"""
        self._drain_queue()
        self._busy = False
        self._task_thread = None
        self.progress_var.set(0)
        for btn in self.task_buttons:
            try:
                btn.state(["!disabled"])
            except tk.TclError:
                pass
        self.busy_label.config(text="")
        self.status_label.config(fg=COLOR_MUTED)
        if getattr(self, "_task_was_empty", False) and self.file_list:
            self._task_was_empty = False
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(0)
        self.show_selected_file_content()
        if self._task_errors:
            messagebox.showerror("错误", "部分操作失败：\n" + "\n".join(self._task_errors[:5]))
        else:
            messagebox.showinfo(self._task_done_title, self._task_done_msg)
        if self._undo_stack:
            last = self._undo_stack[-1]
            self.status_var.set(self.status_var.get()
                                + f" | 可撤销：{last['label']} 等 {len(self._undo_stack)} 步")
        if self._task_done_callback:
            callback = self._task_done_callback
            self._task_done_callback = None
            callback()

    # ------------------------------ 编辑同步 ------------------------------
    def _on_editor_modified(self, event=None):
        """<<Modified>> 事件：编辑后延迟同步回缓存（防抖，避免每个按键都全量复制）"""
        if self.text_area.edit_modified():
            self.text_area.edit_modified(False)  # 复位标志，以便继续监听下一次修改
            if self._sync_job is not None:
                try:
                    self.root.after_cancel(self._sync_job)
                except Exception:
                    pass
            self._sync_job = self.root.after(600, self._sync_editor_to_cache)

    def _sync_editor_to_cache(self):
        """把编辑框内容同步回当前显示的文件缓存（仅单文件视图）"""
        self._sync_job = None
        if self._busy:
            return  # 任务处理中，缓存正在被后台线程读写，暂不同步
        if len(self.current_view_files) != 1:
            return  # 多文件视图无法可靠归属，不做同步（界面状态栏有提示）
        file_path = self.current_view_files[0]
        if file_path not in self.file_contents:
            return
        self.file_contents[file_path] = self.text_area.get("1.0", "end-1c")

    # ------------------------------ 文件操作核心方法 ------------------------------
    def enable_drag_and_drop(self):
        """启用文件拖放功能（未安装 tkinterdnd2 时降级）"""
        if not DND_AVAILABLE:
            self.status_var.set("就绪 | 未安装 tkinterdnd2，拖放不可用（pip install tkinterdnd2）")
            return
        try:
            self.file_listbox.drop_target_register(DND_FILES)
            self.file_listbox.dnd_bind('<<Drop>>', self.on_file_drop)
        except tk.TclError:
            pass

    def on_file_drop(self, event):
        """处理文件/文件夹拖放（文件夹自动展开其中的 .txt）"""
        items = self.root.tk.splitlist(event.data)
        file_paths = []
        folder_count = 0
        for item in items:
            if os.path.isdir(item):
                folder_count += 1
                for name in sorted(os.listdir(item)):
                    path = os.path.join(item, name)
                    if name.lower().endswith(".txt") and os.path.isfile(path):
                        file_paths.append(path)
            else:
                file_paths.append(item)
        if folder_count:
            self.status_var.set(f"检测到 {folder_count} 个文件夹，已展开其中的 .txt 文件")
        if file_paths:
            self.add_files_from_paths(file_paths)

    def add_files(self):
        """打开文件选择对话框添加文件"""
        if self._busy_guard():
            return
        file_paths = filedialog.askopenfilenames(
            title="选择要处理的TXT文件",
            filetypes=[("纯文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_paths:
            self.add_files_from_paths(file_paths)

    def add_files_from_paths(self, file_paths):
        """后台线程读取文件并加入列表（自动尝试备选编码并记录实际编码）"""
        if self._busy_guard():
            return
        chosen_display = self.encode_var.get()
        existing = set(self.file_list)
        todo = [p for p in file_paths if p not in existing]
        if not todo:
            self.status_var.set("所选文件均已在列表中")
            return
        self._task_was_empty = not self.file_list

        def worker():
            q = self.task_queue
            for i, path in enumerate(todo):
                try:
                    content, used_enc = self._read_text(path, chosen_display)
                    q.put(("add_file", (path, content, used_enc)))
                    if used_enc != self._display_to_codec(chosen_display):
                        q.put(("status", f"{os.path.basename(path)} 编码不匹配，已按 {used_enc} 自动读取"))
                except Exception as e:
                    q.put(("error", f"读取 {os.path.basename(path)} 失败：{str(e)}"))
                q.put(("progress", (i + 1) * 100 / len(todo)))
            q.put(("status", f"已添加 {len(todo)} 个文件 | 总计 {len(self.file_list)} 个文件"))
            q.put(("done_msg", f"已添加 {len(todo)} 个文件\n总计 {len(self.file_list)} 个文件"))

        self._start_task(worker)

    def remove_selected_files(self):
        """移除选中的文件"""
        if self._busy_guard():
            return
        selected_indices = sorted(self.file_listbox.curselection(), reverse=True)
        if not selected_indices:
            messagebox.showinfo("提示", "请先选择要移除的文件")
            return

        removed_count = 0
        for idx in selected_indices:
            file_path = self.file_list.pop(idx)
            self.file_contents.pop(file_path, None)
            self.file_encodings.pop(file_path, None)
            self.file_listbox.delete(idx)
            removed_count += 1

        self.current_view_files = []
        self.text_area.delete("1.0", tk.END)
        self.status_var.set(f"已移除 {removed_count} 个文件 | 剩余 {len(self.file_list)} 个文件")

    def clear_file_list(self):
        """清空所有文件"""
        if self._busy_guard():
            return
        if not self.file_list:
            messagebox.showinfo("提示", "文件列表已为空")
            return

        if messagebox.askyesno("确认", "确定要清空所有文件吗？（仅清空列表，不修改原文件）"):
            self.file_list.clear()
            self.file_contents.clear()
            self.file_encodings.clear()
            self.current_view_files = []
            self.file_listbox.delete(0, tk.END)
            self.text_area.delete("1.0", tk.END)
            self.root.title(DEFAULT_TITLE)
            self.status_var.set("文件列表已清空")

    def refresh_file_listbox(self):
        """按 file_list 重建列表框显示，并尽量保持原选中项"""
        selected = list(self.file_listbox.curselection())
        self.file_listbox.delete(0, tk.END)
        for path in self.file_list:
            self.file_listbox.insert(tk.END, os.path.basename(path))
        for idx in selected:
            if idx < self.file_listbox.size():
                self.file_listbox.selection_set(idx)

    def move_file(self, delta):
        """将选中的文件项上移（delta=-1）或下移（delta=1），用于调整合并顺序"""
        if self._busy_guard():
            return
        selected = self.file_listbox.curselection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要移动的文件")
            return
        idx = selected[0]
        new_idx = idx + delta
        if 0 <= new_idx < len(self.file_list):
            self.file_list[idx], self.file_list[new_idx] = self.file_list[new_idx], self.file_list[idx]
            self.refresh_file_listbox()
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(new_idx)
            self.show_selected_file_content()

    def on_encoding_change(self, event=None):
        """编码选择变更时的处理（不影响已加载文件，保存时按各自实际编码写回）"""
        self.current_encoding = self.encode_var.get()
        self.status_var.set(
            f"已切换默认编码为：{self.current_encoding}"
            f"（已加载文件保存时仍按各自实际读取编码写回）"
        )

    def show_selected_file_content(self, event=None):
        """显示选中文件的内容（支持多选拼接显示）"""
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            self.current_view_files = []
            self.text_area.delete("1.0", tk.END)
            self.root.title(DEFAULT_TITLE)
            return

        self.current_view_files = [self.file_list[idx] for idx in selected_indices]

        if len(self.current_view_files) == 1:
            # 单文件：原样显示，保证编辑内容可与缓存无损互同步
            file_path = self.current_view_files[0]
            content = self.file_contents.get(file_path, "")
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", content)
            self.root.title(f"{os.path.basename(file_path)} - {DEFAULT_TITLE}")
            try:
                size = os.path.getsize(file_path)
                size_text = (f"{size / 1024:.1f} KB" if size < 1024 * 1024
                             else f"{size / 1024 / 1024:.2f} MB")
            except OSError:
                size_text = "未知大小"
            enc_text = self.file_encodings.get(file_path, "?")
            self.status_var.set(
                f"正在查看: {os.path.basename(file_path)} · {enc_text} · {size_text} · 编辑自动同步")
        else:
            # 多文件：拼接显示（带分隔符），此视图下的编辑不写回原文件
            blocks = []
            for file_path in self.current_view_files:
                blocks.append(f"===== {os.path.basename(file_path)} =====\n"
                              + self.file_contents.get(file_path, ""))
            content = "\n\n".join(blocks)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", content)
            self.root.title(f"{len(self.current_view_files)} 个文件 - {DEFAULT_TITLE}")
            self.status_var.set(
                f"显示 {len(self.current_view_files)} 个文件（多文件视图，编辑不会写回原文件）"
            )

    # ------------------------------ 文件工具 ------------------------------
    def merge_files(self):
        """把选中（或全部）文件合并到编辑区（仅内存，可另存为保存）"""
        if self._busy_guard():
            return
        if not self.file_list:
            messagebox.showinfo("提示", "请先添加文件")
            return

        selected_indices = self.file_listbox.curselection()
        if selected_indices:
            merge_list = [self.file_list[idx] for idx in selected_indices]
        else:
            merge_list = self.file_list.copy()

        blocks = []
        step = 100 / len(merge_list)
        for i, file_path in enumerate(merge_list):
            blocks.append(f"===== {os.path.basename(file_path)} =====\n"
                          + self.file_contents.get(file_path, ""))
            self.progress_var.set((i + 1) * step)
            self.root.update_idletasks()

        merged = "\n\n".join(blocks)
        self.current_view_files = []  # 合并视图不与单个文件同步
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", merged)
        self.progress_var.set(0)
        self.status_var.set(f"已合并 {len(merge_list)} 个文件到编辑区（如需保存请用「另存为新文件」）")
        messagebox.showinfo("完成", f"已合并 {len(merge_list)} 个文件到编辑区\n如需保存请使用「另存为新文件」")

    def split_chapters(self):
        """按章节标题把选中（或全部）文件分割为独立章节文件（可选规则、可预览）"""
        if self._busy_guard():
            return
        target_files = self._select_target_files("分割")
        if not target_files:
            return
        self._show_chapter_split_dialog(target_files)

    def _select_target_files(self, action_name):
        """取选中文件列表；未选中时询问是否处理全部。无可用目标时返回 None（已提示）"""
        selected_indices = self.file_listbox.curselection()
        if selected_indices:
            return [self.file_list[idx] for idx in selected_indices]
        if not self.file_list:
            messagebox.showinfo("提示", "请先添加文件")
            return None
        if not messagebox.askyesno("确认", f"未选择文件，是否{action_name}所有已加载的文件？"):
            return None
        return self.file_list.copy()

    def _show_chapter_split_dialog(self, target_files):
        """章节分割设置弹窗：选择标题规则（内置/自定义正则）、预览章节、确认分割"""
        win = tk.Toplevel(self.root)
        win.title("分割章节")
        win.geometry("680x560")
        win.configure(bg=COLOR_CARD)
        win.transient(self.root)

        rule_names = list(_CHAPTER_PRESETS) + ["自定义正则"]
        rule_frame = ttk.LabelFrame(win, text="章节标题规则", style="Card.TLabelframe")
        rule_frame.pack(fill=tk.X, padx=10, pady=(10, 6))

        rule_var = tk.StringVar(value=rule_names[0])
        rule_combo = ttk.Combobox(rule_frame, textvariable=rule_var,
                                  values=rule_names, state="readonly", width=22)
        rule_combo.pack(side=tk.LEFT, padx=6, pady=6)

        custom_var = tk.StringVar()
        custom_entry = ttk.Entry(rule_frame, textvariable=custom_var)
        custom_entry.state(["disabled"])
        custom_entry.pack(side=tk.LEFT, padx=6, pady=6, fill=tk.X, expand=True)
        hint_label = ttk.Label(rule_frame, text="（可先预览验证）", style="Muted.TLabel")
        hint_label.pack(side=tk.LEFT, padx=6)

        def on_rule_change(event=None):
            is_custom = rule_var.get() == "自定义正则"
            custom_entry.state(["!disabled"] if is_custom else ["disabled"])
            hint_label.configure(text="如: 第\\d+章|Chapter\\s+\\d+" if is_custom else "（可先预览验证）")

        rule_combo.bind("<<ComboboxSelected>>", on_rule_change)

        def resolve_pattern():
            """当前选择 -> 编译后的正则；无效返回 None（已提示）"""
            if rule_var.get() == "自定义正则":
                expr = custom_var.get().strip()
                if not expr:
                    messagebox.showwarning("提示", "请输入自定义正则表达式", parent=win)
                    return None
                try:
                    return re.compile(expr)
                except re.error as e:
                    messagebox.showerror("错误", f"自定义正则无效：{e}", parent=win)
                    return None
            return re.compile(_CHAPTER_PRESETS[rule_var.get()])

        preview_frame = ttk.LabelFrame(win, text="章节预览（章名 + 字数）", style="Card.TLabelframe")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        preview_scroll = ttk.Scrollbar(preview_frame)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        preview_box = tk.Text(preview_frame, wrap=tk.WORD)
        self._style_input_widget(preview_box, font=self.listbox_font)
        preview_box.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        preview_box.config(yscrollcommand=preview_scroll.set)
        preview_scroll.config(command=preview_box.yview)

        def do_preview():
            pattern = resolve_pattern()
            if pattern is None:
                return
            preview_box.delete("1.0", tk.END)
            found_any = False
            for file_path in target_files:
                blocks = split_chapters_by_pattern(self.file_contents.get(file_path, ""), pattern)
                chapters = [(t, b) for t, b in blocks if t is not None]
                preview_box.insert(tk.END, f"【{os.path.basename(file_path)}】识别到 {len(chapters)} 章\n")
                for i, (t, b) in enumerate(chapters[:50], 1):
                    preview_box.insert(tk.END, f"    {i:03d} {t}（{len(b.strip())} 字）\n")
                if len(chapters) > 50:
                    preview_box.insert(tk.END, f"    ...（其余 {len(chapters) - 50} 章略）\n")
                if chapters:
                    found_any = True
            if not found_any:
                preview_box.insert(tk.END, "\n未识别到任何章节标题，请调整规则后重试。\n")

        def do_split():
            pattern = resolve_pattern()
            if pattern is None:
                return
            save_dir = filedialog.askdirectory(title="选择章节文件保存目录", parent=win)
            if not save_dir:
                return
            win.destroy()
            self._run_chapter_split(target_files, pattern, save_dir)

        btn_bar = ttk.Frame(win, style="Page.TFrame")
        btn_bar.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(btn_bar, text="预览章节", command=do_preview).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_bar, text="开始分割", command=do_split, style="Primary.TButton").pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_bar, text="取消", command=win.destroy).pack(side=tk.RIGHT, padx=3)

    def _run_chapter_split(self, target_files, pattern, save_dir):
        """后台执行章节分割：按标题写独立文件，并生成章节索引"""
        # 默认编码需在主线程预先求值（Tk 变量不能在后台线程访问）
        default_encode = self._display_to_codec(self.encode_var.get())

        def worker():
            q = self.task_queue
            total_chapters = 0
            total_indexes = 0
            step = 100 / len(target_files)

            for idx, file_path in enumerate(target_files):
                try:
                    content = self.file_contents.get(file_path, "")
                    stem = os.path.splitext(os.path.basename(file_path))[0]
                    encode = self.file_encodings.get(file_path, default_encode)

                    blocks = split_chapters_by_pattern(content, pattern)
                    if not any(t is not None for t, _ in blocks):
                        q.put(("error", f"{os.path.basename(file_path)}：未识别到章节标题，已跳过"))
                        continue

                    entries = []
                    seq = 0
                    for title, body in blocks:
                        text = body.strip()
                        if title is None:
                            if not text:
                                continue
                            fname = f"{stem}_00_开头.txt"
                            write_text = text
                        else:
                            seq += 1
                            safe_title = re.sub(r'[\\/:*?"<>|\s]+', "_", title)
                            fname = f"{stem}_{seq:03d}_{safe_title}.txt"
                            write_text = f"{title}\n\n{text}"
                        with open(os.path.join(save_dir, fname), "w", encoding=encode) as f:
                            f.write(write_text)
                        total_chapters += 1
                        entries.append(f"{fname}  （{len(text)} 字）")

                    index_name = "章节索引.txt" if len(target_files) == 1 else f"章节索引_{stem}.txt"
                    with open(os.path.join(save_dir, index_name), "w", encoding=encode) as f:
                        f.write(f"《{stem}》共 {len(entries)} 个文件\n\n" + "\n".join(entries))
                    total_indexes += 1
                except Exception as e:
                    q.put(("error", f"{os.path.basename(file_path)}：{str(e)}"))

                q.put(("progress", (idx + 1) * step))

            q.put(("progress", 0))
            q.put(("status", f"章节分割完成 | 共 {total_chapters} 个文件 | 索引 {total_indexes} 份"))
            if total_chapters:
                q.put(("done_msg", f"共分割出 {total_chapters} 个章节文件，生成 {total_indexes} 份章节索引\n保存于：{save_dir}"))
            else:
                q.put(("done_msg", "没有分割出任何章节文件"))

        self._start_task(worker)

    def batch_rename(self):
        """批量重命名选中的文件（前缀 + 起始编号，保留扩展名）"""
        if self._busy_guard():
            return
        selected_indices = list(self.file_listbox.curselection())
        if not selected_indices:
            messagebox.showinfo("提示", "请先选择要重命名的文件")
            return

        prefix = simpledialog.askstring("批量命名", "请输入文件名前缀:", parent=self.root)
        if not prefix:
            return
        start_num = simpledialog.askinteger(
            "批量命名", "请输入起始编号:", minvalue=0, initialvalue=1, parent=self.root)
        if start_num is None:
            return

        if not messagebox.askyesno(
                "确认", f"将把 {len(selected_indices)} 个文件重命名为 \"{prefix}编号.扩展名\" 的形式，是否继续？"):
            return

        renamed = 0
        for i, idx in enumerate(selected_indices):
            old_path = self.file_list[idx]
            dir_name = os.path.dirname(old_path)
            ext = os.path.splitext(old_path)[1]
            new_path = os.path.join(dir_name, f"{prefix}{start_num + i}{ext}")
            try:
                if os.path.exists(new_path) and new_path != old_path:
                    raise OSError(f"目标文件已存在：{new_path}")
                os.rename(old_path, new_path)
                self.file_list[idx] = new_path
                self.file_contents[new_path] = self.file_contents.pop(old_path, "")
                self.file_encodings[new_path] = self.file_encodings.pop(
                    old_path, self._display_to_codec(self.encode_var.get()))
                renamed += 1
            except Exception as e:
                messagebox.showerror("错误", f"重命名 {os.path.basename(old_path)} 失败：{str(e)}")
                break

        self.refresh_file_listbox()
        self.status_var.set(f"已批量重命名 {renamed} 个文件")

    def export_epub(self):
        """把选中（或全部）文件按章节规则分章后导出为 EPUB3 电子书（后台线程执行）"""
        if self._busy_guard():
            return
        target_files = self._select_target_files("导出EPUB")
        if not target_files:
            return
        self._show_epub_export_dialog(target_files)

    def _show_epub_export_dialog(self, target_files):
        """EPUB 导出设置：作者名与封面图（作者名随设置持久化）"""
        win = tk.Toplevel(self.root)
        win.title("导出 EPUB")
        win.geometry("540x260")
        win.configure(bg=COLOR_CARD)
        win.transient(self.root)

        form = ttk.LabelFrame(win, text="书籍信息（对本次导出的所有文件生效）",
                              style="Card.TLabelframe")
        form.pack(fill=tk.X, padx=10, pady=(10, 6))

        author_row = ttk.Frame(form)
        author_row.pack(fill=tk.X, padx=6, pady=4)
        ttk.Label(author_row, text="作者名", width=8).pack(side=tk.LEFT)
        author_var = tk.StringVar(value=self.epub_author)
        ttk.Entry(author_row, textvariable=author_var, width=28).pack(side=tk.LEFT, padx=3)

        cover_row = ttk.Frame(form)
        cover_row.pack(fill=tk.X, padx=6, pady=4)
        ttk.Label(cover_row, text="封面图", width=8).pack(side=tk.LEFT)
        cover_var = tk.StringVar(value="")
        cover_label = ttk.Label(cover_row, text="（未选择，可选 jpg/png/gif）",
                                style="Muted.TLabel")

        def choose_cover():
            path = filedialog.askopenfilename(
                title="选择封面图片",
                filetypes=[("图片", "*.jpg *.jpeg *.png *.gif"), ("所有文件", "*.*")],
                parent=win)
            if path:
                cover_var.set(path)
                cover_label.configure(text=os.path.basename(path))

        def clear_cover():
            cover_var.set("")
            cover_label.configure(text="（未选择，可选 jpg/png/gif）")

        ttk.Button(cover_row, text="选择图片...", command=choose_cover).pack(side=tk.LEFT, padx=3)
        ttk.Button(cover_row, text="清除", command=clear_cover).pack(side=tk.LEFT, padx=3)
        cover_label.pack(side=tk.LEFT, padx=3)

        ttk.Label(win, text="将按章节规则自动分章，每个文件生成一本 .epub 到所选目录。",
                  style="Muted.TLabel").pack(anchor=tk.W, padx=10, pady=4)

        def confirm():
            author = author_var.get().strip()
            cover_bytes, cover_ext = None, ".jpg"
            cover_path = cover_var.get()
            if cover_path:
                ext = os.path.splitext(cover_path)[1].lower()
                if ext not in _COVER_MEDIA_TYPES:
                    messagebox.showerror("错误", "封面仅支持 jpg / png / gif", parent=win)
                    return
                try:
                    with open(cover_path, "rb") as f:
                        cover_bytes = f.read()
                    cover_ext = ext
                except Exception as e:
                    messagebox.showerror("错误", f"读取封面失败：{e}", parent=win)
                    return
            self.epub_author = author
            self.save_settings()
            win.destroy()
            save_dir = filedialog.askdirectory(title="选择 EPUB 保存目录")
            if not save_dir:
                return
            self._run_epub_export(target_files, author, cover_bytes, cover_ext, save_dir)

        btn_bar = ttk.Frame(win, style="Page.TFrame")
        btn_bar.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(btn_bar, text="开始导出", command=confirm, style="Primary.TButton").pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_bar, text="取消", command=win.destroy).pack(side=tk.RIGHT, padx=3)

    def _run_epub_export(self, target_files, author, cover_bytes, cover_ext, save_dir):
        """后台执行 EPUB 导出"""
        def worker():
            q = self.task_queue
            exported = 0
            step = 100 / len(target_files)
            for idx, file_path in enumerate(target_files):
                try:
                    content = self.file_contents.get(file_path, "")
                    stem = os.path.splitext(os.path.basename(file_path))[0]
                    pattern = re.compile(_CHAPTER_PRESETS["第X章+序章/楔子/番外"])
                    blocks = split_chapters_by_pattern(content, pattern)
                    # 开头内容作为"前言"章节；跳过空章节
                    chapters = [("前言", b) if t is None else (t, b)
                                for t, b in blocks if b.strip()]
                    if not chapters:
                        q.put(("error", f"{os.path.basename(file_path)}：内容为空，已跳过"))
                        continue
                    epub_path = os.path.join(save_dir, f"{stem}.epub")
                    build_epub(epub_path, stem, chapters, author=author,
                               cover=cover_bytes, cover_ext=cover_ext)
                    exported += 1
                except Exception as e:
                    q.put(("error", f"{os.path.basename(file_path)}：{str(e)}"))
                q.put(("progress", (idx + 1) * step))

            q.put(("progress", 0))
            q.put(("status", f"EPUB 导出完成 | 成功 {exported}/{len(target_files)} 本"))
            q.put(("done_msg", f"已导出 {exported} 本 EPUB\n保存于：{save_dir}"))

        self._start_task(worker)

    def export_docx(self):
        """把选中（或全部）文件按章节规则分章后导出为 Word 文档（后台线程执行）"""
        if self._busy_guard():
            return
        target_files = self._select_target_files("导出DOCX")
        if not target_files:
            return
        if len(target_files) == 1:
            default_name = os.path.splitext(os.path.basename(target_files[0]))[0] + ".docx"
            out_path = filedialog.asksaveasfilename(
                title="保存 Word 文档", defaultextension=".docx", initialfile=default_name,
                filetypes=[("Word 文档", "*.docx"), ("所有文件", "*.*")])
            if not out_path:
                return
            jobs = [(fp, out_path) for fp in target_files]
        else:
            save_dir = filedialog.askdirectory(title="选择 Word 文档保存目录")
            if not save_dir:
                return
            jobs = [(fp, os.path.join(save_dir, os.path.splitext(os.path.basename(fp))[0] + ".docx"))
                    for fp in target_files]

        def worker():
            q = self.task_queue
            exported = 0
            step = 100 / len(jobs)
            for idx, (file_path, out_path) in enumerate(jobs):
                try:
                    content = self.file_contents.get(file_path, "")
                    stem = os.path.splitext(os.path.basename(file_path))[0]
                    pattern = re.compile(_CHAPTER_PRESETS["第X章+序章/楔子/番外"])
                    blocks = split_chapters_by_pattern(content, pattern)
                    chapters = [("前言", b) if t is None else (t, b)
                                for t, b in blocks if b.strip()]
                    if not chapters:
                        q.put(("error", f"{os.path.basename(file_path)}：内容为空，已跳过"))
                        continue
                    build_docx(out_path, stem, chapters)
                    exported += 1
                except Exception as e:
                    q.put(("error", f"{os.path.basename(file_path)}：{str(e)}"))
                q.put(("progress", (idx + 1) * step))

            q.put(("progress", 0))
            q.put(("status", f"DOCX 导出完成 | 成功 {exported}/{len(jobs)} 个"))
            q.put(("done_msg", f"已导出 {exported} 个 Word 文档"))

        self._start_task(worker)

    def show_hex_viewer(self):
        """以十六进制查看选中文件的开头字节，附编码体检提示（排查乱码根源）"""
        selected = self.file_listbox.curselection()
        if not selected:
            messagebox.showinfo("提示", "请先在列表中选中一个文件")
            return
        file_path = self.file_list[selected[0]]
        try:
            with open(file_path, "rb") as f:
                data = f.read(_HEX_VIEW_BYTES + 1024)
            full_size = os.path.getsize(file_path)
        except Exception as e:
            messagebox.showerror("错误", f"读取文件失败：{e}")
            return

        hints = "；".join(detect_encoding_hints(data[:4096]))
        header = (f"文件：{os.path.basename(file_path)} · {full_size:,} 字节\n"
                  f"编码体检：{hints}\n"
                  + (f"（仅显示前 {_HEX_VIEW_BYTES:,} 字节）\n" if full_size > _HEX_VIEW_BYTES else "")
                  + "─" * 60 + "\n")
        dump = hex_dump(data[:_HEX_VIEW_BYTES])

        win = tk.Toplevel(self.root)
        win.title(f"十六进制查看 - {os.path.basename(file_path)}")
        win.geometry("860x560")
        win.configure(bg=COLOR_CARD)
        win.transient(self.root)

        mono = ("Consolas", 10) if sys.platform.startswith("win") else ("Menlo", 10)
        box = tk.Text(win, wrap=tk.NONE)
        self._style_input_widget(box, font=mono)
        box.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        box.insert("1.0", header + dump)
        box.configure(state=tk.DISABLED)  # 只读

        def copy_all():
            self.root.clipboard_clear()
            self.root.clipboard_append(header + dump)
            self.status_var.set("十六进制转储已复制到剪贴板")

        ttk.Button(win, text="复制全部", command=copy_all,
                   style="Primary.TButton").pack(side=tk.BOTTOM, pady=(0, 8))

    def compare_files(self):
        """对比恰好两个选中文件的文本差异，生成彩色 HTML 报告并用浏览器打开"""
        selected = self.file_listbox.curselection()
        if len(selected) != 2:
            messagebox.showinfo("提示", "请在文件列表中恰好选中两个文件（按住 Ctrl 多选）")
            return
        path_a, path_b = (self.file_list[i] for i in selected)
        try:
            text_a, _ = read_text_smart(path_a, self.encode_var.get())
            text_b, _ = read_text_smart(path_b, self.encode_var.get())
        except Exception as e:
            messagebox.showerror("错误", f"读取文件失败：{e}")
            return

        name_a = os.path.basename(path_a)
        name_b = os.path.basename(path_b)
        report = unified_diff_html(name_a, name_b, text_a, text_b)
        out = os.path.join(tempfile.gettempdir(),
                           f"对比_{os.path.splitext(name_a)[0]}_vs_{os.path.splitext(name_b)[0]}.html")
        try:
            with open(out, "w", encoding="utf-8") as f:
                f.write(report)
            webbrowser.open("file:///" + out.replace("\\", "/"))
            self.status_var.set(f"对比报告已生成：{out}")
        except Exception as e:
            messagebox.showerror("错误", f"生成对比报告失败：{e}")

    # ------------------------------ 文本处理核心方法 ------------------------------
    def process_selected_files(self, process_func, label="批量文本处理"):
        """批量处理选中的文件（未选中时询问是否处理全部），后台线程执行，仅修改内存。
        修改前自动快照，可通过「撤销上一步」恢复。"""
        if self._busy_guard():
            return
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            if not self.file_list:
                messagebox.showinfo("提示", "没有文件可处理")
                return
            if not messagebox.askyesno("确认", "未选择文件，是否处理所有已加载的文件？"):
                return
            target_files = self.file_list.copy()
        else:
            target_files = [self.file_list[idx] for idx in selected_indices]

        if not target_files:
            messagebox.showinfo("提示", "没有文件可处理")
            return

        self._push_undo(label, target_files)
        def worker():
            q = self.task_queue
            step = 100 / len(target_files)
            success_count = 0
            for idx, file_path in enumerate(target_files):
                try:
                    original_content = self.file_contents.get(file_path, "")
                    self.file_contents[file_path] = process_func(original_content)
                    success_count += 1
                except Exception as e:
                    q.put(("error", f"处理 {os.path.basename(file_path)} 失败：{str(e)}"))
                q.put(("progress", (idx + 1) * step))

            q.put(("progress", 0))
            q.put(("status", f"处理完成 | 成功 {success_count}/{len(target_files)} 个文件 | 仅修改内存，需手动保存"))
            q.put(("done_msg", f"成功处理 {success_count} 个文件\n（修改仅在内存中，需手动保存到文件）"))

        self._start_task(worker)

    def process_add_prefix(self):
        """为每一行添加前缀"""
        prefix = simpledialog.askstring("添加前缀", "请输入要添加的前缀:", parent=self.root)
        if prefix is None:
            return
        self.process_selected_files(
            lambda t: "\n".join(prefix + line for line in t.splitlines()), "添加前缀")

    def process_add_suffix(self):
        """为每一行添加后缀"""
        suffix = simpledialog.askstring("添加后缀", "请输入要添加的后缀:", parent=self.root)
        if suffix is None:
            return
        self.process_selected_files(
            lambda t: "\n".join(line + suffix for line in t.splitlines()), "添加后缀")

    def remove_empty_lines(self, text):
        """去除空行（保留有效内容行）"""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = [line for line in text.split("\n") if line.strip()]
        return "\n".join(lines)

    def remove_all_spaces(self, text):
        """去除所有空格和制表符（保留换行）"""
        return text.replace(" ", "").replace("\t", "")

    def remove_date_info(self, text):
        """去除常见日期格式"""
        date_patterns = [
            r"\d{4}-\d{2}-\d{2}",     # 2025-12-05
            r"\d{2}/\d{2}/\d{4}",     # 05/12/2025
            r"\d{4}年\d{1,2}月\d{1,2}日",  # 2025年12月5日
            r"\d{2}:\d{2}:\d{2}",     # 12:30:45
            r"\d{4}/\d{2}/\d{2}"      # 2025/12/05
        ]
        processed_text = text
        for pattern in date_patterns:
            processed_text = re.sub(pattern, "", processed_text)
        return processed_text

    def remove_duplicate_lines(self, text):
        """去除重复行（保持原有顺序）"""
        seen = set()
        result = []
        for line in text.splitlines():
            if line not in seen:
                seen.add(line)
                result.append(line)
        return "\n".join(result)

    def to_uppercase(self, text):
        """转换为大写"""
        return text.upper()

    def to_lowercase(self, text):
        """转换为小写"""
        return text.lower()

    def add_paragraph_indent(self, text):
        """段首添加两个全角空格（空行保持为空）"""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        return "\n".join(
            ("　　" + line.strip()) if line.strip() else ""
            for line in text.split("\n")
        )

    def remove_paragraph_indent(self, text):
        """去除段首缩进（半角/全角空格、制表符）"""
        return "\n".join(line.lstrip(" \t　") for line in text.split("\n"))

    def fullwidth_to_halfwidth(self, text):
        """全角字母/数字转半角（全角空格一并转换；不改动中文标点）"""
        return text.translate(_FULLWIDTH_TABLE)

    def unify_cjk_punctuation(self, text):
        """把中文之间的半角标点统一为全角（英文单词间、数字间、网址不受影响）"""
        cjk = r"[\u4e00-\u9fff]"
        mapping = {",": "，", "!": "！", "?": "？", ";": "；", ":": "：", ".": "。"}
        for half, full in mapping.items():
            text = re.sub(rf"(?<={cjk}){re.escape(half)}(?={cjk})", full, text)
        return text

    def strip_html_tags(self, text):
        """去除HTML标签并还原常见实体"""
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(
            r"&#(\d+);",
            lambda m: chr(int(m.group(1))) if int(m.group(1)) < 0x110000 else "",
            text
        )
        entities = {
            "&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">",
            "&quot;": '"', "&apos;": "'", "&ldquo;": "“", "&rdquo;": "”",
        }
        for ent, ch in entities.items():
            text = text.replace(ent, ch)
        return text

    def merge_unwanted_newlines(self, text):
        """
        合并非标点后的换行
        规则：
        1. 行尾是标点 → 保留换行
        2. 行尾不是标点 → 合并到下一行（用空格分隔）
        3. 空行直接移除
        """
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = text.split("\n")

        if not lines:
            return ""

        punctuation = "。！？；：，,.!?;:"
        result = []
        buffer = ""  # 缓存非标点结尾的行

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue  # 跳过空行

            if buffer:
                line_stripped = f"{buffer} {line_stripped}"
                buffer = ""

            last_char = line_stripped[-1] if line_stripped else ""
            if last_char in punctuation:
                result.append(line_stripped)
            else:
                buffer = line_stripped

        if buffer:
            result.append(buffer)

        return "\n".join(result)

    def force_newline_after_period(self, text):
        """
        句号后强制换行
        规则：
        1. 中文句号（。）后添加换行（排除已有换行的情况）
        2. 英文句号（.）后添加换行（排除缩写/网址/小数等场景）
        3. 自动清理句号后的多余空白
        """
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        if not text:
            return ""

        result = []
        i = 0
        text_length = len(text)

        while i < text_length:
            char = text[i]
            result.append(char)

            # 中文句号
            if char == "。":
                j = i + 1
                while j < text_length and text[j] in " \t":
                    j += 1
                if j < text_length and text[j] != "\n":
                    result.append("\n")
                i = j
                continue

            # 英文句号（排除缩写/网址/小数）
            elif char == ".":
                skip = False
                # 形如 U.S. 的大写缩写
                if i > 1 and text[i - 1].isupper() and text[i - 2].isalpha():
                    skip = True
                # 后面紧跟字母/数字（网址、小数等）
                elif i + 1 < text_length and text[i + 1].isalnum():
                    skip = True

                if not skip:
                    j = i + 1
                    while j < text_length and text[j] in " \t":
                        j += 1
                    if j < text_length and text[j] != "\n":
                        result.append("\n")
                    i = j
                    continue

            i += 1

        return "".join(result)

    # ------------------------------ 小说清洗 ------------------------------
    def process_filter_ad_lines(self):
        """过滤广告行：编辑关键词列表后批量删除含关键词的行（后台线程执行）"""
        if self._busy_guard():
            return
        target_files = self._select_target_files("清洗")
        if not target_files:
            return
        self._show_ad_filter_dialog(target_files)

    def _show_ad_filter_dialog(self, target_files):
        """广告关键词编辑弹窗：支持手动输入/从文件导入，列表随设置持久化"""
        win = tk.Toplevel(self.root)
        win.title("过滤广告行")
        win.geometry("520x430")
        win.configure(bg=COLOR_CARD)
        win.transient(self.root)

        ttk.Label(win, text="每行一个关键词，包含任一关键词的行将被删除（仅修改内存）：",
                  style="Muted.TLabel").pack(anchor=tk.W, padx=10, pady=(10, 4))

        scroll = ttk.Scrollbar(win)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        words_box = tk.Text(win, wrap=tk.WORD)
        self._style_input_widget(words_box, font=self.listbox_font)
        words_box.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        words_box.config(yscrollcommand=scroll.set)
        scroll.config(command=words_box.yview)
        if self.ad_filter_words:
            words_box.insert("1.0", "\n".join(self.ad_filter_words))

        whole_line_var = tk.BooleanVar(value=self.ad_whole_line)
        ttk.Checkbutton(win, text="整行完全匹配关键词才删除（默认：包含即删）",
                        variable=whole_line_var).pack(anchor=tk.W, padx=10, pady=2)

        def import_words():
            path = filedialog.askopenfilename(
                title="选择关键词文件（每行一个）",
                filetypes=[("纯文本文件", "*.txt"), ("所有文件", "*.*")])
            if not path:
                return
            try:
                content, _ = self._read_text(path, "utf-8")
                existing = [w.strip() for w in words_box.get("1.0", "end-1c").splitlines()]
                merged = [w for w in existing + [w2.strip() for w2 in content.splitlines()] if w]
                seen = set()
                merged = [w for w in merged if not (w in seen or seen.add(w))]
                words_box.delete("1.0", tk.END)
                words_box.insert("1.0", "\n".join(merged))
            except Exception as e:
                messagebox.showerror("错误", f"读取关键词文件失败：{e}", parent=win)

        def confirm():
            words = []
            seen = set()
            for w in words_box.get("1.0", "end-1c").splitlines():
                w = w.strip()
                if w and w not in seen:
                    seen.add(w)
                    words.append(w)
            self.ad_filter_words = words
            self.ad_whole_line = whole_line_var.get()
            self.save_settings()
            win.destroy()
            if not words:
                messagebox.showinfo("提示", "关键词列表为空，未执行过滤")
                return
            self._run_filter_ad_lines(target_files, words, self.ad_whole_line)

        btn_bar = ttk.Frame(win, style="Page.TFrame")
        btn_bar.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(btn_bar, text="从文件导入", command=import_words).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_bar, text="确定", command=confirm, style="Primary.TButton").pack(side=tk.RIGHT, padx=3)
        ttk.Button(btn_bar, text="取消", command=win.destroy).pack(side=tk.RIGHT, padx=3)

    def _run_filter_ad_lines(self, target_files, keywords, whole_line):
        """后台执行广告行过滤，统计各文件删除行数"""
        self._push_undo("过滤广告行", target_files)

        def worker():
            q = self.task_queue
            total_removed = 0
            files_hit = 0
            step = 100 / len(target_files)
            for idx, file_path in enumerate(target_files):
                try:
                    content = self.file_contents.get(file_path, "")
                    new_content, removed = filter_ad_lines(content, keywords, whole_line)
                    if removed:
                        self.file_contents[file_path] = new_content
                        total_removed += removed
                        files_hit += 1
                except Exception as e:
                    q.put(("error", f"{os.path.basename(file_path)}：{str(e)}"))
                q.put(("progress", (idx + 1) * step))

            q.put(("progress", 0))
            q.put(("status", f"广告过滤完成 | {files_hit}/{len(target_files)} 个文件命中 | "
                             f"共删除 {total_removed} 行（仅修改内存，需手动保存）"))
            q.put(("done_msg", f"{files_hit}/{len(target_files)} 个文件命中\n共删除 {total_removed} 行"))

        self._start_task(worker)

    def process_dedup_chapters(self):
        """章节去重：识别章节后剔除完全重复/同标题正文高度相似的章节（后台线程执行）"""
        if self._busy_guard():
            return
        target_files = self._select_target_files("去重")
        if not target_files:
            return
        self._push_undo("章节去重", target_files)
        pattern = re.compile(_CHAPTER_PRESETS["第X章+序章/楔子/番外"])

        def worker():
            q = self.task_queue
            total_removed = 0
            files_hit = 0
            summary = []
            step = 100 / len(target_files)
            for idx, file_path in enumerate(target_files):
                try:
                    content = self.file_contents.get(file_path, "")
                    blocks = split_chapters_by_pattern(content, pattern)
                    if sum(1 for t, _ in blocks if t is not None) < 2:
                        q.put(("error", f"{os.path.basename(file_path)}：未识别到章节（或仅一章），已跳过"))
                        continue
                    kept, removed = dedup_chapter_blocks(blocks)
                    if removed:
                        self.file_contents[file_path] = rebuild_text_from_blocks(kept)
                        total_removed += len(removed)
                        files_hit += 1
                        summary.append(f"{os.path.basename(file_path)}：剔除 {len(removed)} 章，如 {removed[0]}")
                except Exception as e:
                    q.put(("error", f"{os.path.basename(file_path)}：{str(e)}"))
                q.put(("progress", (idx + 1) * step))

            q.put(("progress", 0))
            q.put(("status", f"章节去重完成 | {files_hit}/{len(target_files)} 个文件命中 | "
                             f"共剔除 {total_removed} 章（仅修改内存，需手动保存）"))
            if summary:
                q.put(("done_msg", f"共剔除 {total_removed} 章\n" + "\n".join(summary[:10])))
            else:
                q.put(("done_msg", "未发现重复章节"))

        self._start_task(worker)

    def process_sort_chapters(self):
        """章节重排：按标题编号（中文/阿拉伯数字）升序整理乱序章节（后台线程执行）"""
        if self._busy_guard():
            return
        target_files = self._select_target_files("排序")
        if not target_files:
            return
        self._push_undo("章节重排", target_files)
        pattern = re.compile(_CHAPTER_PRESETS["第X章+序章/楔子/番外"])

        def worker():
            q = self.task_queue
            sorted_files = 0
            step = 100 / len(target_files)
            for idx, file_path in enumerate(target_files):
                try:
                    content = self.file_contents.get(file_path, "")
                    blocks = split_chapters_by_pattern(content, pattern)
                    if sum(1 for t, _ in blocks if t is not None) < 2:
                        q.put(("error", f"{os.path.basename(file_path)}：未识别到章节（或仅一章），已跳过"))
                        continue
                    ordered = sort_chapter_blocks(blocks)
                    if ordered != blocks:
                        self.file_contents[file_path] = rebuild_text_from_blocks(ordered)
                        sorted_files += 1
                except Exception as e:
                    q.put(("error", f"{os.path.basename(file_path)}：{str(e)}"))
                q.put(("progress", (idx + 1) * step))

            q.put(("progress", 0))
            q.put(("status", f"章节重排完成 | {sorted_files}/{len(target_files)} 个文件有调整"
                             f"（仅修改内存，需手动保存）"))
            q.put(("done_msg", f"{sorted_files}/{len(target_files)} 个文件的章节顺序有调整"
                               f"\n（编号解析失败的章节排在最后）"))

        self._start_task(worker)

    # ------------------------------ 内容提取 ------------------------------
    def extract_emails(self):
        """提取邮箱地址"""
        self._show_extraction("邮箱地址")

    def extract_urls(self):
        """提取URL链接"""
        self._show_extraction("URL链接")

    def extract_phones(self):
        """提取手机号"""
        self._show_extraction("手机号")

    def _show_extraction(self, title):
        """按正则从编辑区提取内容，弹窗显示结果（去重、保序）"""
        text = self.text_area.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showinfo("提示", "请先在编辑区载入文本")
            return
        items = []
        seen = set()
        for item in re.findall(_EXTRACT_PATTERNS[title], text):
            if item not in seen:
                seen.add(item)
                items.append(item)

        if not items:
            messagebox.showinfo(title, "未找到匹配内容")
            return

        win = tk.Toplevel(self.root)
        win.title(f"{title}（{len(items)} 项）")
        win.geometry("520x420")
        win.configure(bg=COLOR_CARD)
        win.transient(self.root)

        btn_bar = ttk.Frame(win)
        btn_bar.pack(fill=tk.X, padx=6, pady=(6, 0))

        result_text = tk.Text(win, wrap=tk.WORD)
        self._style_input_widget(result_text, font=self.text_font)
        scrollbar = ttk.Scrollbar(win, command=result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        result_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        result_text.config(yscrollcommand=scrollbar.set)
        result_text.insert("1.0", "\n".join(items))

        def copy_all():
            self.root.clipboard_clear()
            self.root.clipboard_append("\n".join(items))
            self.status_var.set(f"{title} 已复制到剪贴板（共 {len(items)} 项）")

        def save_to_file():
            path = filedialog.asksaveasfilename(
                title="保存提取结果",
                defaultextension=".txt",
                filetypes=[("纯文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            if not path:
                return
            try:
                encode = self._display_to_codec(self.encode_var.get())
                with open(path, "w", encoding=encode) as f:
                    f.write("\n".join(items))
                self.status_var.set(f"{title} 已保存到 {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{str(e)}")

        ttk.Button(btn_bar, text="复制全部", command=copy_all, style="Primary.TButton").pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Button(btn_bar, text="保存为文件", command=save_to_file).pack(side=tk.LEFT, padx=3, pady=3)

    # ------------------------------ 敏感词检查 ------------------------------
    def check_sensitive_words(self):
        """敏感词检查：按词表定位命中行（只读分析，不修改任何内容）"""
        if self._busy_guard():
            return
        target_files = self._select_target_files("检查")
        if not target_files:
            return
        self._show_sensitive_dialog(target_files)

    def _show_sensitive_dialog(self, target_files):
        """敏感词表编辑弹窗：支持手动输入/从文件导入，词表随设置持久化"""
        win = tk.Toplevel(self.root)
        win.title("敏感词检查")
        win.geometry("520x430")
        win.configure(bg=COLOR_CARD)
        win.transient(self.root)

        ttk.Label(win, text="每行一个敏感词，将定位所有包含敏感词的行（只读检查，不修改内容）：",
                  style="Muted.TLabel").pack(anchor=tk.W, padx=10, pady=(10, 4))

        scroll = ttk.Scrollbar(win)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        words_box = tk.Text(win, wrap=tk.WORD)
        self._style_input_widget(words_box, font=self.listbox_font)
        words_box.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        words_box.config(yscrollcommand=scroll.set)
        scroll.config(command=words_box.yview)
        if self.sensitive_words:
            words_box.insert("1.0", "\n".join(self.sensitive_words))

        def import_words():
            path = filedialog.askopenfilename(
                title="选择词表文件（每行一个）",
                filetypes=[("纯文本文件", "*.txt"), ("所有文件", "*.*")], parent=win)
            if not path:
                return
            try:
                content, _ = self._read_text(path, "utf-8")
                existing = [w.strip() for w in words_box.get("1.0", "end-1c").splitlines()]
                merged = [w for w in existing + [w2.strip() for w2 in content.splitlines()] if w]
                seen = set()
                merged = [w for w in merged if not (w in seen or seen.add(w))]
                words_box.delete("1.0", tk.END)
                words_box.insert("1.0", "\n".join(merged))
            except Exception as e:
                messagebox.showerror("错误", f"读取词表文件失败：{e}", parent=win)

        def confirm():
            words = []
            seen = set()
            for w in words_box.get("1.0", "end-1c").splitlines():
                w = w.strip()
                if w and w not in seen:
                    seen.add(w)
                    words.append(w)
            self.sensitive_words = words
            self.save_settings()
            win.destroy()
            if not words:
                messagebox.showinfo("提示", "词表为空，未执行检查")
                return
            self._run_sensitive_check(target_files, words)

        btn_bar = ttk.Frame(win, style="Page.TFrame")
        btn_bar.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(btn_bar, text="从文件导入", command=import_words).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_bar, text="开始检查", command=confirm, style="Primary.TButton").pack(side=tk.RIGHT, padx=3)
        ttk.Button(btn_bar, text="取消", command=win.destroy).pack(side=tk.RIGHT, padx=3)

    def _run_sensitive_check(self, target_files, keywords):
        """后台执行敏感词定位，完成后通过回调打开结果窗口"""
        self._task_done_callback = lambda: self._show_sensitive_result(self._sensitive_result, keywords)

        def worker():
            q = self.task_queue
            results = []
            for idx, file_path in enumerate(target_files):
                try:
                    content = self.file_contents.get(file_path, "")
                    hits = find_sensitive_hits(content, keywords)
                    results.append((os.path.basename(file_path),
                                    summarize_sensitive_hits(hits, keywords)))
                except Exception as e:
                    q.put(("error", f"{os.path.basename(file_path)}：{str(e)}"))
                q.put(("progress", (idx + 1) * 100 / len(target_files)))

            q.put(("progress", 0))
            self._sensitive_result = results
            q.put(("status", f"敏感词检查完成 | {len(target_files)} 个文件 | 结果见弹窗"))
            q.put(("done_msg", "检查完成，结果窗口即将打开"))

        self._start_task(worker, done_title="敏感词检查")

    def _show_sensitive_result(self, results, keywords):
        """弹出敏感词检查结果窗口（主线程）"""
        if not results:
            return
        report = format_sensitive_report(results, keywords)
        win = tk.Toplevel(self.root)
        win.title("敏感词检查结果")
        win.geometry("640x520")
        win.configure(bg=COLOR_CARD)
        win.transient(self.root)

        result_text = tk.Text(win, wrap=tk.WORD)
        self._style_input_widget(result_text, font=self.listbox_font)
        scrollbar = ttk.Scrollbar(win, command=result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        result_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        result_text.config(yscrollcommand=scrollbar.set)
        result_text.insert("1.0", report)

        def copy_all():
            self.root.clipboard_clear()
            self.root.clipboard_append(report)
            self.status_var.set("敏感词检查报告已复制到剪贴板")

        def save_to_file():
            path = filedialog.asksaveasfilename(
                title="保存检查报告",
                defaultextension=".txt",
                filetypes=[("纯文本文件", "*.txt"), ("所有文件", "*.*")])
            if not path:
                return
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(report)
                self.status_var.set(f"检查报告已保存：{os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{str(e)}")

        btn_bar = ttk.Frame(win)
        btn_bar.pack(fill=tk.X, padx=6, pady=(0, 6))
        ttk.Button(btn_bar, text="复制全部", command=copy_all, style="Primary.TButton").pack(side=tk.LEFT, padx=3, pady=3)
        ttk.Button(btn_bar, text="保存为文件", command=save_to_file).pack(side=tk.LEFT, padx=3, pady=3)

    # ------------------------------ 保存与统计功能 ------------------------------
    def count_text_words(self):
        """统计当前显示文本的字数"""
        current_text = self.text_area.get("1.0", "end-1c")
        if not current_text.strip():
            messagebox.showinfo("提示", "无文本可统计")
            return

        # 过滤多文件视图的文件分隔符行
        clean_text = re.sub(r"^=+ .+ =+$", "", current_text, flags=re.M)

        total_chars = len(clean_text)
        chars_no_space = len(re.sub(r"\s", "", clean_text))
        cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", clean_text))
        line_count = len(clean_text.split("\n"))
        nonempty_lines = sum(1 for line in clean_text.split("\n") if line.strip())
        word_count = len(clean_text.split())

        stats_message = f"""字数统计结果：
━━━━━━━━━━━━━━━━━━━━
总字符数（含空格/换行）：{total_chars}
纯字符数（不含空白）：{chars_no_space}
中文字符数：{cjk_chars}
总行数：{line_count}
非空行数：{nonempty_lines}
单词数（按空白分割）：{word_count}
━━━━━━━━━━━━━━━━━━━━
提示：已过滤文件分隔符，仅统计文本内容"""

        messagebox.showinfo("字数统计", stats_message)

    def _newline_mode(self):
        """换行符选项 -> open() 的 newline 参数（None 表示系统默认）"""
        return {"默认": None, "LF (Unix)": "\n", "CRLF (Windows)": "\r\n"}.get(
            self.newline_var.get(), None)

    def generate_report(self):
        """为选中（或全部）文件生成单文件 HTML 可视化统计报告（后台线程执行）"""
        if self._busy_guard():
            return
        target_files = self._select_target_files("生成报告")
        if not target_files:
            return
        if len(target_files) == 1:
            default_name = os.path.splitext(os.path.basename(target_files[0]))[0] + "_报告.html"
        else:
            default_name = "批量统计报告.html"
        out_path = filedialog.asksaveasfilename(
            title="保存统计报告", defaultextension=".html", initialfile=default_name,
            filetypes=[("HTML 报告", "*.html"), ("所有文件", "*.*")])
        if not out_path:
            return
        names_raw = simpledialog.askstring(
            "人物追踪", "输入要统计出场次数的人名（逗号分隔，留空跳过）：", parent=self.root)
        names = [n.strip() for n in (names_raw or "").replace("，", ",").split(",") if n.strip()]
        pattern = re.compile(_CHAPTER_PRESETS["第X章+序章/楔子/番外"])

        def worker():
            q = self.task_queue
            out_ext = os.path.splitext(out_path)[1] or ".html"
            out_dir = os.path.dirname(out_path)
            done = 0
            for idx, file_path in enumerate(target_files):
                try:
                    content = self.file_contents.get(file_path, "")
                    stem = os.path.splitext(os.path.basename(file_path))[0]
                    report = build_text_report(content, stem, pattern, names=names)
                    if len(target_files) == 1:
                        out = out_path
                    else:
                        out = os.path.join(out_dir, f"{stem}_报告{out_ext}")
                    with open(out, "w", encoding="utf-8") as f:
                        f.write(report)
                    done += 1
                    q.put(("status", f"已生成报告：{os.path.basename(out)}"))
                except Exception as e:
                    q.put(("error", f"{os.path.basename(file_path)}：{str(e)}"))
                q.put(("progress", (idx + 1) * 100 / len(target_files)))

            q.put(("progress", 0))
            q.put(("status", f"统计报告完成 | 成功 {done}/{len(target_files)} 份"))
            q.put(("done_msg", f"已生成 {done} 份 HTML 报告\n浏览器直接打开即可查看"))

        self._start_task(worker)

    def save_to_original_files(self):
        """保存处理后的内容到原文件（覆盖，自动生成一次 .bak 备份，后台线程执行）"""
        if self._busy_guard():
            return
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            if not messagebox.askyesno("确认", "未选择文件，是否保存所有已加载文件？（会覆盖原文件！）"):
                return
            target_files = self.file_list.copy()
        else:
            target_files = [self.file_list[idx] for idx in selected_indices]

        if not target_files:
            messagebox.showinfo("提示", "没有文件可保存")
            return

        # 二次确认（防止误操作）
        tip = "\n\n首次保存时将自动为每个文件生成 .bak 备份。"
        if len(self.current_view_files) > 1:
            tip = "\n\n注意：当前是多文件视图，视图中的编辑不会写回原文件。" + tip
        confirm = messagebox.askyesno(
            "危险确认",
            f"确定要覆盖 {len(target_files)} 个原文件吗？\n此操作不可恢复！{tip}"
        )
        if not confirm:
            return

        # 默认编码与换行符需在主线程预先求值（Tk 变量不能在后台线程访问）
        default_encode = self._display_to_codec(self.encode_var.get())
        newline = self._newline_mode()

        def worker():
            q = self.task_queue
            success_count = 0
            step = 100 / len(target_files)

            for idx, file_path in enumerate(target_files):
                try:
                    encode = self.file_encodings.get(file_path, default_encode)

                    # 生成一次 .bak 备份（按字节复制，原样保留原始内容与换行）
                    backup_path = file_path + ".bak"
                    if not os.path.exists(backup_path):
                        with open(file_path, "rb") as src, open(backup_path, "wb") as dst:
                            dst.write(src.read())

                    with open(file_path, "w", encoding=encode, newline=newline) as f:
                        f.write(self.file_contents.get(file_path, ""))
                    success_count += 1
                except Exception as e:
                    q.put(("error", f"保存 {os.path.basename(file_path)} 失败：{str(e)}"))

                q.put(("progress", (idx + 1) * step))

            q.put(("progress", 0))
            q.put(("status", f"保存完成 | 成功 {success_count}/{len(target_files)} 个文件 | 原文件已覆盖（含 .bak 备份）"))
            q.put(("done_msg", f"成功保存 {success_count} 个文件\n原文件已被覆盖"))

        self._start_task(worker)

    def save_as_new_file(self):
        """将当前编辑区的内容另存为新文件"""
        if self._busy_guard():
            return
        current_text = self.text_area.get("1.0", "end-1c")
        if not current_text.strip():
            messagebox.showinfo("提示", "无文本可保存")
            return

        file_path = filedialog.asksaveasfilename(
            title="另存为新文件",
            defaultextension=".txt",
            filetypes=[("纯文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if not file_path:
            return

        try:
            encode = self._display_to_codec(self.encode_var.get())
            with open(file_path, "w", encoding=encode, newline=self._newline_mode()) as f:
                f.write(current_text)

            # 将新文件添加到列表
            if file_path not in self.file_list:
                self.file_list.append(file_path)
                self.file_listbox.insert(tk.END, os.path.basename(file_path))
                self.file_contents[file_path] = current_text
                self.file_encodings[file_path] = encode

            self.status_var.set(f"已另存为新文件：{os.path.basename(file_path)}")
            messagebox.showinfo("成功", f"文件已保存到：\n{file_path}")

        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")

    # ------------------------------ 查找替换 ------------------------------
    @staticmethod
    def _offset_to_index(text, offset):
        """字符偏移量 -> Tk Text 索引（文本内容与编辑框一致，不含末尾自动换行）"""
        line = text.count("\n", 0, offset)
        last_nl = text.rfind("\n", 0, offset)
        col = offset if last_nl == -1 else offset - last_nl - 1
        return f"{line + 1}.{col}"

    @staticmethod
    def _index_to_offset(text, index_str):
        """Tk Text 索引 -> 字符偏移量"""
        line_str, col_str = str(index_str).split(".")
        line, col = int(line_str), int(col_str)
        lines = text.split("\n")
        return sum(len(l) + 1 for l in lines[:line - 1]) + col

    def _build_find_pattern(self):
        """根据当前选项构建编译好的正则。无效时弹窗并返回 None。"""
        find_str = self.find_entry.get()
        if not find_str:
            return None
        flags = 0 if self.case_sensitive_var.get() else re.IGNORECASE
        if self.use_regex_var.get():
            pattern = find_str
        else:
            pattern = re.escape(find_str)
            if self.whole_word_var.get():
                pattern = r"\b" + pattern + r"\b"
        try:
            return re.compile(pattern, flags)
        except re.error as e:
            messagebox.showerror("错误", f"表达式无效：{str(e)}")
            return None

    def _get_replacement(self):
        """获取替换串：非正则模式下按字面替换（避免 \1 等被解释）"""
        replace_str = self.replace_entry.get()
        if self.use_regex_var.get():
            return replace_str
        return lambda m: replace_str

    def find_next(self):
        """查找下一个匹配项（从上次位置继续，找不到时循环到开头）"""
        compiled = self._build_find_pattern()
        if compiled is None:
            messagebox.showinfo("提示", "请输入要查找的内容")
            return

        text = self.preview_text.get("1.0", "end-1c")
        if not text:
            return

        pos = self.last_find_pos if self.last_find_pos <= len(text) else 0
        match = compiled.search(text, pos)
        if match is None:
            match = compiled.search(text, 0)  # 循环到开头再找
            if match is None:
                messagebox.showinfo("提示", f"找不到 '{self.find_entry.get()}'")
                self.last_find_pos = 0
                return

        self.preview_text.tag_remove("search", "1.0", tk.END)
        start_idx = self._offset_to_index(text, match.start())
        end_idx = self._offset_to_index(text, match.end())
        self.preview_text.tag_add("search", start_idx, end_idx)
        self.preview_text.tag_config("search", background="yellow", foreground="black")
        self.preview_text.mark_set(tk.INSERT, end_idx)
        self.preview_text.see(end_idx)

        # 零宽匹配时前进一格，避免原地循环
        self.last_find_pos = match.end() if match.end() > match.start() else match.end() + 1
        self.status_var.set(f"找到匹配项（第 {text[:match.start()].count(chr(10)) + 1} 行）")

    def replace_current(self):
        """替换当前高亮的匹配项，并继续查找下一个"""
        ranges = self.preview_text.tag_ranges("search")
        if not ranges:
            self.find_next()
            return

        replace_str = self.replace_entry.get()
        text_before = self.preview_text.get("1.0", "end-1c")
        start_offset = self._index_to_offset(text_before, ranges[0])

        self.preview_text.delete(ranges[0], ranges[1])
        self.preview_text.insert(ranges[0], replace_str)
        self.preview_text.tag_remove("search", "1.0", tk.END)

        # 替换后从替换内容之后继续查找
        self.last_find_pos = start_offset + len(replace_str)
        self.find_next()

    def replace_all_in_preview(self):
        """替换预览区的所有匹配项"""
        compiled = self._build_find_pattern()
        if compiled is None:
            messagebox.showinfo("提示", "请输入要查找的内容")
            return

        text = self.preview_text.get("1.0", "end-1c")
        try:
            new_text, count = compiled.subn(self._get_replacement(), text)
        except re.error as e:
            messagebox.showerror("错误", f"替换失败：{str(e)}")
            return

        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", new_text)
        self.preview_text.tag_remove("search", "1.0", tk.END)
        self.last_find_pos = 0
        self.status_var.set(f"已替换 {count} 处匹配")

    def mark_all_matches(self):
        """在预览区一次性高亮所有匹配项（上限 5000 处，防止超大文本卡界面）"""
        compiled = self._build_find_pattern()
        if compiled is None:
            messagebox.showinfo("提示", "请输入要查找的内容")
            return

        text = self.preview_text.get("1.0", "end-1c")
        if not text:
            return

        self.preview_text.tag_remove("mark_all", "1.0", tk.END)
        count = 0
        for m in compiled.finditer(text):
            if m.end() == m.start():
                continue  # 跳过零宽匹配
            if count >= 5000:
                break
            start_idx = self._offset_to_index(text, m.start())
            end_idx = self._offset_to_index(text, m.end())
            self.preview_text.tag_add("mark_all", start_idx, end_idx)
            count += 1
        self.preview_text.tag_config("mark_all", background="#FDE68A")
        if count >= 5000:
            self.status_var.set(f"已标记 5000 处匹配（达到上限，后续匹配未标记）")
        else:
            self.status_var.set(f"已标记 {count} 处匹配")

    def batch_replace_files(self):
        """批量替换选中（或全部）文件缓存中的匹配项（后台线程执行，仅修改内存）"""
        if self._busy_guard():
            return
        compiled = self._build_find_pattern()
        if compiled is None:
            messagebox.showinfo("提示", "请输入要查找的内容")
            return

        selected_indices = self.file_listbox.curselection()
        if selected_indices:
            target_files = [self.file_list[idx] for idx in selected_indices]
        else:
            if not self.file_list:
                messagebox.showinfo("提示", "请先添加文件")
                return
            target_files = self.file_list.copy()

        replacement = self._get_replacement()
        self._push_undo("批量替换", target_files)

        def worker():
            q = self.task_queue
            total_replaced = 0
            files_hit = 0
            step = 100 / len(target_files)

            for i, file_path in enumerate(target_files):
                try:
                    content = self.file_contents.get(file_path, "")
                    new_content, count = compiled.subn(replacement, content)
                    if count:
                        self.file_contents[file_path] = new_content
                        total_replaced += count
                        files_hit += 1
                except re.error as e:
                    q.put(("error", f"处理文件 {os.path.basename(file_path)} 时出错：{str(e)}"))

                q.put(("progress", (i + 1) * step))

            q.put(("progress", 0))
            q.put(("status", f"批量替换完成 | {files_hit}/{len(target_files)} 个文件命中 | "
                             f"共替换 {total_replaced} 处（仅修改内存，需手动保存）"))
            q.put(("done_msg", f"{files_hit}/{len(target_files)} 个文件命中\n共替换 {total_replaced} 处匹配"))

        self._start_task(worker)

    def load_text_from_file(self):
        """从文件加载文本到预览区"""
        file_path = filedialog.askopenfilename(
            title="选择文本文件",
            filetypes=[("纯文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if not file_path:
            return
        try:
            content, _ = self._read_text(file_path, self.encode_var.get())
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert("1.0", content)
            self.last_find_pos = 0
            self.status_var.set(f"已加载文件：{os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"加载文件失败：{str(e)}")

    def load_from_editor(self):
        """把文件处理页编辑区的内容载入预览区"""
        content = self.text_area.get("1.0", "end-1c")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", content)
        self.last_find_pos = 0
        self.status_var.set("已载入编辑区内容")

    def clear_find_replace(self):
        """清空查找替换区域"""
        self.find_entry.delete(0, tk.END)
        self.replace_entry.delete(0, tk.END)
        self.preview_text.delete("1.0", tk.END)
        self.last_find_pos = 0
        self.status_var.set("查找替换区域已清空")


# ------------------------------ 命令行模式 ------------------------------
# 不启动界面，便于脚本化批量处理；不带参数运行仍是图形界面
_CLI_COMMANDS = {"split", "epub", "docx", "epub2txt", "dedup", "sort",
                 "adfilter", "convert", "stats", "hex", "diff", "version", "sensitive"}


def _cli_inplace_write(path, content, encode):
    """覆盖写回原文件（首次自动按字节生成 .bak 备份）"""
    backup = path + ".bak"
    if not os.path.exists(backup):
        with open(path, "rb") as src, open(backup, "wb") as dst:
            dst.write(src.read())
    with open(path, "w", encoding=encode, newline="") as f:
        f.write(content)


def _cli_split_content(content, preset, custom):
    """CLI 按规则名或自定义正则得到章节块"""
    if custom:
        pattern = re.compile(custom)
    else:
        pattern = re.compile(_CHAPTER_PRESETS[preset])
    return split_chapters_by_pattern(content, pattern)


def _cli_cmd_split(args):
    total = 0
    for path in args.files:
        content, enc = read_text_smart(path, args.encoding)
        stem = os.path.splitext(os.path.basename(path))[0]
        outdir = args.outdir or (stem + "_章节")
        os.makedirs(outdir, exist_ok=True)
        blocks = _cli_split_content(content, args.preset, args.pattern)
        if not any(t is not None for t, _ in blocks):
            print(f"[跳过] {path}：未识别到章节标题", file=sys.stderr)
            continue
        entries = []
        seq = 0
        for title, body in blocks:
            text = body.strip()
            if title is None:
                if not text:
                    continue
                fname = f"{stem}_00_开头.txt"
                write_text = text
            else:
                seq += 1
                safe_title = re.sub(r'[\\/:*?"<>|\s]+', "_", title)
                fname = f"{stem}_{seq:03d}_{safe_title}.txt"
                write_text = f"{title}\n\n{text}"
            with open(os.path.join(outdir, fname), "w", encoding=enc, newline="") as f:
                f.write(write_text)
            entries.append(f"{fname}  （{len(text)} 字）")
            total += 1
        with open(os.path.join(outdir, "章节索引.txt"), "w", encoding=enc, newline="") as f:
            f.write(f"《{stem}》共 {len(entries)} 个文件\n\n" + "\n".join(entries))
        print(f"[完成] {path} -> {outdir}/（{len(entries)} 个文件 + 章节索引）")
    print(f"共分割出 {total} 个章节文件")
    return 0


def _cli_cmd_epub(args):
    content, _ = read_text_smart(args.file, args.encoding)
    stem = os.path.splitext(os.path.basename(args.file))[0]
    blocks = _cli_split_content(content, args.preset, args.pattern)
    chapters = [("前言", b) if t is None else (t, b) for t, b in blocks if b.strip()]
    if not chapters:
        print("错误：内容为空", file=sys.stderr)
        return 1
    cover_bytes, cover_ext = None, ".jpg"
    if args.cover:
        ext = os.path.splitext(args.cover)[1].lower()
        if ext not in _COVER_MEDIA_TYPES:
            print("错误：封面仅支持 jpg / png / gif", file=sys.stderr)
            return 1
        with open(args.cover, "rb") as f:
            cover_bytes = f.read()
        cover_ext = ext
    build_epub(args.out, args.title or stem, chapters, author=args.author,
               cover=cover_bytes, cover_ext=cover_ext)
    print(f"已导出 EPUB：{args.out}（{len(chapters)} 章）")
    return 0


def _cli_cmd_dedup(args):
    pattern = re.compile(_CHAPTER_PRESETS["第X章+序章/楔子/番外"])
    for path in args.files:
        content, enc = read_text_smart(path, args.encoding)
        blocks = split_chapters_by_pattern(content, pattern)
        if sum(1 for t, _ in blocks if t is not None) < 2:
            print(f"[跳过] {path}：未识别到章节（或仅一章）", file=sys.stderr)
            continue
        kept, removed = dedup_chapter_blocks(blocks)
        if not removed:
            print(f"[无变化] {path}：未发现重复章节", file=sys.stderr)
            continue
        new_content = rebuild_text_from_blocks(kept)
        if args.in_place:
            _cli_inplace_write(path, new_content, enc)
            print(f"[完成] {path}：剔除 {len(removed)} 章（已写回，原文件备份为 .bak）")
        else:
            print(new_content)
    return 0


def _cli_cmd_sort(args):
    pattern = re.compile(_CHAPTER_PRESETS["第X章+序章/楔子/番外"])
    for path in args.files:
        content, enc = read_text_smart(path, args.encoding)
        blocks = split_chapters_by_pattern(content, pattern)
        if sum(1 for t, _ in blocks if t is not None) < 2:
            print(f"[跳过] {path}：未识别到章节（或仅一章）", file=sys.stderr)
            continue
        ordered = sort_chapter_blocks(blocks)
        if ordered == blocks:
            print(f"[无变化] {path}：章节顺序已正确", file=sys.stderr)
            continue
        new_content = rebuild_text_from_blocks(ordered)
        if args.in_place:
            _cli_inplace_write(path, new_content, enc)
            print(f"[完成] {path}：章节已按编号重排（已写回，原文件备份为 .bak）")
        else:
            print(new_content)
    return 0


def _cli_cmd_adfilter(args):
    words_content, _ = read_text_smart(args.words_file, "utf-8")
    keywords = sorted({w.strip() for w in words_content.splitlines() if w.strip()})
    if not keywords:
        print("错误：关键词文件为空", file=sys.stderr)
        return 1
    for path in args.files:
        content, enc = read_text_smart(path, args.encoding)
        new_content, removed = filter_ad_lines(content, keywords, args.whole_line)
        if not removed:
            print(f"[无变化] {path}：未命中任何关键词", file=sys.stderr)
            continue
        if args.in_place:
            _cli_inplace_write(path, new_content, enc)
            print(f"[完成] {path}：删除 {removed} 行（已写回，原文件备份为 .bak）")
        else:
            print(new_content)
    return 0


def _cli_cmd_convert(args):
    for path in args.files:
        size = os.path.getsize(path)
        target = display_to_codec(args.to)
        if size > _STREAM_THRESHOLD:
            # 大文件流式转码，内存占用恒定
            src_enc = _detect_source_encoding(path)
            if args.in_place:
                if not os.path.exists(path + ".bak"):
                    with open(path, "rb") as src, open(path + ".bak", "wb") as dst:
                        dst.write(src.read())
                tmp = path + ".converting"
                src_enc, replaced = convert_file_stream(path, tmp, target)
                os.replace(tmp, path)
            else:
                outdir = args.outdir or "."
                os.makedirs(outdir, exist_ok=True)
                out_path = os.path.join(outdir, os.path.basename(path))
                src_enc, replaced = convert_file_stream(path, out_path, target)
            note = "（含无法解码字节，已用 U+FFFD 替换）" if replaced else ""
            print(f"[完成] {path}：流式转码 {src_enc} -> {args.to}{note}")
            continue
        content, src_enc = read_text_smart(path, "utf-8")  # 源编码智能探测
        if args.in_place:
            _cli_inplace_write(path, content, target)
        else:
            outdir = args.outdir or "."
            os.makedirs(outdir, exist_ok=True)
            out_path = os.path.join(outdir, os.path.basename(path))
            with open(out_path, "w", encoding=target, newline="") as f:
                f.write(content)
        print(f"[完成] {path}：{src_enc} -> {args.to}")
    return 0


def _cli_cmd_version(args):
    print(f"全能TXT文本处理器 {_APP_VERSION}")
    if args.check:
        try:
            tag, url = check_update_from_github()
        except Exception as e:
            print(f"检查更新失败：{e}", file=sys.stderr)
            return 1
        if version_tuple(tag) > version_tuple(_APP_VERSION):
            print(f"发现新版本：{tag}\n{url}")
        else:
            print("已是最新版本")
    return 0


def _cli_cmd_stats(args):
    content, _ = read_text_smart(args.file, args.encoding)
    stem = os.path.splitext(os.path.basename(args.file))[0]
    pattern = (re.compile(args.pattern) if args.pattern
               else re.compile(_CHAPTER_PRESETS[args.preset]))
    if args.out:
        report = build_text_report(content, stem, pattern)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"已生成 HTML 报告：{args.out}")
        return 0
    blocks = split_chapters_by_pattern(content, pattern)
    stats = compute_text_stats(content)
    stats["chapters"] = sum(1 for t, _ in blocks if t is not None)
    print(json.dumps({"file": os.path.basename(args.file), "title": stem, **stats},
                     ensure_ascii=False, indent=2))
    return 0


def _cli_cmd_hex(args):
    with open(args.file, "rb") as f:
        data = f.read(args.bytes)
    full_size = os.path.getsize(args.file)
    print(f"文件：{args.file} · {full_size:,} 字节")
    print(f"编码体检：{'；'.join(detect_encoding_hints(data))}")
    if full_size > args.bytes:
        print(f"（仅显示前 {args.bytes:,} 字节）")
    print(hex_dump(data))
    return 0


def _cli_cmd_diff(args):
    text_a, _ = read_text_smart(args.file_a, args.encoding)
    text_b, _ = read_text_smart(args.file_b, args.encoding)
    if args.out:
        report = unified_diff_html(os.path.basename(args.file_a),
                                   os.path.basename(args.file_b), text_a, text_b)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"已生成对比报告：{args.out}")
        return 0
    diff_lines = difflib.unified_diff(
        text_a.splitlines(), text_b.splitlines(),
        fromfile=args.file_a, tofile=args.file_b, lineterm="")
    for line in diff_lines:
        print(line)
    return 0


def _cli_cmd_docx(args):
    content, _ = read_text_smart(args.file, args.encoding)
    stem = os.path.splitext(os.path.basename(args.file))[0]
    blocks = _cli_split_content(content, args.preset, args.pattern)
    chapters = [("前言", b) if t is None else (t, b) for t, b in blocks if b.strip()]
    if not chapters:
        print("错误：内容为空", file=sys.stderr)
        return 1
    build_docx(args.out, args.title or stem, chapters, author=args.author)
    print(f"已导出 DOCX：{args.out}（{len(chapters)} 章）")
    return 0


def _cli_cmd_epub2txt(args):
    title, chapters = extract_text_from_epub(args.file)
    text = chapters_to_txt(chapters)
    if not text.strip():
        print("错误：未从 EPUB 中提取到文本", file=sys.stderr)
        return 1
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"已导入 EPUB：《{title}》共 {len(chapters)} 章 -> {args.out}")
    return 0


def _cli_cmd_sensitive(args):
    words_content, _ = read_text_smart(args.words_file, "utf-8")
    keywords = list(dict.fromkeys(w.strip() for w in words_content.splitlines() if w.strip()))
    if not keywords:
        print("错误：词表为空", file=sys.stderr)
        return 1
    results = []
    for path in args.files:
        content, _ = read_text_smart(path, args.encoding)
        hits = find_sensitive_hits(content, keywords)
        results.append((os.path.basename(path), summarize_sensitive_hits(hits, keywords)))
    report = format_sensitive_report(results, keywords)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"已生成敏感词检查报告：{args.out}")
    else:
        print(report)
    return 0


def build_cli_parser():
    parser = argparse.ArgumentParser(
        prog="全能TXT文本处理器",
        description="命令行批量处理模式（不带参数运行则启动图形界面）")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("split", help="按章节标题分割为独立文件 + 章节索引")
    p.add_argument("files", nargs="+", help="TXT 文件")
    p.add_argument("--preset", default="第X章+序章/楔子/番外",
                   choices=list(_CHAPTER_PRESETS), help="内置章节规则（默认：第X章+序章/楔子/番外）")
    p.add_argument("--pattern", default=None, help="自定义章节标题正则（优先于 --preset）")
    p.add_argument("--outdir", default=None, help="输出目录（默认：<文件名>_章节/）")
    p.add_argument("--encoding", default="utf-8", help="读取编码（默认 utf-8，自动探测兜底）")
    p.set_defaults(func=_cli_cmd_split)

    p = sub.add_parser("epub", help="导出 EPUB3 电子书")
    p.add_argument("file", help="TXT 文件")
    p.add_argument("--out", required=True, help="输出的 .epub 路径")
    p.add_argument("--title", default=None, help="书名（默认用文件名）")
    p.add_argument("--author", default="", help="作者名")
    p.add_argument("--cover", default=None, help="封面图片（jpg/png/gif）")
    p.add_argument("--preset", default="第X章+序章/楔子/番外",
                   choices=list(_CHAPTER_PRESETS), help="内置章节规则")
    p.add_argument("--pattern", default=None, help="自定义章节标题正则（优先于 --preset）")
    p.add_argument("--encoding", default="utf-8")
    p.set_defaults(func=_cli_cmd_epub)

    p = sub.add_parser("dedup", help="章节去重（默认输出到 stdout，--in-place 写回）")
    p.add_argument("files", nargs="+")
    p.add_argument("--in-place", action="store_true", help="覆盖原文件（自动 .bak 备份）")
    p.add_argument("--encoding", default="utf-8")
    p.set_defaults(func=_cli_cmd_dedup)

    p = sub.add_parser("sort", help="章节按编号重排（默认输出到 stdout，--in-place 写回）")
    p.add_argument("files", nargs="+")
    p.add_argument("--in-place", action="store_true")
    p.add_argument("--encoding", default="utf-8")
    p.set_defaults(func=_cli_cmd_sort)

    p = sub.add_parser("adfilter", help="删除包含关键词的行（默认输出到 stdout，--in-place 写回）")
    p.add_argument("files", nargs="+")
    p.add_argument("--words-file", required=True, help="关键词文件（每行一个，UTF-8）")
    p.add_argument("--whole-line", action="store_true", help="整行完全匹配才删除")
    p.add_argument("--in-place", action="store_true")
    p.add_argument("--encoding", default="utf-8")
    p.set_defaults(func=_cli_cmd_adfilter)

    p = sub.add_parser("convert", help="编码转换（源编码自动探测）")
    p.add_argument("files", nargs="+")
    p.add_argument("--to", default="utf-8",
                   choices=["utf-8", "gbk", "gb2312", "utf-16", "ansi"], help="目标编码")
    p.add_argument("--outdir", default=None, help="输出目录（缺省当前目录；--in-place 时忽略）")
    p.add_argument("--in-place", action="store_true", help="覆盖原文件（自动 .bak 备份）")
    p.set_defaults(func=_cli_cmd_convert)

    p = sub.add_parser("stats", help="文本统计：默认打印 JSON 概览，--out 生成 HTML 可视化报告")
    p.add_argument("file", help="TXT 文件")
    p.add_argument("--out", default=None, help="输出 HTML 报告路径（缺省打印 JSON）")
    p.add_argument("--preset", default="第X章+序章/楔子/番外",
                   choices=list(_CHAPTER_PRESETS), help="章节规则（影响章节数统计）")
    p.add_argument("--pattern", default=None, help="自定义章节标题正则（优先于 --preset）")
    p.add_argument("--encoding", default="utf-8")
    p.set_defaults(func=_cli_cmd_stats)

    p = sub.add_parser("hex", help="十六进制查看文件开头字节 + 编码体检（排查乱码）")
    p.add_argument("file")
    p.add_argument("--bytes", type=int, default=4096, help="显示前多少字节（默认 4096）")
    p.set_defaults(func=_cli_cmd_hex)

    p = sub.add_parser("diff", help="对比两个文件的文本差异（默认 stdout，--out 生成 HTML 报告）")
    p.add_argument("file_a")
    p.add_argument("file_b")
    p.add_argument("--out", default=None, help="输出彩色 HTML 对比报告路径")
    p.add_argument("--encoding", default="utf-8")
    p.set_defaults(func=_cli_cmd_diff)

    p = sub.add_parser("version", help="显示版本号（--check 联网检查更新）")
    p.add_argument("--check", action="store_true", help="联网查询 GitHub 最新 Release")
    p.set_defaults(func=_cli_cmd_version)

    p = sub.add_parser("docx", help="导出 Word 文档（.docx）")
    p.add_argument("file", help="TXT 文件")
    p.add_argument("--out", required=True, help="输出的 .docx 路径")
    p.add_argument("--title", default=None, help="书名（默认用文件名）")
    p.add_argument("--author", default="", help="作者名")
    p.add_argument("--preset", default="第X章+序章/楔子/番外",
                   choices=list(_CHAPTER_PRESETS), help="内置章节规则")
    p.add_argument("--pattern", default=None, help="自定义章节标题正则（优先于 --preset）")
    p.add_argument("--encoding", default="utf-8")
    p.set_defaults(func=_cli_cmd_docx)

    p = sub.add_parser("epub2txt", help="EPUB 电子书反向导入为 TXT")
    p.add_argument("file", help=".epub 文件")
    p.add_argument("--out", required=True, help="输出的 .txt 路径（UTF-8）")
    p.set_defaults(func=_cli_cmd_epub2txt)

    p = sub.add_parser("sensitive", help="敏感词检查：定位包含敏感词的行（只读不改内容）")
    p.add_argument("files", nargs="+", help="TXT 文件")
    p.add_argument("--words-file", required=True, help="词表文件（每行一个，UTF-8）")
    p.add_argument("--out", default=None, help="输出检查报告路径（缺省打印到 stdout）")
    p.add_argument("--encoding", default="utf-8")
    p.set_defaults(func=_cli_cmd_sensitive)

    return parser


def cli_main(argv=None):
    """命令行入口。返回退出码。"""
    args = build_cli_parser().parse_args(argv)
    # 控制台输出容错：GBK 控制台遇到生僻字不崩
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    try:
        return args.func(args)
    except BrokenPipeError:
        return 0
    except Exception as e:
        print(f"错误：{e}", file=sys.stderr)
        return 1


# ------------------------------ 程序入口 ------------------------------
if __name__ == "__main__":
    # 带子命令或任意选项参数（如 --help）进入命令行模式；不带参数启动图形界面
    if len(sys.argv) > 1 and (sys.argv[1] in _CLI_COMMANDS or sys.argv[1].startswith("-")):
        sys.exit(cli_main())
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    app = TextProcessorApp(root)
    root.mainloop()
