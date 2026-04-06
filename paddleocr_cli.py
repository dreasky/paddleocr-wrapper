#!/usr/bin/env python3
"""
PaddleOCR CLI

Subcommands:
  convert   Convert a PDF/image to Markdown
"""

import argparse
import sys
from pathlib import Path

scripts_dir = Path(__file__).parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from paddleocr_wrapper import PaddleocrWrapper


def cmd_convert(args):
    PaddleocrWrapper().convert(Path(args.input), Path(args.output))


def main():
    parser = argparse.ArgumentParser(prog="paddleocr_cli")
    sub = parser.add_subparsers(dest="command", required=True)

    p_conv = sub.add_parser("convert", help="Convert a PDF or image to Markdown")
    p_conv.add_argument(
        "-i", "--input", required=True, dest="input", help="Input file path (PDF or image)"
    )
    p_conv.add_argument(
        "-o", "--output", required=True, dest="output", help="Output .md file path"
    )

    args = parser.parse_args()

    try:
        cmd_convert(args)
        return 0
    except Exception as e:
        print(f"转换失败: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
