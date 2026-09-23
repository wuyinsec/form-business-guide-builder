#!/usr/bin/env python3
"""Convert an approved business-assistant review workbook into DAT files."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

from office_data import read_first_sheet


FIELDS = {
    "业务助手内容": "content",
    "业务流程指引": "wfGuide",
    "业务填报指引": "bizFillingGuide",
    "附件清单说明": "attachmentGuide",
}
REQUIRED_HEADERS = ["表单名称", *FIELDS]
INVALID_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="根据已确认的业务助手审阅表批量生成可导入 DAT 文件。"
    )
    parser.add_argument("xlsx", type=Path, help="已确认的业务助手 Excel 文件")
    parser.add_argument("--template", required=True, type=Path, help="系统导出的 DAT 模板")
    parser.add_argument("--output-dir", required=True, type=Path, help="DAT 输出目录")
    parser.add_argument(
        "--overwrite", action="store_true", help="允许覆盖输出目录中同名 DAT 文件"
    )
    return parser.parse_args()


def text_to_html(value: str) -> str:
    """Preserve reviewed line breaks without adding or rewriting any wording."""
    lines = str(value).replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "".join(f"<p>{html.escape(line, quote=False)}</p>" for line in lines)


def load_template(path: Path) -> dict:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"DAT 模板不是有效的 UTF-8 JSON：{path}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("cfgEntity"), dict):
        raise ValueError("DAT 模板缺少 cfgEntity 对象，无法安全生成文件。")
    return data


def records_from_xlsx(path: Path) -> list[dict[str, str]]:
    rows = read_first_sheet(path)
    if not rows:
        raise ValueError("Excel 中没有数据。")
    headers = [str(cell).strip() for cell in rows[0]]
    missing = [name for name in REQUIRED_HEADERS if name not in headers]
    if missing:
        raise ValueError(f"Excel 缺少列：{'、'.join(missing)}")
    indexes = {name: headers.index(name) for name in REQUIRED_HEADERS}
    records: list[dict[str, str]] = []
    seen: set[str] = set()
    for row_number, row in enumerate(rows[1:], start=2):
        record = {
            name: str(row[index]) if index < len(row) else ""
            for name, index in indexes.items()
        }
        if not any(record.values()):
            continue
        form_name = record["表单名称"].strip()
        record["表单名称"] = form_name
        if not form_name:
            raise ValueError(f"第 {row_number} 行缺少表单名称。")
        if INVALID_FILENAME.search(form_name) or form_name.endswith((".", " ")):
            raise ValueError(f"第 {row_number} 行表单名称不能作为 Windows 文件名：{form_name}")
        if form_name in seen:
            raise ValueError(f"表单名称重复：{form_name}")
        seen.add(form_name)
        empty = [name for name in FIELDS if not record[name].strip()]
        if empty:
            raise ValueError(
                f"第 {row_number} 行“{form_name}”存在空白板块：{'、'.join(empty)}"
            )
        records.append(record)
    if not records:
        raise ValueError("Excel 中没有可生成的表单记录。")
    return records


def main() -> int:
    args = parse_args()
    try:
        template = load_template(args.template)
        records = records_from_xlsx(args.xlsx)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for record in records:
            output = args.output_dir / f"{record['表单名称']}.dat"
            if output.exists() and not args.overwrite:
                raise FileExistsError(f"目标文件已存在；如需覆盖请增加 --overwrite：{output}")
        for record in records:
            data = json.loads(json.dumps(template, ensure_ascii=False))
            entity = data["cfgEntity"]
            entity["formName"] = record["表单名称"]
            for header, key in FIELDS.items():
                entity[key] = text_to_html(record[header])
            output = args.output_dir / f"{record['表单名称']}.dat"
            output.write_text(
                json.dumps(data, ensure_ascii=False, separators=(",", ":")),
                encoding="utf-8",
                newline="",
            )
        print(f"已生成 {len(records)} 个 DAT 文件：{args.output_dir}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
