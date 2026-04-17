---
name: ra-exporter
description: "LEET 추리논증 문항 JSON을 시대인재 양식 hwpx로 출력 — default(26추리) / jeonguk(전국) / serva(서바) 3종 양식 + MCP 인터랙티브 편집"
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
  - "서바 양식"
  - "전국 양식"
  - "서바로"
  - "전국으로"
  - "모의고사 양식"
  - "시대인재 양식"
argument-hint: "<양식> (default | jeonguk | serva)"
requires: ["omc"]
---

# RA-EXPORTER: 문항 → hwpx 출력기 (시대인재 3종 양식)

**OMC 전제.** 두 경로 지원:

1. **배치 출력 (기본)** — `leet_ra/exporter/export_hwpx.py`가 **빈 템플릿**(시대인재 실제 제작본에서 `<hp:t>` 텍스트만 제거한 파일)을 복제 후 본문에 우리 문항을 스타일 적용하여 추가한다. 표·2단 컬럼·바탕쪽·헤더·스타일 세트 유지.
2. **인터랙티브 편집 (선택)** — 프로젝트 `.mcp.json`에 등록된 `hwpx` MCP 서버(33개 도구)로 Claude가 직접 문서 조작. 표 셀 편집, 특정 문구 교체, 양식 폼 채우기 등에 유용.

## When to Activate

- ra-review 판정 ❌ 0개 통과 후 문제지 출력 요청
- "hwpx로 뽑아줘", "한글로 출력", "문제지 만들어줘", "서바 양식으로", "전국 양식으로" 등
- 풀 파이프라인의 마지막 단계

## 전제 조건

- `pip install python-hwpx hwpx-mcp-server python-docx` (또는 `bash setup.sh`)
- 문항 JSON 스키마: `question_number`, `domain`, `stem`, `passage_text`, `has_bogie`, `bogie_items`, `choices`, `answer`, `explanations`, `w_codes_used`
- review ❌ 존재 시 export 금지
- 빈 템플릿 파일(`leet_ra/templates/*_빈.hwpx`) 존재 — 없으면 `python3 leet_ra/exporter/build_blank_template.py` 실행하여 재생성

## 양식 선택 (3종)

사용자 자연어에서 양식을 자동 판별한 뒤 `--format`으로 전달:

| 자연어 | `--format` | 문제지 템플릿 | 해설지 템플릿 |
|--------|-----------|-------------|-------------|
| (명시 없음) · "시대인재 양식" | `default` | `templates/시대인재_문제지_빈.hwpx` (84KB) | `templates/시대인재_해설지_빈.hwpx` (50KB) |
| "전국 양식" · "전국으로" · "전국 모의고사" | `jeonguk` | `templates/전국_문제지_빈.hwpx` (366KB) | `templates/전국서바_해설지_빈.hwpx` (61KB) |
| "서바 양식" · "서바로" · "서바이벌" | `serva` | `templates/서바_문제지_빈.hwpx` (366KB) | `templates/전국서바_해설지_빈.hwpx` (61KB) |

**판별 규칙**: "서바" 단어가 있으면 `serva`, "전국" 단어가 있으면 `jeonguk`, 그 외는 `default`.

## Workflow

### 경로 1: 배치 출력 (기본)

```bash
# 기본 양식 (26추리 간결)
python3 leet_ra/exporter/export_hwpx.py \
  --input <questions.json> \
  --format default \
  --title "<사용자 지정 제목>"

# 전국 모의고사
python3 leet_ra/exporter/export_hwpx.py -i <json> -f jeonguk -t "<제목>"

# 서바이벌
python3 leet_ra/exporter/export_hwpx.py -i <json> -f serva -t "<제목>"

# docx 대체 출력 (옵션)
python3 leet_ra/exporter/export_docx.py -i <json> -o output/<레이블>.docx -t "<제목>"
```

기본 출력 경로: `output/문제지_<format>.hwpx`, `output/해설지_<format>.hwpx`.
경로 오버라이드: `--output-problem`, `--output-solution`.
템플릿 직접 지정: `--problem-template`, `--solution-template` (우선순위 높음).

### 경로 2: MCP 서버로 인터랙티브 편집

`.mcp.json`이 레포 루트에 있어 `claude` 실행 시 자동 등록. 도구 prefix `mcp__hwpx__*`.

주요 도구 (33개 중 핵심):

| 도구 | 용도 |
|------|------|
| `create_document` / `add_heading` / `add_paragraph` / `add_table` | 새 hwpx 구축 |
| `search_and_replace` / `batch_replace` | 텍스트 치환 (스타일 보존) |
| `set_table_cell_text` / `get_table_text` | 표 셀 읽기/쓰기 |
| `fill_by_path` / `find_cell_by_label` | 한국 양식/폼 자동 채우기 |
| `get_document_info` / `get_document_text` / `get_document_outline` | 조회 |
| `hwpx_to_markdown` / `hwpx_to_html` / `hwpx_extract_json` | 역변환 |
| `insert_paragraph` / `delete_paragraph` / `add_page_break` / `add_memo` | 국소 편집 |

**인터랙티브 시나리오**:
```
사용자: "output/문제지_serva.hwpx 3번 문항 해설 바꿔줘 — 정답을 ④로"
→ Claude: mcp__hwpx__search_and_replace 로 해당 문구 치환
```

## 빈 템플릿 생성 방식

`leet_ra/exporter/build_blank_template.py`:
- ZIP+XML 수준에서 `<hp:t>...</hp:t>` 내부 텍스트를 정규식으로 일괄 제거
- 표/2단 컬럼/바탕쪽/헤더/스타일 세트 그대로 유지
- 한 번 실행 후 결과물(`templates/*_빈.hwpx`)을 레포에 커밋해둠

재생성 필요 시: `python3 leet_ra/exporter/build_blank_template.py`

## 시대인재 스타일 자동 매핑

exporter는 `build_style_map()`으로 템플릿 hwpx의 `header.xml`에서 style name → id 매핑을 빌드 후 다음 스타일명으로 `add_paragraph(text, style_id_ref=...)` 호출:

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
- **고정폭 빈 칸(U+00A0)**: 컴포저 함수 상수로 준비
- **들여쓰기**: 공백 아닌 스타일(`박스내용(들여쓰기)`, `보기내용(내어쓰기)`)로 처리
- **선지 공백**: `'① ㄱ'` → `'①⁠ㄱ'` 자동 치환
- 추가 치환(`아니한다→않는다`, `만 원` 띄어쓰기)은 후속 `compose_*` 함수로 확장 가능

## 품질 체크

- 출력 파일 존재 + 크기 > 0
- `HwpxDocument.open()` + `export_text()`로 readback
- 문항 수가 입력 JSON과 일치

## 주의 사항

- 빈 템플릿은 "본문 텍스트만 제거"된 상태. 앞쪽에 시대인재 양식의 빈 표/레이아웃 슬롯이 그대로 있고, 그 뒤에 우리 문항이 스타일 적용되어 추가됨. 필요 시 한컴에서 후처리.
- review 미통과 문항 export 금지.
- MCP 서버가 뜨지 않으면 `pip install --upgrade python-hwpx hwpx-mcp-server` 후 `claude` 재시작.
