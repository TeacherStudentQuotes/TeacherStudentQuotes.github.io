# 师生名言精选

纸页之间的师生对话。纯前端单页应用，GitHub Pages 托管，无构建步骤。

在线地址：<https://teacherstudentquotes.github.io/>

## 仓库结构

```
.
├── index.html          # 单文件应用：页面结构、全部样式与交互逻辑都在这一个文件里
├── quotes.js           # 数据层：教师简表、班级学生字典、Quote 类、名言数组
├── sw.js               # Service Worker：离线缓存核心资源（改动静文件需同步升 CACHE 版本号）
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
│   └── og-cover.png            # Open Graph 分享卡片
│
├── source/             # 原始素材：名言手写纸扫描/照片（按册分目录，不参与网站构建）
│   ├── 心形纸.jpg
│   ├── 第一册/                  # 20 张
│   ├── 第二册/                  # 1 张
│   └── 第三册/                  # 10 张
│
├── tools/
│   └── regen_font.py           # 字体子集化脚本：收集 quotes.js / index.html 中所有非 ASCII
│                               # 字符，用 pyftsubset 重生成 STZHONGS.subset.woff2
│
└── .github/workflows/
    └── rebuild-font.yml        # push 到 main 且改到 quotes.js / index.html / tools 时自动运行：
                                # 重建字体子集 + 把名言总数同步进 OG 描述，amend 进触发提交
```

## 名言数据格式

`quotes.js` 中的名言通过 `Quote` 类构造：

```js
new Quote('高子', `名言内容`, ["标签"])
```

- 第一个参数传**教师简称**（如 `'高子'`）会自动解析为全名；传 `student(班级, 学号)` 或任意字符串则原样显示。
- 教师简称在文件顶部的 `teachers` 数组中维护；学生在 `students` 字典（按班级分组）。

## 常用维护流程

**添加名言**：直接编辑 `quotes.js` → push。CI 会自动重建字体子集并同步 OG 卡片上的名言数量，无需手动运行脚本。本地若想立即生效，也可手动跑：

```bash
pip install fonttools brotli
python3 tools/regen_font.py
```

**本地预览**：

```bash
python3 -m http.server 8000
# 打开 http://localhost:8000
```

> 注意：直接双击 `index.html`（file:// 协议）无法加载 `quotes.js`，请用本地服务器。
