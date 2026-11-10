#!/usr/bin/env python3
"""把 quotes.js 的名言总数同步进 index.html 的描述文案。

index.html 里一共有三处带数字的文案，全部由本脚本统一改写：
  - <meta property="og:description">
  - <meta name="twitter:description">
  - setOgMeta(...)（切页时刷新分享信息）
文案形态支持 `N 句师生对话` 与早期的 `N 条师生名言` 两种，改版换措辞不用改脚本。

用法:
    python3 tools/sync_meta.py           # 写入（数字已对时不落盘）
    python3 tools/sync_meta.py --check   # 只校验，不一致返回 1

CI 里先写入再 --check，任何一处漏改都会让任务失败，而不是静默放过。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUOTES = ROOT / "quotes.js"
INDEX = ROOT / "index.html"

# 数量后面紧跟的中文措辞；新增措辞时在这里补一条
PATTERN = re.compile(r"(\d+)(\s*)(句师生对话|条师生名言)")

# index.html 里应当被同步的处数。模板改版（比如去掉 twitter meta）时同步调整此值，
# 数字对不上就报错，而不是让脚本"少改一处也返回成功"。
EXPECTED_MATCHES = 3


def count_quotes() -> int:
    text = QUOTES.read_text(encoding="utf-8")
    return len(re.findall(r"new Quote\(", text))


def line_no(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def main() -> int:
    check_only = "--check" in sys.argv[1:]
    count = count_quotes()
    text = INDEX.read_text(encoding="utf-8")

    matches = list(PATTERN.finditer(text))
    if len(matches) != EXPECTED_MATCHES:
        print(
            f"错误：index.html 中匹配到 {len(matches)} 处数量文案，期望 {EXPECTED_MATCHES} 处。\n"
            "       若文案模板有改动，请同步更新 EXPECTED_MATCHES。",
            file=sys.stderr,
        )
        return 1

    stale = [m for m in matches if int(m.group(1)) != count]
    for m in stale:
        print(
            f"  index.html:{line_no(text, m.start())}  "
            f"{m.group(1)} -> {count}（{m.group(3)}）"
        )

    if check_only:
        if stale:
            print(f"校验失败：{len(stale)} 处数量与 quotes.js（{count} 条）不一致。", file=sys.stderr)
            return 1
        print(f"校验通过：{len(matches)} 处数量均为 {count}。")
        return 0

    if not stale:
        print(f"已是最新：{len(matches)} 处数量均为 {count}。")
        return 0

    new_text = PATTERN.sub(lambda m: f"{count}{m.group(2)}{m.group(3)}", text)
    INDEX.write_text(new_text, encoding="utf-8")
    print(f"已同步 {len(stale)} 处数量为 {count}。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
