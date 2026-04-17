"""
LEET-RA hwpx 출력기.

문항 JSON(samples/v2_5questions.json 형식 또는 단일 문항 dict)을 받아
한컴오피스 hwpx 파일을 생성한다.

OWPML 5.0 최소 구조로 직접 ZIP+XML 조립. 시대인재 양식의 완벽한 재현은 아니며,
2단 레이아웃 + 문항 번호 + 발문 + 지문 + 보기 + 선지의 논리적 구조만 갖춘다.
스타일 세부(폰트/여백/표 테두리 두께 등)는 한컴에서 열어 후처리 필요.

Usage:
    python export_hwpx.py --input samples/v2_5questions.json --output output/문제지.hwpx
    python export_hwpx.py --input samples/v2_5questions.json --output output/문제지.hwpx --title "LEET 추리논증 연습 1회"
"""
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape


HWPX_MIMETYPE = "application/hwp+zip"

VERSION_XML = """<?xml version="1.0" encoding="UTF-8"?>
<hv:HCFVersion xmlns:hv="http://www.hancom.co.kr/hwpml/2011/version" targetApplication="WORDPROC" major="5" minor="1" micro="0" buildNumber="0" os="0" xmlVersion="1.3" application="LEET-RA Exporter" appVersion="0.1.0"/>
"""

CONTAINER_XML = """<?xml version="1.0" encoding="UTF-8"?>
<ocf:container xmlns:ocf="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <ocf:rootfiles>
    <ocf:rootfile full-path="Contents/content.hpf" media-type="application/hwpml-package+xml"/>
  </ocf:rootfiles>
</ocf:container>
"""

SETTINGS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<hs:settings xmlns:hs="http://www.hancom.co.kr/hwpml/2011/settings"/>
"""

CONTENT_HPF = """<?xml version="1.0" encoding="UTF-8"?>
<opf:package xmlns:opf="http://www.idpf.org/2007/opf/" version="1.2" unique-identifier="hwpx-id">
  <opf:metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf-metadata="http://www.idpf.org/2007/opf">
    <opf-metadata:title>{title}</opf-metadata:title>
    <dc:language>ko</dc:language>
  </opf:metadata>
  <opf:manifest>
    <opf:item id="version" href="../version.xml" media-type="application/xml"/>
    <opf:item id="settings" href="../settings.xml" media-type="application/xml"/>
    <opf:item id="header" href="header.xml" media-type="application/xml"/>
    <opf:item id="section0" href="section0.xml" media-type="application/xml"/>
  </opf:manifest>
  <opf:spine>
    <opf:itemref idref="section0" linear="yes"/>
  </opf:spine>
</opf:package>
"""

HEADER_XML = """<?xml version="1.0" encoding="UTF-8"?>
<hh:head xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" version="1.3" secCnt="1">
  <hh:beginNum page="1" footnote="1" endnote="1" pic="1" tbl="1" equation="1"/>
  <hh:refList>
    <hh:fontfaces itemCnt="1">
      <hh:fontface lang="HANGUL" fontCnt="1">
        <hh:font id="0" face="함초롬바탕" type="TTF" isEmbedded="0"/>
      </hh:fontface>
    </hh:fontfaces>
    <hh:charProperties itemCnt="3">
      <hh:charPr id="0" height="1000" textColor="#000000" shadeColor="none" useFontSpace="0" useKerning="0" symMark="NONE" borderFillIDRef="2">
        <hh:fontRef hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>
        <hh:ratio hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>
        <hh:spacing hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>
        <hh:relSz hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>
        <hh:offset hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>
      </hh:charPr>
      <hh:charPr id="1" height="1400" textColor="#000000" shadeColor="none" useFontSpace="0" useKerning="0" symMark="NONE" borderFillIDRef="2">
        <hh:fontRef hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>
        <hh:ratio hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>
        <hh:spacing hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>
        <hh:relSz hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>
        <hh:offset hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>
        <hh:bold/>
      </hh:charPr>
      <hh:charPr id="2" height="900" textColor="#000000" shadeColor="none" useFontSpace="0" useKerning="0" symMark="NONE" borderFillIDRef="2">
        <hh:fontRef hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>
        <hh:ratio hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>
        <hh:spacing hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>
        <hh:relSz hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>
        <hh:offset hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>
      </hh:charPr>
    </hh:charProperties>
    <hh:paraProperties itemCnt="1">
      <hh:paraPr id="0" tabPrIDRef="0" condense="0" fontLineHeight="0" snapToGrid="1" suppressLineNumbers="0" checked="0">
        <hh:align horizontal="JUSTIFY" vertical="BASELINE"/>
        <hh:heading type="NONE" idRef="0" level="0"/>
        <hh:breakSetting breakLatinWord="KEEP_WORD" breakNonLatinWord="KEEP_WORD" widowOrphan="0" keepWithNext="0" keepLines="0" pageBreakBefore="0" lineWrap="BREAK"/>
        <hh:margin><hh:intent value="0"/><hh:left value="0"/><hh:right value="0"/><hh:prev value="0"/><hh:next value="0"/></hh:margin>
        <hh:lineSpacing type="PERCENT" value="160" unit="HWPUNIT"/>
        <hh:border borderFillIDRef="2" offsetLeft="0" offsetRight="0" offsetTop="0" offsetBottom="0" connect="0" ignoreMargin="0"/>
        <hh:autoSpacing eAsianEng="0" eAsianNum="0"/>
      </hh:paraPr>
    </hh:paraProperties>
    <hh:styles itemCnt="1">
      <hh:style id="0" type="PARA" name="바탕글" engName="Normal" paraPrIDRef="0" charPrIDRef="0" nextStyleIDRef="0" langID="1042" lockForm="0"/>
    </hh:styles>
  </hh:refList>
  <hh:forbiddenWordList itemCnt="0"/>
  <hh:compatibleDocument targetProgram="HWP2018"/>
