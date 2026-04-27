# paddleocr-wrapper

基于 PaddleOCR API 的封装库，支持 PDF 和图片转 Markdown，含版面分析、跨页表格合并等能力。

## 安装

```bash
# 作为 git submodule
git clone https://github.com/dreasky/paddleocr-wrapper.git
pip install -e paddleocr-wrapper

# 直接从 GitHub 安装
pip install --upgrade git+https://github.com/dreasky/paddleocr-wrapper.git
```

## 配置

在项目根目录创建 `.env`：

```
PADDLEOCR_OCR_API_URL=http://your-paddleocr-api/ocr
PADDLEOCR_ACCESS_TOKEN=your_token
```

### 配置文件（可选）

包内置了默认的 `paddleocr_config.json`，覆盖优先级：**传入参数 > `cwd/paddleocr_config.json` > 包内置默认**。

```python
from paddleocr_wrapper import PaddleocrWrapper
from pathlib import Path

# 使用包内置默认配置
wrapper = PaddleocrWrapper()

# 使用自定义配置
wrapper = PaddleocrWrapper(config_file=Path("my_paddleocr_config.json"))
```

常用配置项：

| 字段                   | 默认值                      | 说明                           |
| ---------------------- | --------------------------- | ------------------------------ |
| `useLayoutDetection`   | `true`                      | 版面区域检测与排序             |
| `restructurePages`     | `true`                      | 多页结果重构（跨页表格合并等） |
| `mergeTables`          | `true`                      | 跨页表格合并                   |
| `prettifyMarkdown`     | `true`                      | Markdown 美化输出              |
| `temperature`          | `0`                         | 识别稳定性，越低越保守         |
| `markdownIgnoreLabels` | `["header", "footer", ...]` | 生成 Markdown 时忽略的区域标签 |

完整配置项见包内 `paddleocr_wrapper/paddleocr_config.json`。

## 使用

```python
from paddleocr_wrapper import PaddleocrWrapper
from pathlib import Path

wrapper = PaddleocrWrapper()

# PDF 或图片转 Markdown，图片保存在 output/imgs/
output_md = wrapper.convert(Path("document.pdf"), output_dir=Path("output"))
```

## 支持的输入格式

PDF、jpg、jpeg、png、bmp、gif、tiff、webp
