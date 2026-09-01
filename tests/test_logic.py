# -*- coding: utf-8 -*-
"""纯逻辑单元测试（不启动 GUI）：python tests/test_logic.py"""
import importlib.util
import os
import re
import sys
import unittest

SPEC = importlib.util.spec_from_file_location(
    "processor",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "全能TXT文本处理器.py"))
processor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(processor)

split_by = processor.split_chapters_by_pattern
P = processor._CHAPTER_PRESETS


def compile_preset(name):
    return re.compile(P[name])


class TestSplitChapters(unittest.TestCase):
    def test_basic_split(self):
        text = "前言内容\n第一章 起点\n正文A\n第二章 转折\n正文B"
        blocks = split_by(text, compile_preset("第X章"))
        self.assertEqual(blocks[0], (None, "前言内容"))
        self.assertEqual(len(blocks), 3)
        self.assertEqual(blocks[1][0], "第一章 起点")
        self.assertEqual(blocks[1][1], "正文A")
        self.assertNotIn("第一章", blocks[1][1])

    def test_no_match(self):
        blocks = split_by("没有任何章节标题的文本", compile_preset("第X章"))
        self.assertEqual(blocks, [(None, "没有任何章节标题的文本")])

    def test_broad_preset(self):
        text = "卷前说明\n第一卷 开端\n卷内容\n第十二章 转折\n章内容\n第三回 回目\n回内容"
        blocks = split_by(text, compile_preset("第X章/卷/回/节/集/篇"))
        self.assertEqual(len(blocks), 4)
        self.assertEqual(blocks[0], (None, "卷前说明"))
        self.assertEqual(blocks[2][0], "第十二章 转折")
        # 文本以章节标题开头时，不存在"开头内容"块
        text2 = "第一卷 开端\n卷内容\n第三回 回目\n回内容"
        blocks2 = split_by(text2, compile_preset("第X章/卷/回/节/集/篇"))
        self.assertEqual(len(blocks2), 2)
        self.assertEqual(blocks2[0][0], "第一卷 开端")

    def test_special_chapters(self):
        text = "本书由某某整理\n序章 风起\n序内容\n第一章 起\n内容\n番外1 彩蛋\n番内容"
        blocks = split_by(text, compile_preset("第X章+序章/楔子/番外"))
        titles = [t for t, _ in blocks]
        self.assertEqual(titles, [None, "序章 风起", "第一章 起", "番外1 彩蛋"])

    def test_mid_line_mention_not_matched(self):
        # 正文行中间出现的"第X章"不应被误认为标题
        text = "开头内容\n他说第三章写得好。\n第一章 真·标题\n正文"
        blocks = split_by(text, compile_preset("第X章"))
        self.assertEqual([t for t, _ in blocks], [None, "第一章 真·标题"])

    def test_english_chapter(self):
        text = "Prologue\nChapter 1 Start\nbody\nChapter 2 End\nbody2"
        blocks = split_by(text, compile_preset("Chapter X（英文）"))
        self.assertEqual([t for t, _ in blocks][1:], ["Chapter 1 Start", "Chapter 2 End"])

    def test_custom_regex_with_group(self):
        # 用户自定义正则含捕获组时，finditer 方式仍应正确切分；标题取整行（含副标题）
        text = "开头\n第1章 A\nx\n第2章 B\ny"
        blocks = split_by(text, re.compile(r"(第\d+章)"))
        self.assertEqual(len(blocks), 3)
        self.assertEqual(blocks[0], (None, "开头\n"))
        self.assertEqual(blocks[1][0], "第1章 A")
        self.assertEqual(blocks[1][1], "x\n")

    def test_duplicate_titles_unique_filenames_basis(self):
        text = "第一章 相同\nA内容\n第一章 相同\nB内容"
        blocks = split_by(text, compile_preset("第X章"))
        self.assertEqual(len(blocks), 2)