</hh:head>
"""


def p(text: str, *, char_id: int = 0, para_id: int = 0, style_id: int = 0) -> str:
    """텍스트 1줄 단락(<hp:p>) XML 조각."""
    if not text:
        return (
            '<hp:p paraPrIDRef="{p}" styleIDRef="{s}" pageBreak="0" columnBreak="0" merged="0">'
            '<hp:run charPrIDRef="{c}"><hp:t></hp:t></hp:run></hp:p>'
        ).format(p=para_id, s=style_id, c=char_id)
    safe = escape(text)
    return (
        '<hp:p paraPrIDRef="{p}" styleIDRef="{s}" pageBreak="0" columnBreak="0" merged="0">'
        '<hp:run charPrIDRef="{c}"><hp:t>{t}</hp:t></hp:run></hp:p>'
    ).format(p=para_id, s=style_id, c=char_id, t=safe)


def render_question_xml(q: dict[str, Any]) -> list[str]:
    """단일 문항 → 단락 블록 목록."""
    out: list[str] = []
    qno = q.get("question_number", "")
    stem = q.get("stem", "")
    passage = q.get("passage_text", "")
    bogie = q.get("bogie_items", {}) or {}
    choices = q.get("choices", []) or []
    answer = q.get("answer", "")
    explanations = q.get("explanations", {}) or {}
    domain = q.get("domain", "")

    # 문항 헤더: [1. 영역] + 발문
    out.append(p(""))
    out.append(p(f"{qno}. [{domain}] {stem}", char_id=1))

    if passage:
        out.append(p(""))
        out.append(p("<지문>", char_id=1))
        for line in str(passage).splitlines():
            line = line.strip()
            if line:
                out.append(p(line))

    if bogie:
        out.append(p(""))
        out.append(p("<보기>", char_id=1))
        for k, v in bogie.items():
            out.append(p(f"{k}. {v}"))

    if choices:
        out.append(p(""))
        for c in choices:
            out.append(p(str(c)))

    if answer:
        out.append(p(""))
        out.append(p(f"[정답] {answer}", char_id=1))

    if explanations:
        out.append(p("[해설]", char_id=1))
        for k, v in explanations.items():
            out.append(p(f"{k}) {v}", char_id=2))

    return out


def build_section_xml(title: str, questions: list[dict[str, Any]]) -> str:
    """section0.xml 전체."""
    head = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<hs:sec xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" '
        'xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph">\n'
    )
    body: list[str] = []
    # 제목
    body.append(p(title, char_id=1))
    body.append(p(""))
    body.append(p(f"총 {len(questions)}문항", char_id=2))
    body.append(p(""))
    # 문항
    for q in questions:
        body.extend(render_question_xml(q))
        body.append(p(""))
    tail = "</hs:sec>\n"
    return head + "\n".join(body) + "\n" + tail


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


def write_hwpx(out_path: Path, title: str, questions: list[dict[str, Any]]) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    section_xml = build_section_xml(title, questions)
    content_hpf = CONTENT_HPF.format(title=escape(title))

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # mimetype 은 반드시 첫 엔트리, 무압축
        zf.writestr(
            zipfile.ZipInfo("mimetype"),
            HWPX_MIMETYPE,
            compress_type=zipfile.ZIP_STORED,
        )
        zf.writestr("version.xml", VERSION_XML)
        zf.writestr("settings.xml", SETTINGS_XML)
        zf.writestr("META-INF/container.xml", CONTAINER_XML)
        zf.writestr("Contents/content.hpf", content_hpf)
        zf.writestr("Contents/header.xml", HEADER_XML)
        zf.writestr("Contents/section0.xml", section_xml)
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
    print(f"[ok] wrote {dst}  ({len(qs)} 문항)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
