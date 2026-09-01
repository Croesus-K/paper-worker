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

所有处理仅修改内存，需手动"保存到原文件"或"另存为新文件"才会写盘。
运行依赖：tkinterdnd2（可选，pip install tkinterdnd2，用于拖放）
"""

import difflib
import json
import os
import queue
import re
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

# 默认窗口标题
DEFAULT_TITLE = "全能TXT文本处理器 2.3"

# ------------------------------ 界面主题配色（扁平化浅色主题） ------------------------------
COLOR_BG        = "#EEF1F5"   # 页面背景
COLOR_CARD      = "#FFFFFF"   # 卡片背景
COLOR_BORDER    = "#D9DEE7"   # 边框
COLOR_PRIMARY   = "#2563EB"   # 主色（标题栏/主按钮/选中）
COLOR_PRIMARY_D = "#1D4ED8"   # 主色（悬停加深）
COLOR_PRIMARY_L = "#DBEAFE"   # 主色浅（列表选中背景）
COLOR_TEXT      = "#1F2937"   # 主文字
COLOR_MUTED     = "#6B7280"   # 次要文字
COLOR_DISABLE   = "#9CA3AF"   # 禁用文字

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


class TextProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(DEFAULT_TITLE)
        self.root.geometry("1240x860")
        self.root.resizable(True, True)

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
        self.newline_var = tk.StringVar(value="默认")  # 保存时的换行符模式

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
           background=[("pressed", "#E5E7EB"), ("active", "#F3F4F6"), ("disabled", "#F9FAFB")],
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
        cfg("TScrollbar", background="#CBD5E1", troughcolor=COLOR_CARD,
            bordercolor=COLOR_CARD, arrowcolor=COLOR_MUTED, relief="flat")
        mp("TScrollbar", background=[("active", "#94A3B8")])
        cfg("TSeparator", background=COLOR_BORDER)

        # 标签页
        cfg("TNotebook", background=COLOR_BG, bordercolor=COLOR_BORDER, tabmargins=(6, 6, 6, 0))
        cfg("TNotebook.Tab", padding=(18, 7), background="#E2E7EF", foreground=COLOR_MUTED,
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
        """当前系统的 ANSI 编码名（Windows 为 mbcs）"""
        return "mbcs" if sys.platform.startswith("win") else "cp1252"

    @classmethod
    def _display_to_codec(cls, display):
        """界面编码显示名 -> 实际 Python 编码名（修复 ansi 不合法的问题）"""
        return cls._system_ansi() if display == "ansi" else display

    def _read_text(self, path, chosen_display):
        """按选定编码读取文件，失败时自动尝试常见备选编码。
        返回 (内容, 实际使用的编码名)，写回时按此编码保存以保持原样。"""
        chosen = self._display_to_codec(chosen_display)
        if chosen in ("utf-8", "utf-8-sig"):
            # utf-8-sig 可同时正确读取带/不带 BOM 的 UTF-8 文件
            candidates = ["utf-8-sig", "gbk", "utf-16", self._system_ansi()]
        else:
            candidates = [chosen, "utf-8-sig", "gbk", "utf-16", self._system_ansi()]
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
        words = settings.get("ad_filter_words")
        if isinstance(words, list):
            self.ad_filter_words = [str(w) for w in words if str(w).strip()]
        self.ad_whole_line = bool(settings.get("ad_whole_line", False))

    def save_settings(self):
        """保存设置（编码、窗口大小、换行符、广告过滤词）"""
        try:
            with open(self._settings_path, "w", encoding="utf-8") as f:
                json.dump({
                    "encoding": self.encode_var.get(),
                    "geometry": self.root.geometry(),
                    "newline_mode": self.newline_var.get(),
                    "ad_filter_words": self.ad_filter_words,
                    "ad_whole_line": self.ad_whole_line,
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
        tk.Label(header_inner, text="v2.3 · 仅修改内存 · 手动保存", bg=COLOR_PRIMARY,
                 fg="#BFDBFE", font=(face, 9)).pack(side=tk.LEFT, padx=(10, 0), pady=(4, 0))
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
        tools_btn_frame.pack(fill=tk.X, pady=6)
        self._action_button(tools_btn_frame, "合并文件", self.merge_files)
        self._action_button(tools_btn_frame, "分割章节", self.split_chapters)
        self._action_button(tools_btn_frame, "批量命名", self.batch_rename)

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
            ("排版", [
                ("合并非标点后换行", lambda: self.process_selected_files(self.merge_unwanted_newlines)),
                ("句号后强制换行", lambda: self.process_selected_files(self.force_newline_after_period)),
                ("段首缩进", lambda: self.process_selected_files(self.add_paragraph_indent)),
                ("去除段首缩进", lambda: self.process_selected_files(self.remove_paragraph_indent)),
            ]),
            ("清理", [
                ("去除空行", lambda: self.process_selected_files(self.remove_empty_lines)),
                ("去除所有空格", lambda: self.process_selected_files(self.remove_all_spaces)),
                ("去除重复行", lambda: self.process_selected_files(self.remove_duplicate_lines)),
                ("去除日期信息", lambda: self.process_selected_files(self.remove_date_info)),
                ("去除HTML标签", lambda: self.process_selected_files(self.strip_html_tags)),
            ]),
            ("小说", [
                ("过滤广告行", self.process_filter_ad_lines),
                ("章节去重", self.process_dedup_chapters),
                ("压缩连续空行", lambda: self.process_selected_files(compress_blank_lines)),
                ("清理行首尾空白", lambda: self.process_selected_files(strip_line_edges)),
            ]),
            ("转换", [
                ("转大写", lambda: self.process_selected_files(self.to_uppercase)),
                ("转小写", lambda: self.process_selected_files(self.to_lowercase)),
                ("全角转半角", lambda: self.process_selected_files(self.fullwidth_to_halfwidth)),
                ("中文标点统一", lambda: self.process_selected_files(self.unify_cjk_punctuation)),
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
        extract_group = ttk.LabelFrame(right_frame, text="内容提取（结果显示在弹出窗口）",
                                       style="Card.TLabelframe")

        extract_btn_frame = ttk.Frame(extract_group)
        extract_btn_frame.pack(fill=tk.X, pady=6, padx=4)
        ttk.Label(extract_btn_frame, text="提取", style="Muted.TLabel", width=5).pack(side=tk.LEFT)
        ttk.Button(extract_btn_frame, text="邮箱", command=self.extract_emails).pack(side=tk.LEFT, padx=3, pady=2)
        ttk.Button(extract_btn_frame, text="URL", command=self.extract_urls).pack(side=tk.LEFT, padx=3, pady=2)
        ttk.Button(extract_btn_frame, text="手机号", command=self.extract_phones).pack(side=tk.LEFT, padx=3, pady=2)

        # 保存与统计组（含进度条）
        save_group = ttk.LabelFrame(right_frame, text="保存与统计", style="Card.TLabelframe")

        btn_frame4 = ttk.Frame(save_group)
        btn_frame4.pack(fill=tk.X, pady=(6, 2), padx=4)
        ttk.Button(btn_frame4, text="统计字数", command=self.count_text_words).pack(side=tk.LEFT, padx=3, pady=2)
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

        # 换行符选项（影响"保存到原文件/另存为新文件"的写盘格式）
        newline_frame = ttk.Frame(save_group)
        newline_frame.pack(fill=tk.X, pady=(2, 8), padx=4)
        ttk.Label(newline_frame, text="换行符", style="Muted.TLabel", width=5).pack(side=tk.LEFT)
        newline_combo = ttk.Combobox(
            newline_frame, textvariable=self.newline_var,
            values=["默认", "LF (Unix)", "CRLF (Windows)"], state="readonly", width=14)
        newline_combo.pack(side=tk.LEFT, padx=3)
        ttk.Label(newline_frame, text="（保存到原文件/另存时生效）",
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

    # ------------------------------ 文本处理核心方法 ------------------------------
    def process_selected_files(self, process_func):
        """批量处理选中的文件（未选中时询问是否处理全部），后台线程执行，仅修改内存"""
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
            lambda t: "\n".join(prefix + line for line in t.splitlines()))

    def process_add_suffix(self):
        """为每一行添加后缀"""
        suffix = simpledialog.askstring("添加后缀", "请输入要添加的后缀:", parent=self.root)
        if suffix is None:
            return
        self.process_selected_files(
            lambda t: "\n".join(line + suffix for line in t.splitlines()))

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
                        rebuilt = "\n\n".join(
                            f"{t}\n\n{b.strip()}" if t is not None else b.strip()
                            for t, b in kept if b.strip())
                        self.file_contents[file_path] = rebuilt
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


# ------------------------------ 程序入口 ------------------------------
if __name__ == "__main__":
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    app = TextProcessorApp(root)
    root.mainloop()
