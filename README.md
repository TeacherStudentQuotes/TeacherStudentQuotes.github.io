# 师生名言精选

纸页之间的师生对话。纯前端单页应用，GitHub Pages 托管，无构建步骤。

在线地址：<https://teacherstudentquotes.github.io/>

## 仓库结构

```
.
├── index.html          # 单文件应用：页面结构、全部样式与交互逻辑都在这一个文件里
├── quotes.js           # 数据层：教师简表、班级学生字典、Quote 类、名言数组
├── sw.js               # Service Worker：离线缓存核心资源（CACHE 版本由 tools/stamp_sw.py 按内容哈希生成）
├── manifest.json       # PWA 清单
│
├── fonts/              # 字体
│   ├── STZHONGS.subset.woff2   # 华文宋体子集（网站实际加载，仅含站内用到的字符）
│   ├── STZHONGS.woff2          # 华文宋体完整版（仅作子集化源文件，不直接加载）
│   └── cmu.serif-roman.woff2   # CMU Serif（数学公式用衬线）
│
├── img/                # 静态图片
│   ├── favicon.ico
│   ├── cry.png                 # 搜索无结果时的插图
│   └── og-cover.png            # Open Graph 分享卡片（不写名言数量，数量只在 meta 文案里）
│
├── source/             # 原始素材：名言手写纸扫描/照片（按册分目录，不参与网站构建）
│   ├── 心形纸.jpg              # 1 张
│   ├── 第一册/                  # 20 张
│   ├── 第二册/                  # 20 张
│   └── 第三册/                  # 10 张
│
├── tools/
│   ├── regen_font.py           # 字体子集化：收集 quotes.js / index.html 中所有非 ASCII
│   │                           # 字符，用 pyftsubset 重生成 STZHONGS.subset.woff2
│   ├── sync_meta.py            # 把 quotes.js 的名言总数写进 index.html 的三处描述文案
│   │                           # （og:description / twitter:description / setOgMeta）
│   └── stamp_sw.py             # 按 index.html + quotes.js + 字体子集的内容哈希派生
│                               # sw.js 的 CACHE 版本号，内容一变缓存必然失效
│
└── .github/workflows/
    └── rebuild-font.yml        # push 到 main 且改到 quotes.js / index.html / tools / 字体源文件时：
                                # 重建字体子集 → 同步名言总数 → 刷新 SW 版本号 → 校验 → 由 bot 单独提交
```

## 名言数据格式

`quotes.js` 中的名言通过 `Quote` 类构造：

```js
new Quote('高子', `名言内容`, ["标签"])
```

- 第一个参数传**教师简称**（如 `'高子'`）会自动解析为全名；传 `student(班级, 学号)` 或任意字符串则原样显示。
- 教师简称在文件顶部的 `teachers` 数组中维护；学生在 `students` 字典（按班级分组）。
- 第四个参数是原稿位置 `'册-页'`（如 `'2-7'`，跨页写 `'2-3+2-4'`），"看原稿"功能用；编者手记不传。

## 常用维护流程

**添加名言**：直接编辑 `quotes.js` → push。CI 会自动重建字体子集、同步 OG/分享文案里的名言总数、刷新 Service Worker 的缓存版本号，然后以一条独立的 bot 提交推回 main（提交信息带 `[skip ci]`，不会二次触发自己）。

本地若想立即生效，可手动跑同一套脚本：

```bash
pip install fonttools brotli
python3 tools/regen_font.py    # 重建字体子集
python3 tools/sync_meta.py     # 同步名言数量
python3 tools/stamp_sw.py      # 派生 SW 缓存版本
```

推之前建议先校验一遍（CI 里也会跑同样的检查，不一致直接失败，不会静默放过）：

```bash
python3 tools/sync_meta.py --check
python3 tools/stamp_sw.py --check
```

> `index.html` 里的数量文案由 `sync_meta.py` 统一改写，**不要手工改数字**；`sw.js` 的 `CACHE` 由 `stamp_sw.py` 生成，**不要手工改版本号**。改文案措辞时，记得同步 `sync_meta.py` 里的正则与 `EXPECTED_MATCHES`。

**本地预览**：

```bash
python3 -m http.server 8000
# 打开 http://localhost:8000
```

> 注意：直接双击 `index.html`（file:// 协议）无法加载 `quotes.js`，请用本地服务器。