class TestDedupChapters(unittest.TestCase):
    def test_exact_duplicate_removed(self):
        blocks = [(None, "前言"), ("第一章 A", "正文内容XYZ"), ("第一章 A", "正文内容XYZ"),
                  ("第二章 B", "另一段")]
        kept, removed = processor.dedup_chapter_blocks(blocks)
        self.assertEqual(len(kept), 3)
        self.assertEqual(len(removed), 1)
        self.assertIn("完全重复", removed[0])

    def test_same_title_similar_removed(self):
        a = "这是第一章的正文内容，讲述主角登场的故事，" * 20
        b = a[:-5] + "略有不同的结尾补充"
        blocks = [("第一章 A", a), ("第一章 A", b), ("第二章 B", "完全不同的另一章内容")]
        kept, removed = processor.dedup_chapter_blocks(blocks)
        self.assertEqual(len(kept), 2)
        self.assertEqual(len(removed), 1)
        self.assertIn("相似", removed[0])

    def test_same_title_different_content_kept(self):
        a = "第一章讲的是主角在山中修炼，偶遇机缘，" * 30
        b = "第一章重写版：主角在都市醒来，发现世界大变样，" * 30
        blocks = [("第一章", a), ("第一章", b)]
        kept, removed = processor.dedup_chapter_blocks(blocks)
        self.assertEqual(len(kept), 2)
        self.assertEqual(len(removed), 0)

    def test_order_and_preface_preserved(self):
        blocks = [(None, "开头散落内容"), ("第一章 A", "甲"), ("第二章 B", "乙")]
        kept, removed = processor.dedup_chapter_blocks(blocks)
        self.assertEqual(kept, blocks)
        self.assertEqual(removed, [])


class TestAdFilter(unittest.TestCase):
    def test_contains_mode(self):
        text = "正文第一行\n本章未完点击下一页\n正文第二行\n广告：某某站点\n正文第三行"
        new_text, removed = processor.filter_ad_lines(text, ["点击下一页", "广告："])
        self.assertEqual(removed, 2)
        self.assertNotIn("点击下一页", new_text)
        self.assertIn("正文第二行", new_text)

    def test_whole_line_mode(self):
        text = "正文：请看下一页\n下一页\n尾部"
        new_text, removed = processor.filter_ad_lines(text, ["下一页"], whole_line=True)
        self.assertEqual(removed, 1)
        self.assertIn("请看下一页", new_text)
        self.assertNotIn("\n下一页\n", "\n" + new_text + "\n")

    def test_empty_keywords_noop(self):
        text = "保持\n原样\n"
        new_text, removed = processor.filter_ad_lines(text, ["", "  "])
        self.assertEqual((new_text, removed), (text, 0))

    def test_crlf_normalized(self):
        new_text, removed = processor.filter_ad_lines("a\r\n广告行\r\nb", ["广告"])
        self.assertEqual(removed, 1)
        self.assertNotIn("\r", new_text)


class TestBlankLines(unittest.TestCase):
    def test_compress(self):
        text = "A\n\n\n\n\nB\n   \n\t\nC"
        self.assertEqual(processor.compress_blank_lines(text), "A\n\nB\n\nC")

    def test_leading_blank_removed(self):
        self.assertEqual(processor.compress_blank_lines("\n\n\nA"), "A")

    def test_strip_edges(self):
        self.assertEqual(processor.strip_line_edges("  x　\n\ty \n z"), "x\ny\nz")


class TestChineseNum(unittest.TestCase):
    def test_digits(self):
        for s, n in [("一", 1), ("十", 10), ("二十三", 23), ("一百零三", 103),
                     ("两千零六", 2006), ("一万二千", 12000), ("三万零一十", 30010),
                     ("108", 108), ("两", 2), ("两章", None), ("", None), ("abc", None)]:
            self.assertEqual(processor.chinese_num_to_int(s), n, s)


