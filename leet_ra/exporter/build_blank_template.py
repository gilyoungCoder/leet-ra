"""
시대인재 실제 문제지/해설지 hwpx에서 '텍스트만 지우고 레이아웃·스타일·표를 그대로 유지한
빈 템플릿'을 생성한다.

데이터 소스(leet_ra/data/):
  - 26추리_전국_07회_문제.hwpx  →  templates/시대인재_문제지_빈.hwpx
  - 26추리_전국_07회_해설.hwpx  →  templates/시대인재_해설지_빈.hwpx

구현: hwpx는 ZIP+XML이므로, ZIP 내부의 `Contents/section*.xml`을 읽어
`<hp:t>...</hp:t>` 태그 내부 텍스트를 전부 비워 다시 쓴다. python-hwpx의
dirty tracking 이슈(iter_runs 범위 한계)에 의존하지 않는다.

Usage:
    python leet_ra/exporter/build_blank_template.py
"""
from __future__ import annotations

import re
import shutil
import zipfile
from pathlib import Path

SOURCES = [
    ("leet_ra/data/26추리_전국_07회_문제.hwpx", "leet_ra/templates/시대인재_문제지_빈.hwpx"),
    ("leet_ra/data/26추리_전국_07회_해설.hwpx", "leet_ra/templates/시대인재_해설지_빈.hwpx"),
]

# <hp:t ...>...</hp:t> / <hp:t/> 형태 — ns prefix 는 hp 고정 (시대인재 hwpx 확인)
RE_HP_T = re.compile(r"(<hp:t(?:\s[^>]*)?>)(.*?)(</hp:t>)", flags=re.DOTALL)


def blank_xml(xml: str) -> tuple[str, int]:
    """section XML에서 <hp:t>...</hp:t> 내부 텍스트를 비운다."""
    count = 0

    def sub(m: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return m.group(1) + m.group(3)

    return RE_HP_T.sub(sub, xml), count


def blank_out(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dst)

    total = 0
    with zipfile.ZipFile(dst, "r") as rz:
        entries: list[tuple[zipfile.ZipInfo, bytes]] = []
        for info in rz.infolist():
            data = rz.read(info.filename)
            if info.filename.startswith("Contents/section") and info.filename.endswith(".xml"):
                xml = data.decode("utf-8", errors="replace")
                new_xml, n = blank_xml(xml)
                total += n
                data = new_xml.encode("utf-8")
            entries.append((info, data))

    # 새 ZIP 으로 덮어쓰기 (mimetype 은 첫 엔트리 + 무압축 유지)
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED) as wz:
        for info, data in entries:
            if info.filename == "mimetype":
                wz.writestr(zipfile.ZipInfo("mimetype"), data, compress_type=zipfile.ZIP_STORED)
            else:
                new_info = zipfile.ZipInfo(info.filename)
                new_info.compress_type = zipfile.ZIP_DEFLATED
                wz.writestr(new_info, data)

    print(f"[ok] {src.name}  →  {dst}  ({dst.stat().st_size:,} bytes, blanked {total} <hp:t> nodes)")


def main() -> int:
    root = Path(".")
    for src_rel, dst_rel in SOURCES:
        src = root / src_rel
        dst = root / dst_rel
        if not src.exists():
            print(f"[skip] {src} not found")
            continue
        blank_out(src, dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
