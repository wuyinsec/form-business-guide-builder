#!/usr/bin/env python3
"""Validate generated business-assistant DAT files and optional XLSX parity."""

from __future__ import annotations

import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

from office_data import read_first_sheet


FIELDS = {
    "业务助手内容": "content",
    "业务流程指引": "wfGuide",
    "业务填报指引": "bizFillingGuide",
    "附件清单说明": "attachmentGuide",
}


class ParagraphReader(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.paragraphs: list[str] = []
        self.current: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "p":
            if self.current is not None:
                self.paragraphs.append("".join(self.current))
            self.current = []
        elif tag.lower() == "br" and self.current is not None:
            self.current.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "p" and self.current is not None:
            self.paragraphs.append("".join(self.current))
            self.current = None

    def handle_data(self, data: str) -> None:
        if self.current is not None:
            self.current.append(data)

    def result(self) -> str:
        if self.current is not None:
            self.paragraphs.append("".join(self.current))
            self.current = None
        return "\n".join(self.paragraphs)


def html_to_text(value: str) -> str:
    parser = ParagraphReader()
    parser.feed(value)
    parsed = parser.result()
    return parsed if parser.paragraphs else value


def workbook_records(path: Path) -> dict[str, dict[str, str]]:
    rows = read_first_sheet(path)
    if not rows:
        raise ValueError("审阅表为空。")
    headers = [str(cell).strip() for cell in rows[0]]
    required = ["表单名称", *FIELDS]
    missing = [name for name in required if name not in headers]
    if missing:
        raise ValueError(f"审阅表缺少列：{'、'.join(missing)}")
    indexes = {name: headers.index(name) for name in required}
    result: dict[str, dict[str, str]] = {}
    for row in rows[1:]:
        name = str(row[indexes["表单名称"]]).strip() if indexes["表单名称"] < len(row) else ""
        if not name:
            continue
        result[name] = {
            header: str(row[index]) if index < len(row) else ""
            for header, index in indexes.items()
        }
        result[name]["表单名称"] = name
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="校验 DAT 结构及其与审阅表的一致性。")
    parser.add_argument("dat_dir", type=Path, help="DAT 文件目录")
    parser.add_argument("--xlsx", type=Path, help="用于逐字比对的最终审阅表")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    dat_files = sorted(args.dat_dir.glob("*.dat"))
    if not dat_files:
        print(f"错误：目录中没有 DAT 文件：{args.dat_dir}", file=sys.stderr)
        return 1

    expected: dict[str, dict[str, str]] | None = None
    if args.xlsx:
        try:
            expected = workbook_records(args.xlsx)
        except (OSError, ValueError) as exc:
            print(f"错误：{exc}", file=sys.stderr)
            return 1

    found_names: set[str] = set()
    for path in dat_files:
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            errors.append(f"{path.name}：含 UTF-8 BOM")
        try:
            data = json.loads(raw.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"{path.name}：不是有效的 UTF-8 JSON（{exc}）")
            continue
        entity = data.get("cfgEntity") if isinstance(data, dict) else None
        if not isinstance(entity, dict):
            errors.append(f"{path.name}：缺少 cfgEntity 对象")
            continue
        form_name = str(entity.get("formName", "")).strip()
        found_names.add(form_name)
        if not form_name:
            errors.append(f"{path.name}：formName 为空")
        elif path.stem != form_name:
            errors.append(f"{path.name}：文件名与 formName 不一致（{form_name}）")
        for header, key in FIELDS.items():
            value = entity.get(key)
            if not isinstance(value, str) or not html_to_text(value).strip():
                errors.append(f"{path.name}：{header}为空或格式无效")
            if expected is not None and form_name in expected and isinstance(value, str):
                actual = html_to_text(value).replace("\r\n", "\n").replace("\r", "\n")
                wanted = expected[form_name][header].replace("\r\n", "\n").replace("\r", "\n")
                if actual != wanted:
                    errors.append(f"{path.name}：{header}与审阅表不一致")

    if expected is not None:
        expected_names = set(expected)
        for name in sorted(expected_names - found_names):
            errors.append(f"缺少 DAT：{name}.dat")
        for name in sorted(found_names - expected_names):
            errors.append(f"存在审阅表中没有的 DAT：{name}.dat")

    if errors:
        print("校验失败：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    suffix = "，并与审阅表逐字一致" if args.xlsx else ""
    print(f"校验通过：{len(dat_files)} 个 DAT 文件结构有效{suffix}。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