class TestChapterSort(unittest.TestCase):
    def test_key_order(self):
        key = processor.chapter_sort_key
        self.assertLess(key(None), key("第一章 x"))
        self.assertLess(key("第九章 x"), key("第十章 x"))
        self.assertLess(key("第十章 x"), key("第十一章 x"))
        self.assertLess(key("第十一章 x"), key("第一百零一章 x"))
        self.assertLess(key("第2章"), key("第10章"))
        self.assertLess(key("第九章"), key("Chapter 10"))   # 有编号 > 无编号
        self.assertLess(key("第10章"), key("番外"))          # 无编号排最后

    def test_sort_blocks(self):
        blocks = [("第一章 甲", "a"), (None, "前言"), ("第十二章 转折", "b"),
                  ("第二章 乙", "c"), ("番外1", "d")]
        ordered = processor.sort_chapter_blocks(blocks)
        titles = [t for t, _ in ordered]
        self.assertEqual(titles, [None, "第一章 甲", "第二章 乙", "第十二章 转折", "番外1"])


class TestEpub(unittest.TestCase):
    def test_paragraph_escape(self):
        out = processor.text_to_xhtml_paragraphs('第一行<边>\n\n第二行 & "引号"\n第三行')
        self.assertEqual(out.count("<p>"), 3)
        self.assertIn("&lt;边&gt;", out)
        self.assertIn("&amp;", out)
        self.assertNotIn("<边>", out)

    def test_build_epub_structure(self):
        import tempfile, zipfile
        chapters = [("前言", "开场白"), ("第一章 起点", "主角登场\n内容<测试>"),
                    ("第二章 转折", "发展")]
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "测试书.epub")
            processor.build_epub(path, "测试书", chapters)
            with zipfile.ZipFile(path) as z:
                names = z.namelist()
                # mimetype 必须是第一个条目且未压缩
                self.assertEqual(names[0], "mimetype")
                self.assertEqual(z.getinfo("mimetype").compress_type, zipfile.ZIP_STORED)
                self.assertEqual(z.read("mimetype"), b"application/epub+zip")
                for required in ("META-INF/container.xml", "OEBPS/content.opf",
                                 "OEBPS/nav.xhtml", "OEBPS/toc.ncx", "OEBPS/style.css",
                                 "OEBPS/chapter_001.xhtml", "OEBPS/chapter_002.xhtml",
                                 "OEBPS/chapter_003.xhtml"):
                    self.assertIn(required, names)
                ch2 = z.read("OEBPS/chapter_002.xhtml").decode("utf-8")
                self.assertIn("<h2>第一章 起点</h2>", ch2)
                self.assertIn("<p>内容&lt;测试&gt;</p>", ch2)
                opf = z.read("OEBPS/content.opf").decode("utf-8")
                self.assertIn("<dc:title>测试书</dc:title>", opf)
                self.assertIn('href="chapter_003.xhtml"', opf)
                nav = z.read("OEBPS/nav.xhtml").decode("utf-8")
                self.assertIn("第二章 转折", nav)

    def test_sort_and_export_pipeline(self):
        # 模拟"章节重排 -> EPUB 导出"的完整数据流
        text = "第一章 甲\n内容A\n第十二章 转折\n内容B\n第二章 乙\n内容C"
        pattern = re.compile(processor._CHAPTER_PRESETS["第X章+序章/楔子/番外"])
        blocks = processor.sort_chapter_blocks(processor.split_chapters_by_pattern(text, pattern))
        chapters = [("前言", b) if t is None else (t, b) for t, b in blocks if b.strip()]
        self.assertEqual([t for t, _ in chapters], ["第一章 甲", "第二章 乙", "第十二章 转折"])


