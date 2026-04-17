"""
LEET-RA hwpx 출력기 — 시대인재 3종 양식 (default/jeonguk/serva).

실제 시대인재 LEET hwpx에서 본문 텍스트만 비운 '빈 템플릿'
(`leet_ra/templates/*_빈.hwpx`)을 양식별로 복제하고, 문항 JSON의
내용을 시대인재 스타일명(예: '문제', '선택지', '보기박스',
'보기내용(내어쓰기)', '지문 (테두리)', '박스내용(들여쓰기)')으로 추가한다.

교열 매뉴얼(추리논증ver)의 핵심 규칙 중 자동 처리 가능한 것을 반영한다:
- 문항 번호와 발문 사이는 '묶음 빈 칸'(U+2060 WORD JOINER) 삽입
- 선지 번호(①②③④⑤)와 내용 사이도 묶음 빈 칸
- 조문 내부 수치의 `만 원` 띄어쓰기 등 문자 치환
- 들여쓰기는 공백이 아니라 스타일을 통해 표현

Usage:
    python export_hwpx.py --input samples/v2_5questions.json \
        --output-problem output/문제지.hwpx \
        --output-solution output/해설지.hwpx \
        --title "LEET-RA 연습 1회"
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import warnings
import zipfile
from pathlib import Path
from typing import Any

from hwpx import HwpxDocument

warnings.filterwarnings("ignore", message="manifest에서.*")

# Unicode 특수 공백 — 교열 매뉴얼
U_WORD_JOINER = "\u2060"   # 묶음 빈 칸 (Ctrl+Alt+Space 대응)
U_NBSP = "\u00A0"          # 고정폭 빈 칸 (Alt+Space 대응)

# 선지 원문자
CHOICE_MARKS = ("①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩")

# 양식(format) 별 템플릿 매핑 — '서바 양식으로 뽑아줘' / '전국 양식으로 뽑아줘' 등 자연어 트리거가
# ra-exporter 스킬을 거쳐 --format으로 도달한다.
FORMAT_TEMPLATES: dict[str, dict[str, str]] = {
    # 26추리 실제 제작본 기반. 크기 작고 레이아웃 간결. 기본값.
    "default": {
        "problem": "leet_ra/templates/시대인재_문제지_빈.hwpx",
        "solution": "leet_ra/templates/시대인재_해설지_빈.hwpx",
    },
    # 전국 모의고사 양식 — 전국_문제지.hwpx 에서 본문만 비운 것 + 공용 해설지
    "jeonguk": {
        "problem": "leet_ra/templates/전국_문제지_빈.hwpx",
        "solution": "leet_ra/templates/전국서바_해설지_빈.hwpx",
    },
    # 서바이벌 모의고사 양식 — 서바_문제지.hwpx 기반
    "serva": {
        "problem": "leet_ra/templates/서바_문제지_빈.hwpx",
        "solution": "leet_ra/templates/전국서바_해설지_빈.hwpx",
    },
}

# 하위 호환
DEFAULT_TEMPLATES = FORMAT_TEMPLATES["default"]


# ------------------------ 유틸 ------------------------

def build_style_map(hwpx_path: Path) -> dict[str, int]:
    """hwpx 내부 header.xml에서 style name → id 매핑 추출."""
    mapping: dict[str, int] = {}
    with zipfile.ZipFile(hwpx_path) as zf:
        for name in zf.namelist():
            if name.endswith("header.xml"):
                xml = zf.read(name).decode("utf-8", errors="replace")
                for m in re.finditer(r"<hh:style\s+([^/>]+)/?>", xml):
                    attrs = m.group(1)
                    id_m = re.search(r'\bid="(\d+)"', attrs)
                    name_m = re.search(r'\bname="([^"]+)"', attrs)
                    if id_m and name_m:
                        # HWPX 파일이 entity-encoded 이름을 쓸 수 있음 (예: &lt;사례견해&gt;)
                        style_name = name_m.group(1).replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
                        mapping[style_name] = int(id_m.group(1))
    return mapping


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


def clean_body(doc: HwpxDocument) -> None:
    """더 이상 사용하지 않음. 빈 템플릿(시대인재_*_빈.hwpx)은 이미 텍스트가 비워져 있고
    레이아웃(표·2단 컬럼·바탕쪽·헤더)만 유지된 상태이므로, 섹션 children을 제거하지 않고
    그대로 사용한다. 이 함수는 하위 호환용 no-op."""
    return


def compose_stem_line(qno: Any, stem: str) -> str:
    """문항 번호와 발문 사이 묶음 빈 칸 삽입 (교열 매뉴얼 권고)."""
    return f"{qno}.{U_WORD_JOINER}{stem}".strip()


def compose_choice_line(raw: str) -> str:
    """선지 번호(①②…) 다음에 묶음 빈 칸 삽입.
    JSON 원본이 '① ㄱ' 같은 경우 공백을 묶음 빈 칸으로 교체.
    """
    s = str(raw).strip()
    if not s:
        return s
    # 첫 문자가 원문자면 바로 뒤 공백을 U+2060 으로 치환
    if s[0] in CHOICE_MARKS and len(s) > 1 and s[1] == " ":
        return s[0] + U_WORD_JOINER + s[2:]
    return s


def compose_bogie_line(key: str, value: str) -> str:
    """ㄱ/ㄴ/ㄷ 뒤에 묶음 빈 칸 + 내용. `보기내용(내어쓰기)` 스타일 적용 전제."""
    return f"{key}.{U_WORD_JOINER}{value}".strip()


# ------------------------ 문제지 빌더 ------------------------

def add_styled(doc: HwpxDocument, text: str, style_map: dict[str, int], style_name: str | None = None) -> None:
    sid = style_map.get(style_name) if style_name else None
    if sid is not None:
        doc.add_paragraph(text, style_id_ref=sid)
    else:
        doc.add_paragraph(text)


def render_problem(doc: HwpxDocument, q: dict[str, Any], style_map: dict[str, int]) -> None:
    qno = q.get("question_number", "")
    stem = q.get("stem", "")
    passage = q.get("passage_text", "") or ""
    bogie = q.get("bogie_items", {}) or {}
    choices = q.get("choices", []) or []

    # 문항 번호 + 발문 → '문제' 스타일
    add_styled(doc, compose_stem_line(qno, stem), style_map, "문제")

    # 지문 — 박스 테두리 스타일이 있으면 '지문 (테두리)', 아니면 '박스내용(들여쓰기)'
    if passage:
        passage_style = "지문 (테두리)" if "지문 (테두리)" in style_map else "박스내용(들여쓰기)"
        for line in passage.splitlines():
            line = line.strip()
            if line:
                add_styled(doc, line, style_map, passage_style)

    # 보기 — '보기박스' 제목 + '보기내용(내어쓰기)' 내용
    if bogie:
        if "보기박스" in style_map:
            add_styled(doc, "<보 기>", style_map, "보기박스")
        for k, v in bogie.items():
            add_styled(doc, compose_bogie_line(k, v), style_map, "보기내용(내어쓰기)")

    # 선지 — '선택지' 스타일
    for c in choices:
        add_styled(doc, compose_choice_line(c), style_map, "선택지")

    # 문항 간 빈 줄
    doc.add_paragraph("")


def build_problem_hwpx(
    out_path: Path,
    title: str,
    questions: list[dict[str, Any]],
    *,
    template_override: Path | None = None,
    format_name: str = "default",
) -> Path:
    template_path = template_override or Path(FORMAT_TEMPLATES[format_name]["problem"])
    if not template_path.exists():
        raise FileNotFoundError(f"문제지 템플릿 없음: {template_path}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(template_path, out_path)

    style_map = build_style_map(out_path)
    doc = HwpxDocument.open(str(out_path))

    # 기존 문단 정리
    clean_body(doc)

    # 제목
    add_styled(doc, title, style_map, "제목" if "제목" in style_map else None)
    add_styled(doc, f"총 {len(questions)}문항 · 추리논증", style_map, None)
    doc.add_paragraph("")

    for q in questions:
        render_problem(doc, q, style_map)

    save_fn = getattr(doc, "save_to_path", None) or doc.save
    save_fn(str(out_path))
    return out_path


# ------------------------ 해설지 빌더 ------------------------

def render_solution(doc: HwpxDocument, q: dict[str, Any], style_map: dict[str, int]) -> None:
    qno = q.get("question_number", "")
    answer = q.get("answer", "")
    explanations = q.get("explanations", {}) or {}
    w_codes = q.get("w_codes_used", []) or []
    domain = q.get("domain", "")

    # 문항 번호 → '문항번호' 스타일 (해설지)
    add_styled(doc, f"{qno}번", style_map, "문항번호")
    # 정답 → '정답_10pt' 또는 '정답'
    answer_style = "정답_10pt" if "정답_10pt" in style_map else ("정답" if "정답" in style_map else None)
    add_styled(doc, f"정답 {answer}", style_map, answer_style)
    # 해시태그
    if w_codes or domain:
        tag_parts = [f"#{domain}"] if domain else []
        tag_parts += [f"#{w}" for w in w_codes]
        add_styled(doc, " ".join(tag_parts), style_map, "해시태그" if "해시태그" in style_map else None)

    # 정오판단 해설
    for k, v in explanations.items():
        add_styled(doc, f"{k}.{U_WORD_JOINER}{v}", style_map, "정오판단_설명" if "정오판단_설명" in style_map else None)

    doc.add_paragraph("")


def build_solution_hwpx(
    out_path: Path,
    title: str,
    questions: list[dict[str, Any]],
    *,
    template_override: Path | None = None,
    format_name: str = "default",
) -> Path:
    template_path = template_override or Path(FORMAT_TEMPLATES[format_name]["solution"])
    if not template_path.exists():
        raise FileNotFoundError(f"해설지 템플릿 없음: {template_path}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(template_path, out_path)

    style_map = build_style_map(out_path)
    doc = HwpxDocument.open(str(out_path))
    clean_body(doc)

    add_styled(doc, f"{title} 해설", style_map, "제목" if "제목" in style_map else None)
    doc.add_paragraph("")

    for q in questions:
        render_solution(doc, q, style_map)

    save_fn = getattr(doc, "save_to_path", None) or doc.save
    save_fn(str(out_path))
    return out_path


# ------------------------ CLI ------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", "-i", required=True, help="문항 JSON 경로")
    ap.add_argument("--output-problem", "-op", default=None, help="문제지 hwpx 출력 경로")
    ap.add_argument("--output-solution", "-os", default=None, help="해설지 hwpx 출력 경로")
    ap.add_argument(
        "--output", "-o", default=None,
        help="하위 호환 — 지정 시 문제지 경로로 사용 (해설지는 같은 이름에 '_해설' 접미사)",
    )
    ap.add_argument("--title", "-t", default="LEET 추리논증 문제지", help="문서 제목")
    ap.add_argument("--problem-only", action="store_true", help="문제지만 생성")
    ap.add_argument("--solution-only", action="store_true", help="해설지만 생성")
    ap.add_argument(
        "--format", "-f", choices=sorted(FORMAT_TEMPLATES.keys()), default="default",
        help="양식 선택: default(26추리) | jeonguk(전국 모의고사) | serva(서바이벌)",
    )
    ap.add_argument(
        "--problem-template", default=None,
        help="문제지 템플릿 직접 지정 (hwpx). --format보다 우선.",
    )
    ap.add_argument(
        "--solution-template", default=None,
        help="해설지 템플릿 직접 지정 (hwpx). --format보다 우선.",
    )
    args = ap.parse_args()

    src = Path(args.input)
    qs = load_questions(src)

    prob_path = (
        Path(args.output_problem) if args.output_problem
        else (Path(args.output) if args.output else None)
    )
    sol_path = (
        Path(args.output_solution) if args.output_solution
        else (prob_path.with_name(prob_path.stem + "_해설.hwpx") if prob_path else None)
    )

    prob_tpl = Path(args.problem_template) if args.problem_template else None
    sol_tpl = Path(args.solution_template) if args.solution_template else None

    if not args.solution_only:
        if prob_path is None:
            prob_path = Path(f"output/문제지_{args.format}.hwpx")
        build_problem_hwpx(
            prob_path, args.title, qs,
            template_override=prob_tpl,
            format_name=args.format,
        )
        print(f"[ok] 문제지({args.format}) → {prob_path}  ({len(qs)} 문항, {prob_path.stat().st_size} bytes)")
    if not args.problem_only:
        if sol_path is None:
            sol_path = Path(f"output/해설지_{args.format}.hwpx")
        build_solution_hwpx(
            sol_path, args.title, qs,
            template_override=sol_tpl,
            format_name=args.format,
        )
        print(f"[ok] 해설지({args.format}) → {sol_path}  ({len(qs)} 문항, {sol_path.stat().st_size} bytes)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
