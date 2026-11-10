#!/usr/bin/env python3
"""按核心静态资源内容派生 Service Worker 的缓存版本号。

sw.js 的 CACHE 名决定用户端缓存是否失效，手工维护极易漏升
（历史上 v140–144 就因为 sed 误解析被静默跳过）。本脚本用内容哈希生成：

    const CACHE = 'tsq-<sha1(index.html + quotes.js + 字体子集)[:10]>';

任何一处内容变化都会换新版本，sw 的 install 阶段即重新拉取核心资源。

用法:
    python3 tools/stamp_sw.py           # 写入
    python3 tools/stamp_sw.py --check   # 只校验，不一致返回 1
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SW = ROOT / "sw.js"

# 决定用户端缓存内容的文件；改动其中任何一个都必须失效旧缓存
CORE_FILES = (
    "index.html",
    "quotes.js",
    "fonts/STZHONGS.subset.woff2",
)

PATTERN = re.compile(r"const CACHE = 'tsq-[^']*';")


def digest() -> str:
    h = hashlib.sha1()
    for name in CORE_FILES:
        h.update(name.encode("utf-8"))
        h.update((ROOT / name).read_bytes())
    return h.hexdigest()[:10]


def main() -> int:
    check_only = "--check" in sys.argv[1:]
    version = f"tsq-{digest()}"
    text = SW.read_text(encoding="utf-8")

    m = PATTERN.search(text)
    if not m:
        print("错误：sw.js 中找不到 const CACHE = 'tsq-...'; 声明。", file=sys.stderr)
        return 1

    current = m.group(0).split("'")[1]
    if current == version:
        print(f"校验通过：CACHE = {version}" if check_only else f"已是最新：CACHE = {version}")
        return 0

    if check_only:
        print(f"校验失败：sw.js 为 {current}，应为 {version}（请运行 tools/stamp_sw.py）。", file=sys.stderr)
        return 1

    SW.write_text(PATTERN.sub(f"const CACHE = '{version}';", text, count=1), encoding="utf-8")
    print(f"已更新 CACHE：{current} -> {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
