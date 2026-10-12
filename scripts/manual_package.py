#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
manual_package.py — 手动发布整理（仅标准库，任何系统可用）

过内容门禁 → 图片按上传顺序编号 → 生成文案.txt，交用户在点评 App 里手动发布。

用法:
  manual_package.py --json post.json [--kind note|review] [--out-dir DIR] [--no-gate]
      post.json: {"shop": "品牌（分店）", "title": "笔记标题", "body": "…", "tags": ["#…"],
                  "images": ["/abs/01.jpg", …], "facts": {…事实卡…},
                  "stars": 4.5, "scores": {"口味": 4}, "per_capita": 38}
      默认输出到 ~/Downloads/<店名>-发布/<评价|笔记>/

退出码: 0 成功 1 门禁未过或输入错误
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from content_gate import check, format_report, load_sibling_hooks  # noqa: E402

IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png")
KIND_LABEL = {"review": "评价", "note": "笔记"}


class PublishError(Exception):
    """本文件用到 E401 门禁未过 / E402 字段或星级不合法 / E403 图片问题；全表见 Pro 版的发布文档。"""

    def __init__(self, message: str, code: str = ""):
        super().__init__(message)
        self.code = code

    def __str__(self):
        msg = super().__str__()
        return f"[{self.code}] {msg}" if self.code else msg


def _valid_star(v, allow_half: bool) -> bool:
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not 1 <= v <= 5:
        return False
    return float(v * 2).is_integer() if allow_half else isinstance(v, int)


def validate_payload(payload: dict, kind: str, no_gate: bool, allow_half: bool = False) -> list:
    """allow_half：手动发布可填半星；自动代发只会点整星，必须是整数。"""
    if not payload.get("shop"):
        raise PublishError("缺少 shop（店铺名，用于搜索与店铺断言）", code="E402")
    if not payload.get("body"):
        raise PublishError("缺少 body", code="E402")
    if kind == "note" and not payload.get("title"):
        raise PublishError("笔记缺少 title", code="E402")
    if kind == "review":
        unit = "0.5 为步长" if allow_half else "整数"
        if not _valid_star(payload.get("stars"), allow_half):
            raise PublishError(f"评价必须给 stars（1–5，{unit}，来自用户真实打分）", code="E402")
        for label, s in (payload.get("scores") or {}).items():
            if not _valid_star(s, allow_half):
                raise PublishError(f"scores.{label} 必须是 1–5（{unit}）", code="E402")
    if not no_gate and payload.get("facts") is None:
        raise PublishError("缺少事实卡 facts（访谈事实，用于校验数字有出处）", code="E402")
    images = [Path(p) for p in payload.get("images", [])]
    for img in images:
        if not img.exists():
            raise PublishError(f"图片不存在: {img}", code="E403")
        if img.suffix.lower() not in IMAGE_SUFFIXES:
            raise PublishError(f"图片格式不支持: {img.name}（先转成 JPG）", code="E403")
    return images


def run_gate(title: str, body: str, kind: str, payload: dict) -> dict:
    report = check(title, body, kind, payload.get("facts"), per_capita=payload.get("per_capita"),
                   siblings=load_sibling_hooks(payload.get("shop")))
    print(format_report(report))
    if not report["pass"]:
        raise PublishError("内容门禁未通过（--no-gate 可跳过，但不建议）", code="E401")
    return report


def manual_text(payload: dict, kind: str) -> str:
    lines = []
    if kind == "note":
        lines += [payload["title"], ""]
    lines.append(payload["body"])
    if payload.get("tags"):
        lines += ["", " ".join(payload["tags"])]
    meta = []
    if kind == "review":
        meta.append(f"总体星级：{payload.get('stars')}")
        meta += [f"{k}：{v}" for k, v in (payload.get("scores") or {}).items()]
    if payload.get("per_capita") is not None:
        meta.append(f"人均：{payload['per_capita']}")
    if meta:
        lines += ["", "—— 发布时填写 ——"] + meta
    return "\n".join(lines) + "\n"


def stage_manual(payload: dict, kind: str, out_root: str = "", no_gate: bool = False) -> Path:
    images = validate_payload(payload, kind, no_gate, allow_half=True)
    title = payload.get("title", "") if kind == "note" else ""
    if not no_gate:
        run_gate(title, payload["body"], kind, payload)
    root = Path(out_root) if out_root else Path.home() / "Downloads" / f"{payload['shop']}-发布"
    d = root / KIND_LABEL[kind]
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    for i, img in enumerate(images, 1):
        shutil.copy(img, d / f"{i:02d}-{img.name}")
    (d / "文案.txt").write_text(manual_text(payload, kind), encoding="utf-8")
    print(f"✅ 已整理到 {d}（{len(images)} 张图按上传顺序编号 + 文案.txt）")
    return d


def main():
    ap = argparse.ArgumentParser(description="手动发布整理：门禁 + 图片编号 + 文案")
    ap.add_argument("--json", required=True, help="post.json")
    ap.add_argument("--kind", default="note", choices=["note", "review"])
    ap.add_argument("--out-dir", help="默认 ~/Downloads/<店名>-发布/")
    ap.add_argument("--no-gate", action="store_true")
    args = ap.parse_args()
    try:
        payload = json.loads(Path(args.json).read_text(encoding="utf-8"))
        stage_manual(payload, args.kind, args.out_dir, args.no_gate)
    except PublishError as e:
        print(f"⛔ {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
