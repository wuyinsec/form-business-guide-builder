#!/usr/bin/env python3
"""Extract searchable text from DOCX and XLSX source materials."""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from office_data import read_first_sheet


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def docx_text(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    lines: list[str] = []
    for paragraph in root.iter(f"{{{W_NS}}}p"):
        text = "".join(node.text or "" for node in paragraph.iter(f"{{{W_NS}}}t")).strip()
        if text:
            lines.append(text)
    return lines


def xlsx_text(path: Path) -> list[str]:
    lines: list[str] = []
    for row in read_first_sheet(path):
        values = [str(value).strip() for value in row]
        if any(values):
            lines.append("\t".join(values))
    return lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="提取 DOCX/XLSX 中的可检索文本。")
    parser.add_argument("files", nargs="+", type=Path, help="一个或多个 DOCX/XLSX 文件")
    parser.add_argument("--keywords", help="关键词，多个词用 | 分隔；不传则输出全部文本")
    parser.add_argument("--context", type=int, default=1, help="关键词命中时的上下文行数")
    return parser.parse_args()


def selected_lines(lines: list[str], keywords: str | None, context: int) -> list[str]:
    if not keywords:
        return lines
    pattern = re.compile(keywords, re.IGNORECASE)
    indexes: set[int] = set()
    for index, line in enumerate(lines):
        if pattern.search(line):
            start = max(0, index - max(context, 0))
            end = min(len(lines), index + max(context, 0) + 1)
            indexes.update(range(start, end))
    return [lines[index] for index in sorted(indexes)]


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    args = parse_args()
    failed = False
    for path in args.files:
        try:
            suffix = path.suffix.lower()
            if suffix == ".docx":
                lines = docx_text(path)
            elif suffix == ".xlsx":
                lines = xlsx_text(path)
            else:
                raise ValueError("仅支持 .docx 和 .xlsx")
            print(f"\n===== {path} =====")
            for line in selected_lines(lines, args.keywords, args.context):
                print(line)
        except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
            print(f"错误：{path}：{exc}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