class TestEpubCover(unittest.TestCase):
    def test_cover_and_author(self):
        import tempfile, zipfile
        cover_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16  # 假 PNG 字节
        chapters = [("第一章 起点", "内容")]
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "带封面.epub")
            processor.build_epub(path, "书名", chapters,
                                 author="作者甲", cover=cover_bytes, cover_ext=".png")
            with zipfile.ZipFile(path) as z:
                names = z.namelist()
                self.assertIn("OEBPS/cover.png", names)
                self.assertIn("OEBPS/cover.xhtml", names)
                self.assertEqual(z.read("OEBPS/cover.png"), cover_bytes)
                opf = z.read("OEBPS/content.opf").decode("utf-8")
                self.assertIn('<dc:creator>作者甲</dc:creator>', opf)
                self.assertIn('properties="cover-image"', opf)
                self.assertIn('<meta name="cover" content="cover-image"/>', opf)
                # 封面页在 spine 首位
                spine = opf.split("<spine")[1]
                self.assertLess(spine.index('idref="cover-page"'), spine.index('idref="ch1"'))

    def test_no_cover_no_creator(self):
        import tempfile, zipfile
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "无封面.epub")
            processor.build_epub(path, "书名", [("章", "文")])
            with zipfile.ZipFile(path) as z:
                names = z.namelist()
                self.assertNotIn("OEBPS/cover.png", names)
                opf = z.read("OEBPS/content.opf").decode("utf-8")
                self.assertNotIn("dc:creator", opf)
                self.assertNotIn("cover-image", opf)


