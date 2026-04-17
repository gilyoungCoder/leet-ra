---
name: ra-exporter
description: "LEET 추리논증 문항 JSON을 hwpx(한컴) / docx로 출력 — python-hwpx 기반 배치 + hwpx MCP 서버 기반 인터랙티브 편집 지원"
triggers:
  - "hwpx로"
  - "hwp로"
  - "한글로 출력"
  - "한글 파일"
  - "문제지로 뽑아"
  - "docx로"
  - "워드로"
  - "출력해줘"
  - "export"
  - "exporter"
  - "문제지 만들어줘"
argument-hint: "(review 통과한 문항 JSON)"
requires: ["omc"]
---

# RA-EXPORTER: 문항 → hwpx / docx 출력기

**OMC 전제.** 두 경로 지원:

1. **배치 출력 (기본)** — `leet_ra/exporter/export_hwpx.py` 가 **시대인재 양식 hwpx 템플릿을 복제 → 본문 XML 비우기(`sections[0].element` children clear) → 시대인재 스타일명으로 문단 삽입** 방식으로 문제지/해설지를 동시 생성한다. 기본 출력 2개:
   - `output/<레이블>_문제지.hwpx` (27추리_출제 양식 템플릿 기반)
   - `output/<레이블>_해설지.hwpx` (전국&서바 해설지 템플릿 기반)
2. **인터랙티브 편집 (선택)** — 프로젝트 `.mcp.json`에 등록된 `hwpx` MCP 서버(33개 도구)로 Claude가 직접 문서 조작. 표 셀 편집, 특정 문구 교체, 양식 폼 채우기 등에 유용.

## 템플릿 파일

| 용도 | 경로 | 베이스 원본 |
|------|------|-----------|
| 문제지 | `leet_ra/templates/문제지_템플릿.hwpx` | `27추리_출제 양식_260206.hwpx` |
| 해설지 | `leet_ra/templates/해설지_템플릿.hwpx` | `전국&서바_해설지.hwpx` |

## 시대인재 스타일 자동 매핑

exporter는 `build_style_map()`으로 템플릿 hwpx 내부 `header.xml`에서 style name → id 매핑을 빌드한 뒤 다음 스타일명으로 `add_paragraph(text, style_id_ref=...)` 호출:

| 블록 | 문제지 스타일 | 해설지 스타일 |
|------|------------|-------------|
| 문항 번호 + 발문 | `문제` | `문항번호` |
| 지문 본문 | `지문 (테두리)` 우선, 없으면 `박스내용(들여쓰기)` | - |
| 보기 제목 | `보기박스` | - |
| 보기 ㄱ/ㄴ/ㄷ | `보기내용(내어쓰기)` | - |
| 선지 ①②③④⑤ | `선택지` | - |
| 정답 | - | `정답_10pt` / `정답` |
| 해시태그 | - | `해시태그` |
| 정오판단 설명 | - | `정오판단_설명` |

## 교열 매뉴얼(추리논증ver) 자동 반영

- **묶음 빈 칸(U+2060)**: 문항 번호↔발문, `①②③④⑤`↔내용, `ㄱ./ㄴ./ㄷ.`↔내용 자동 삽입
- **고정폭 빈 칸(U+00A0)**: 필요 시 삽입 (컴포저 함수로 확장 가능)
- **들여쓰기**: 공백 아닌 스타일(`박스내용(들여쓰기)`, `보기내용(내어쓰기)`)로 처리
- **선지와 내용 사이 공백**: 원본 `'① ㄱ'` → `'①⁠ㄱ'` (묶음 빈 칸)으로 치환
- 추가 규정 치환(`아니한다→않는다`, `만 원` 띄어쓰기)은 후속 `compose_*` 함수로 확장 가능

## When to Activate

- ra-review 판정 ❌ 0개 통과 후 문제지 출력 요청
- "hwpx로 뽑아줘", "한글로 출력", "문제지 만들어줘" 등
- 풀 파이프라인의 마지막 단계

