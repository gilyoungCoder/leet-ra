---
name: ra-exporter
description: "LEET 추리논증 문항 JSON을 hwpx(한컴) / docx로 출력 — ra-review ✅ 이후 최종 배포 포맷 생성"
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

**OMC 전제.** 이 스킬은 `leet_ra/exporter/export_hwpx.py` 와 `export_docx.py` 를 호출하여 최종 배포 포맷을 생성한다. review ✅ 통과 후 호출하는 최종 단계.

## When to Activate

- ra-review 판정 ❌ 0개 통과 후
- "hwpx로 뽑아줘", "한글로 출력", "문제지 만들어줘" 등의 자연어 요청
- 풀 파이프라인의 마지막 단계

## 전제 조건

- `samples/*.json` 또는 ra-design/review 출력의 문항 JSON이 준비되어 있어야 한다
- JSON 스키마: `question_number`, `domain`, `stem`, `passage_text`, `has_bogie`, `bogie_items`, `choices`, `answer`, `explanations`, `w_codes_used`
- review ❌ 존재 시 export 금지. review 먼저 통과시킨다.

## Workflow

### Step 1: JSON 수집

검수 통과한 문항 세트를 임시 JSON으로 수집한다:
- 이전 대화의 design/review 결과를 파싱하여 `output/tmp_<timestamp>.json` 으로 저장
- 또는 사용자가 기존 JSON 경로를 지정한 경우 해당 경로 사용

### Step 2: Exporter 호출 (Bash 직접 실행)

**포맷 선택**:
- 기본: hwpx (한컴오피스 바로 열림)
- 옵션: docx (python-docx, 한컴에서도 열림. 변환 보험)

```bash
# hwpx 출력
python3 leet_ra/exporter/export_hwpx.py \
  --input <questions.json> \
  --output output/<레이블>_문제지.hwpx \
  --title "<사용자 지정 제목>"

# docx 출력 (병행 또는 대체)
python3 leet_ra/exporter/export_docx.py \
  --input <questions.json> \
  --output output/<레이블>_문제지.docx \
  --title "<사용자 지정 제목>"
```

### Step 3: 결과 전달

생성된 파일 경로를 사용자에게 전달한다:
```
✅ 출력 완료
- output/LEET-RA_2026-04-17_문제지.hwpx  (N 문항)
- output/LEET-RA_2026-04-17_문제지.docx  (동일 내용)
```

사용자가 한컴오피스에서 hwpx를 열어 검토/저장한다.

## 출력 구성

각 문항은 다음 순서로 렌더링된다:

```
1. [영역] 발문
<지문>
(지문 본문 여러 줄)

<보기>
ㄱ. …
ㄴ. …
ㄷ. …

① / ② / ③ / ④ / ⑤

[정답] N
[해설]
ㄱ) …
ㄴ) …
ㄷ) …
```

## 주의 사항

- **hwpx는 OWPML 최소 구조로 생성**된다. 시대인재 양식의 스타일(폰트/여백/2단 컬럼/표 테두리)은 자동 재현되지 않으며, 한컴오피스에서 열어 스타일 후처리가 필요할 수 있다.
- **시대인재 양식 완벽 재현**을 원하면 `leet_ra/templates/시대인재_문제지.hwpx` (한컴에서 한 번 변환해둔 템플릿) 를 배치하고 exporter 스크립트를 템플릿 기반 치환 모드로 확장한다 (향후 과제).
- docx는 python-docx로 2단 레이아웃까지 자동 세팅. 한컴오피스에서 열고 `다른 이름으로 저장 → HWP`로 바로 변환 가능.
- **review 미통과 문항 export 금지.** ❌ 있는 상태에서 export 요청이 오면 "review 먼저 통과시키세요" 응답.

## 품질 체크

- 출력 파일 존재 확인 (파일 크기 > 0)
- hwpx 내부 구조 검증: `mimetype`, `version.xml`, `META-INF/container.xml`, `Contents/section0.xml` 존재
- 문항 수가 입력 JSON과 일치

## Notes

- 출력 디렉터리: `output/` (레포 .gitignore에 포함 — 생성물은 커밋되지 않음)
- 스크립트 수정은 `leet_ra/exporter/*.py` 편집 후 다음 실행 시 반영.
- 향후: 시대인재 hwpx 템플릿 슬롯 치환 방식, 교열 매뉴얼 자동 반영, 2단 컬럼 hwpx 정밀화.
