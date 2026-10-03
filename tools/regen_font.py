#!/usr/bin/env python3
"""重新生成 STZHONGS.subset.woff2 — 添加新名言后运行此脚本。

用法: python3 tools/regen_font.py
依赖: pip install fonttools brotli
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_FONT = ROOT / "STZHONGS.woff2"
OUT_FONT = ROOT / "STZHONGS.subset.woff2"
CHARS_FILE = "/tmp/subset_chars.txt"

# 收集网站所有非 ASCII 字符
chars = set()
for name in ("quotes.js", "index.html"):
    text = (ROOT / name).read_text(encoding="utf-8")
    chars.update(c for c in text if ord(c) >= 0x80)

# ASCII 可打印 + 常用全角标点 + 弯引号（被 STZhongsong 渲染）
chars.update(chr(i) for i in range(32, 127))
chars.update("。，、；：？！''（）《》—…·")
chars.update("\u2018\u2019\u201a\u201b\u201c\u201d\u201e\u201f")

Path(CHARS_FILE).write_text("".join(sorted(chars)), encoding="utf-8")
print(f"字符数: {len(chars)}")

subprocess.run([
    "pyftsubset", str(SRC_FONT),
    f"--text-file={CHARS_FILE}",
    f"--output-file={OUT_FONT}",
    "--flavor=woff2",
    "--no-hinting",
    "--desubroutinize",
    "--layout-features=*",
], check=True)

# 验证缺字
from fontTools.ttLib import TTFont
cmap = TTFont(str(OUT_FONT)).getBestCmap()
missing = set()
for name in ("quotes.js", "index.html"):
    text = (ROOT / name).read_text(encoding="utf-8")
    missing.update(c for c in text if ord(c) >= 0x80 and ord(c) not in cmap)

if missing:
    print(f"⚠ {len(missing)} 个字符不在原字体中（系统回退显示，不影响）: {missing}")
else:
    print("✓ 所有字符都在子集中")

size = OUT_FONT.stat().st_size
print(f"✓ 生成完成: {OUT_FONT.name} ({size / 1024:.0f} KB)")