class TestCli(unittest.TestCase):
    """命令行模式端到端测试（子进程运行）"""

    SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                          "全能TXT文本处理器.py")
    NOVEL = ("本书由某某整理\n"
             "第一章 甲\n内容甲第一段。\n内容甲第二段。\n"
             "第十二章 转折\n内容十二。\n"
             "第二章 乙\n内容乙。\n"
             "第一章 甲\n内容甲第一段。\n内容甲第二段。\n")  # 第四章与第一章完全重复（乱序+重复）

    def _run(self, *cli_args):
        import subprocess
        return subprocess.run(
            [sys.executable, self.SCRIPT, *cli_args],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)

    def _make_novel(self, d, name="小说.txt"):
        path = os.path.join(d, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.NOVEL)
        return path

    def test_dedup_stdout_and_inplace(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            path = self._make_novel(d)
            r = self._run("dedup", path, "--encoding", "utf-8")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("第十二章", r.stdout)
            # 完全重复的"第一章 甲"正文块只出现一次
            self.assertEqual(r.stdout.count("内容甲第二段。"), 1)
            # 原文件未被修改
            self.assertIn("第一章 甲\n内容甲第一段", open(path, encoding="utf-8").read())

            r2 = self._run("dedup", path, "--in-place", "--encoding", "utf-8")
            self.assertEqual(r2.returncode, 0, r2.stderr)
            self.assertIn("剔除", r2.stdout)
            self.assertTrue(os.path.exists(path + ".bak"))
            self.assertEqual(open(path, encoding="utf-8").read().count("第一章 甲"), 1)

    def test_sort_inplace(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            path = self._make_novel(d)
            r = self._run("sort", path, "--in-place", "--encoding", "utf-8")
            self.assertEqual(r.returncode, 0, r.stderr)
            text = open(path, encoding="utf-8").read()
            self.assertLess(text.index("第一章 甲"), text.index("第二章 乙"))
            self.assertLess(text.index("第二章 乙"), text.index("第十二章"))

    def test_split_outdir(self):
        import tempfile, os as osmod
        with tempfile.TemporaryDirectory() as d:
            path = self._make_novel(d)
            outdir = os.path.join(d, "out")
            r = self._run("split", path, "--outdir", outdir, "--encoding", "utf-8")
            self.assertEqual(r.returncode, 0, r.stderr)
            files = sorted(osmod.listdir(outdir))
            self.assertIn("章节索引.txt", files)
            self.assertTrue(any("第一章" in f for f in files))

    def test_epub_export(self):
        import tempfile, zipfile
        with tempfile.TemporaryDirectory() as d:
            path = self._make_novel(d)
            out = os.path.join(d, "书.epub")
            r = self._run("epub", path, "--out", out, "--title", "测试书",
                          "--author", "作者乙", "--encoding", "utf-8")
            self.assertEqual(r.returncode, 0, r.stderr)
            with zipfile.ZipFile(out) as z:
                opf = z.read("OEBPS/content.opf").decode("utf-8")
                self.assertIn("<dc:title>测试书</dc:title>", opf)
                self.assertIn("<dc:creator>作者乙</dc:creator>", opf)

    def test_adfilter_and_convert(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            path = self._make_novel(d)
            words = os.path.join(d, "words.txt")
            with open(words, "w", encoding="utf-8") as f:
                f.write("内容乙\n")
            r = self._run("adfilter", path, "--words-file", words,
                          "--in-place", "--encoding", "utf-8")
            self.assertEqual(r.returncode, 0, r.stderr)
            # 含"内容乙"的行已被删除
            self.assertNotIn("内容乙", open(path, encoding="utf-8").read())

            outdir = os.path.join(d, "converted")
            r2 = self._run("convert", path, "--to", "gbk", "--outdir", outdir)
            self.assertEqual(r2.returncode, 0, r2.stderr)
            gbk_file = os.path.join(outdir, os.path.basename(path))
            with open(gbk_file, "rb") as f:
                raw = f.read()
            self.assertNotIn(b"\xef\xbb\xbf", raw)  # utf-8 BOM 应已去除
            raw.decode("gbk")  # 能按 GBK 解码

    def test_cli_stats_json_and_html(self):
        import tempfile, json as jsonmod
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "书.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(TestStats.SAMPLE)
            r = self._run("stats", path, "--encoding", "utf-8")
            self.assertEqual(r.returncode, 0, r.stderr)
            data = jsonmod.loads(r.stdout)
            self.assertEqual(data["chapters"], 3)
            self.assertEqual(data["title"], "书")

            out = os.path.join(d, "报告.html")
            r2 = self._run("stats", path, "--out", out)
            self.assertEqual(r2.returncode, 0, r2.stderr)
            html_text = open(out, encoding="utf-8").read()
            self.assertIn("<svg", html_text)

    def test_cli_hex_and_diff(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            pa = os.path.join(d, "a.txt")
            pb = os.path.join(d, "b.txt")
            with open(pa, "w", encoding="utf-8") as f:
                f.write("第一版内容\n第二章保持不变\n")
            with open(pb, "w", encoding="utf-8") as f:
                f.write("第二版内容\n第二章保持不变\n新增结尾\n")
            # GBK 编码文件应提示"不是合法 UTF-8"
            gbk_path = os.path.join(d, "gbk.txt")
            with open(gbk_path, "w", encoding="gbk") as f:
                f.write("老编码文件")
            r = self._run("hex", gbk_path)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("不是合法 UTF-8", r.stdout)
            self.assertIn("C0 CF", r.stdout)  # "老"字 GBK 编码为 C0 CF

            r2 = self._run("diff", pa, pb)
            self.assertEqual(r2.returncode, 0, r2.stderr)
            self.assertIn("+新增结尾", r2.stdout)
            self.assertIn("-第一版内容", r2.stdout)

            out = os.path.join(d, "diff.html")
            r3 = self._run("diff", pa, pb, "--out", out)
            self.assertEqual(r3.returncode, 0, r3.stderr)
            self.assertIn('class="line add"', open(out, encoding="utf-8").read())

    def test_cli_version(self):
        r = self._run("version")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(processor._APP_VERSION, r.stdout)

    def test_cli_docx_epub2txt(self):
        import tempfile, zipfile
        with tempfile.TemporaryDirectory() as d:
            novel = os.path.join(d, "小说.txt")
            with open(novel, "w", encoding="utf-8") as f:
                f.write("第一章 起点\n主角登场。\n\n第二章 相遇\n故人重逢。\n")
            docx_out = os.path.join(d, "小说.docx")
            r = self._run("docx", novel, "--out", docx_out, "--author", "作者乙")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(os.path.exists(docx_out))
            with zipfile.ZipFile(docx_out) as z:
                self.assertIn("故人重逢。", z.read("word/document.xml").decode("utf-8"))

            epub_out = os.path.join(d, "小说.epub")
            r2 = self._run("epub", novel, "--out", epub_out)
            self.assertEqual(r2.returncode, 0, r2.stderr)
            txt_out = os.path.join(d, "还原.txt")
            r3 = self._run("epub2txt", epub_out, "--out", txt_out)
            self.assertEqual(r3.returncode, 0, r3.stderr)
            restored = open(txt_out, encoding="utf-8").read()
            self.assertIn("第一章 起点", restored)
            self.assertIn("故人重逢。", restored)


class TestStats(unittest.TestCase):
    SAMPLE = ('第一章 起\n主角说："这是正文内容。"\n\n第二章 承\n江湖风波再起。\n'
              '第三章 转\n一路向西，遇见故人。\n')

    def test_compute_text_stats(self):
        s = processor.compute_text_stats(self.SAMPLE)
        self.assertEqual(s["lines"], 8)               # 含末尾换行产生的空行
        self.assertEqual(s["nonempty_lines"], 6)
        self.assertGreater(s["cjk_chars"], 0)
        self.assertEqual(s["dialogue_lines"], 1)      # 含中文引号的一行
        self.assertGreaterEqual(s["reading_minutes"], 1)

    def test_top_unigrams_excludes_stopchars(self):
        uni = processor.top_cjk_unigrams(self.SAMPLE, 10)
        self.assertTrue(all(ch not in processor._CJK_STOPCHARS for ch, _ in uni))
        labels = [ch for ch, _ in uni]
        self.assertIn("主", labels)

    def test_bigrams(self):
        bi = processor.top_cjk_bigrams(self.SAMPLE, 10)
        self.assertTrue(all(len(w) == 2 for w, _ in bi))

    def test_bucket_series(self):
        items = [(str(i), i) for i in range(1, 251)]  # 250 章
        buckets = processor.bucket_series(items, max_bars=100)
        self.assertLessEqual(len(buckets), 100)
        # 前 3 章聚合为均值 2，末尾不满一桶时按实际均值
        self.assertEqual(buckets[0], ("1-3", 2))
        self.assertEqual(buckets[-1], ("250", 250))
        # 不需要聚合时原样返回
        self.assertEqual(processor.bucket_series([("a", 1), ("b", 2)], max_bars=100),
                         [("a", 1), ("b", 2)])

    def test_svg_charts(self):
        bars = processor.svg_vbars([("第一章", 100), ("第二章", 60)])
        self.assertIn("<svg", bars)
        self.assertIn("<title>第一章：100</title>", bars)
        hbars = processor.svg_hbars([("测", 5)])
        self.assertIn('fill="#2563EB"', hbars)

    def test_report_html(self):
        pattern = re.compile(processor._CHAPTER_PRESETS["第X章"])
        report = processor.build_text_report(self.SAMPLE, "书名<测试>", pattern)
        self.assertIn("统计报告", report)
        self.assertIn("<svg", report)
        self.assertIn("书名&lt;测试&gt;", report)   # 标题已转义
        self.assertIn("高频汉字", report)
        self.assertIn("数据未离开本机", report)


class TestEngineering(unittest.TestCase):
    def test_version_tuple(self):
        vt = processor.version_tuple
        self.assertEqual(vt("v2.8"), (2, 8))
        self.assertLess(vt("v2.9"), vt("v2.10"))
        self.assertLess(vt("v2.8"), vt("v3.0"))
        self.assertEqual(vt("garbage"), (0,))

    def test_push_undo_snapshot(self):
        stack = []
        contents = {"a.txt": "内容A", "b.txt": "内容B"}
        self.assertTrue(processor.push_undo_snapshot(stack, "去除空行", contents, ["a.txt"]))
        self.assertEqual(len(stack), 1)
        self.assertEqual(stack[0]["snapshot"], {"a.txt": "内容A"})
        # 不在 contents 中的 key 被跳过；全部缺失时不入栈
        self.assertFalse(processor.push_undo_snapshot(stack, "x", contents, ["c.txt"]))
        # 上限裁剪，最旧的先被丢弃
        for i in range(processor._UNDO_LIMIT + 2):
            processor.push_undo_snapshot(stack, f"第{i}步", contents, ["a.txt"])
        self.assertEqual(len(stack), processor._UNDO_LIMIT)
        self.assertEqual(stack[0]["label"], "第2步")

    def test_convert_file_stream(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            # GBK 源 -> UTF-8 目标
            src = os.path.join(d, "gbk.txt")
            with open(src, "w", encoding="gbk") as f:
                f.write("第一章 起点正常。\n" * 500 + "结尾：完。")
            dst = os.path.join(d, "out.txt")
            src_enc, replaced = processor.convert_file_stream(src, dst, "utf-8")
            self.assertEqual(src_enc, "gbk")
            self.assertFalse(replaced)
            text = open(dst, encoding="utf-8").read()
            self.assertTrue(text.startswith("第一章 起点正常。"))
            self.assertTrue(text.endswith("结尾：完。"))
            # UTF-8 BOM 源 -> BOM 被去除
            src2 = os.path.join(d, "bom.txt")
            with open(src2, "w", encoding="utf-8-sig") as f:
                f.write("带BOM内容")
            dst2 = os.path.join(d, "out2.txt")
            src_enc2, _ = processor.convert_file_stream(src2, dst2, "utf-8")
            self.assertEqual(src_enc2, "utf-8-sig")
            with open(dst2, "rb") as f:
                self.assertFalse(f.read().startswith(b"\xef\xbb\xbf"))
            # UTF-16 BOM 源 + 截断的半个码元 -> 替换并提示
            # （BOM 探测与系统 ANSI 代码页无关，保证在任意 locale 的机器上结果一致）
            src3 = os.path.join(d, "bad.txt")
            with open(src3, "wb") as f:
                f.write("中文".encode("utf-16"))
                f.write(b"\x00")
            dst3 = os.path.join(d, "out3.txt")
            _, replaced3 = processor.convert_file_stream(src3, dst3, "utf-8")
            self.assertTrue(replaced3)


class TestHexAndDiff(unittest.TestCase):
    def test_hex_dump(self):
        out = processor.hex_dump(b"ABC\x00\xff")
        self.assertIn("00000000", out)
        self.assertIn("41 42 43 00 FF", out)
        self.assertIn("ABC", out)
        self.assertIn("··", out)  # 不可见字符
        # 多行偏移量递增
        out2 = processor.hex_dump(bytes(range(40)))
        self.assertIn("00000010", out2)
        self.assertIn("00000020", out2)

    def test_detect_encoding_hints(self):
        self.assertIn("带 UTF-8 BOM", processor.detect_encoding_hints(b"\xef\xbb\xbfabc"))
        self.assertIn("带 UTF-16 BOM", processor.detect_encoding_hints(b"\xff\xfe\x00a"))
        self.assertIn("是合法 UTF-8", processor.detect_encoding_hints("中文".encode("utf-8")))
        gbk_only = "中文".encode("gbk")
        hints = processor.detect_encoding_hints(gbk_only)
        self.assertIn("不是合法 UTF-8", "；".join(hints))
        self.assertIn("可按 GBK 解码", "；".join(hints))

    def test_unified_diff_html(self):
        report = processor.unified_diff_html("旧.txt", "新.txt", "第一行\n第二行\n第三行",
                                             "第一行\n第二行改\n第三行\n新增行")
        self.assertIn('class="line del"', report)
        self.assertIn('class="line add"', report)
        self.assertIn("第二行改", report)
        self.assertIn("+2 行 / -1 行", report)
        self.assertIn("旧.txt vs 新.txt", report)

    def test_unified_diff_html_identical(self):
        report = processor.unified_diff_html("a", "b", "相同\n内容", "相同\n内容")
        self.assertIn("内容完全一致", report)


class TestAuthor(unittest.TestCase):
    NOVEL = [("第一章 起点", "主角登场，主角看向前方。"), ("第二章 相遇", "故人重逢。"),
             ("第三章 决意", "主角下定决心。")]

    def test_build_docx_structure(self):
        import tempfile, zipfile
        import xml.etree.ElementTree as ET
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "书.docx")
            processor.build_docx(path, "书名", self.NOVEL, author="作者甲")
            with zipfile.ZipFile(path) as z:
                names = z.namelist()
                self.assertIn("[Content_Types].xml", names)
                self.assertIn("_rels/.rels", names)
                self.assertIn("word/document.xml", names)
                doc = z.read("word/document.xml").decode("utf-8")
                root = ET.fromstring(doc)  # XML 必须良构
                text = "".join(root.itertext())
                self.assertIn("书名", text)
                self.assertIn("作者甲", text)
                self.assertIn("主角登场，主角看向前方。", text)
                self.assertIn("故人重逢。", text)

    def test_epub_roundtrip(self):
        import tempfile, zipfile
        with tempfile.TemporaryDirectory() as d:
            epub_path = os.path.join(d, "书.epub")
            processor.build_epub(epub_path, "测试书", self.NOVEL, author="作者甲")
            title, chapters = processor.extract_text_from_epub(epub_path)
            self.assertEqual(title, "测试书")
            self.assertEqual([t for t, _ in chapters], [t for t, _ in self.NOVEL])
            self.assertIn("主角登场", chapters[0][1])
            text = processor.chapters_to_txt(chapters)
            self.assertIn("第一章 起点\n\n主角登场", text)
            self.assertIn("\n\n第三章 决意", text)

    def test_chapters_to_txt_skips_empty(self):
        text = processor.chapters_to_txt([("第一章", "内容"), ("空章", ""), (None, "散落内容")])
        self.assertNotIn("空章", text)
        self.assertIn("散落内容", text)

    def test_count_name_per_chapter(self):
        blocks = [(None, "前言"), ("第一章", "甲出现甲出现"), ("第二章", "甲和乙都出现")]
        series = processor.count_name_per_chapter(blocks, ["甲", "乙"])
        self.assertEqual(series[0], ("甲", [0, 2, 1]))
        self.assertEqual(series[1], ("乙", [0, 0, 1]))

    def test_svg_line_chart(self):
        svg = processor.svg_line_chart([("甲", [1, 3, 2]), ("乙", [0, 5, 1])])
        self.assertEqual(svg.count("<polyline"), 2)
        self.assertIn(">甲</text>", svg)   # 图例
        self.assertIn("<title>甲 · 第2章：3</title>", svg)
        self.assertEqual(processor.svg_line_chart([]), "")

    def test_report_rhythm_and_names(self):
        # 8 章、第 5 章明显偏短：应触发节奏提示
        parts = [f"第{i}章 标题{i}\n" + "正文内容。" * (60 if i != 5 else 5) for i in range(1, 9)]
        text = "\n\n".join(parts)
        pattern = re.compile(processor._CHAPTER_PRESETS["第X章"])
        report = processor.build_text_report(text, "节奏书", pattern, names=["正文"])
        self.assertIn("章节节奏提示", report)
        self.assertIn("中位章字数", report)
        self.assertIn("异常短章", report)
        self.assertIn("人物出场曲线", report)
        self.assertIn("中位", report)  # 分布图中位虚线标签
        # 人名全程未出现时不出曲线区块
        report2 = processor.build_text_report(text, "书", pattern, names=["路人丙"])
        self.assertNotIn("人物出场曲线", report2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