## 전제 조건

- `pip install python-hwpx hwpx-mcp-server` 완료
- 문항 JSON 스키마: `question_number`, `domain`, `stem`, `passage_text`, `has_bogie`, `bogie_items`, `choices`, `answer`, `explanations`, `w_codes_used`
- review ❌ 존재 시 export 금지

## Workflow

### 경로 1: 배치 출력 (기본 추천)

review 통과한 문항 세트를 한 번에 파일로 내보낸다.

```bash
python3 leet_ra/exporter/export_hwpx.py \
  --input <questions.json> \
  --output output/<레이블>_문제지.hwpx \
  --title "<사용자 지정 제목>"

python3 leet_ra/exporter/export_docx.py \
  --input <questions.json> \
  --output output/<레이블>_문제지.docx \
  --title "<사용자 지정 제목>"
```

결과 파일 경로를 사용자에게 반환.

### 경로 2: MCP 서버로 인터랙티브 편집

`.mcp.json`이 레포 루트에 있으므로 `claude` 실행 시 자동 등록. 도구 prefix는 `mcp__hwpx__*`.

주요 도구:

| 도구 | 용도 |
|------|------|
| `create_document` | 새 HWPX 문서 생성 |
| `add_heading` | 제목/헤딩 추가 (level 1~6) |
| `add_paragraph` | 문단 추가 |
| `add_table` | 표 추가 (data 2D 배열) |
| `set_table_cell_text` | 표 셀 텍스트 변경 |
| `search_and_replace` | 텍스트 치환 (스타일 보존) |
| `batch_replace` | 여러 문구 순차 치환 |
| `fill_by_path` | `성명 > right` 같은 경로 문법으로 폼 칸 채움 |
| `find_cell_by_label` | 라벨 인접 셀 탐지 (한국 양식/템플릿용) |
| `hwpx_to_markdown` / `hwpx_to_html` / `hwpx_extract_json` | 역변환 |
| `get_document_info` / `get_document_text` / `get_document_outline` | 조회 |
| `insert_paragraph` / `delete_paragraph` | 위치 지정 문단 조작 |
| `add_page_break` / `add_memo` / `remove_memo` | 페이지/메모 |

**인터랙티브 시나리오 예**:
```
사용자: "output/leet_v2_real.hwpx 3번 문항 해설을 교열해줘"
→ Claude: mcp__hwpx__search_and_replace 로 해당 부분 치환
```

## 출력 구성

각 문항은 다음 순서로 렌더링:

```
N. [영역] 발문
<지문>
(지문 본문)

<보기>
ㄱ. …
ㄴ. …
ㄷ. …

①
②
③
④
⑤

[정답] N
[해설]
ㄱ) …
ㄴ) …
ㄷ) …
```

## 품질 체크

- 출력 파일 존재 + 크기 > 0
- `python-hwpx`의 `HwpxDocument.open()` + `export_text()`로 readback 검증
- 문항 수가 입력 JSON과 일치

## 주의 사항

- **hwpx는 python-hwpx `HwpxDocument.new()` 기반.** 한컴오피스에서 바로 열림 (Open XML 표준 준수).
- 시대인재 양식의 **스타일(폰트/여백/2단 컬럼/표 테두리)까지 완벽 재현은 아님**. 한컴에서 열어 스타일 후처리 필요.
- 완벽 재현을 원하면 `leet_ra/templates/시대인재_문제지.hwpx` (한컴에서 변환해둔 실물 템플릿)를 배치하고 `search_and_replace` / `fill_by_path` MCP 도구로 슬롯 치환 방식으로 확장 가능.
- review 미통과 문항 export 금지.

## Notes

- 출력 디렉터리: `output/` (gitignore — 생성물 커밋 X)
- MCP 서버 실행: `hwpx-mcp-server --transport stdio` (자동, `.mcp.json` 참조)
- 문제 발생 시 `pip install --upgrade python-hwpx hwpx-mcp-server`
