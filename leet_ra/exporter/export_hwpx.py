"""
LEET-RA hwpx 출력기 — python-hwpx 기반 (v2 구현).

문항 JSON(samples/v2_5questions.json 형식 또는 단일 문항 dict)을 받아
한컴오피스에서 바로 열리는 hwpx 파일을 생성한다.

python-hwpx >= 2.6 의 HwpxDocument.new() 템플릿을 기반으로 단락을 추가하므로,
OWPML 최소 구조를 수작업 조립하던 v1 대비 호환성이 높다.

시대인재 양식의 완벽한 스타일 재현은 아니며, 2단 컬럼/폰트/표 스타일은 한컴에서 후처리 필요.

Usage:
    python export_hwpx.py --input samples/v2_5questions.json --output output/문제지.hwpx
    python export_hwpx.py --input samples/v2_5questions.json --output output/문제지.hwpx --title "LEET 연습 1회"
"""
from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path
from typing import Any

from hwpx import HwpxDocument

# python-hwpx가 blank 템플릿 로드 시 내는 정보성 경고 억제
warnings.filterwarnings("ignore", message="manifest에서.*")


def load_questions(src: Path) -> list[dict[str, Any]]:
    data = json.loads(src.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("questions", "items", "results"):
            if key in data and isinstance(data[key], list):
                return data[key]
        return [data]
    raise ValueError(f"unsupported JSON shape: {type(data).__name__}")


def add_block(doc: HwpxDocument, lines: list[str]) -> None:
    for line in lines:
        doc.add_paragraph(line)


def render_question(doc: HwpxDocument, q: dict[str, Any]) -> None:
    qno = q.get("question_number", "")
    stem = q.get("stem", "")
    passage = q.get("passage_text", "") or ""
    bogie = q.get("bogie_items", {}) or {}
    choices = q.get("choices", []) or []
    answer = q.get("answer", "")
    explanations = q.get("explanations", {}) or {}
    domain = q.get("domain", "")

    doc.add_paragraph("")
    doc.add_paragraph(f"{qno}. [{domain}] {stem}")

    if passage:
        doc.add_paragraph("")
        doc.add_paragraph("<지문>")
        for line in str(passage).splitlines():
            line = line.strip()
            if line:
                doc.add_paragraph(line)

    if bogie:
        doc.add_paragraph("")
        doc.add_paragraph("<보기>")
        for k, v in bogie.items():
            doc.add_paragraph(f"{k}. {v}")

    if choices:
        doc.add_paragraph("")
        for c in choices:
            doc.add_paragraph(str(c))

    if answer:
        doc.add_paragraph("")
        doc.add_paragraph(f"[정답] {answer}")

    if explanations:
        doc.add_paragraph("[해설]")
        for k, v in explanations.items():
            doc.add_paragraph(f"{k}) {v}")


def write_hwpx(out_path: Path, title: str, questions: list[dict[str, Any]]) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc = HwpxDocument.new()
    doc.add_paragraph(title)
    doc.add_paragraph(f"총 {len(questions)}문항")
    doc.add_paragraph("")
    for q in questions:
        render_question(doc, q)
        doc.add_paragraph("")

    # save_to_path 우선, 없으면 save 폴백
    save_fn = getattr(doc, "save_to_path", None) or doc.save
    save_fn(str(out_path))
    return out_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", "-i", required=True, help="문항 JSON 경로")
    ap.add_argument("--output", "-o", required=True, help="출력 hwpx 경로")
    ap.add_argument("--title", "-t", default="LEET 추리논증 문제지", help="문서 제목")
    args = ap.parse_args()

    src = Path(args.input)
    dst = Path(args.output)
    qs = load_questions(src)
    write_hwpx(dst, args.title, qs)
    print(f"[ok] wrote {dst}  ({len(qs)} 문항, {dst.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
