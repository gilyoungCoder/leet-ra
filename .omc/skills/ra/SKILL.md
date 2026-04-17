---
name: ra
description: LEET 추리논증 출제 시스템 — 소재·지문·분석·문항·검수 단계별 RAG 주입 + opus 에이전트 오케스트레이션
triggers:
  - "LEET"
  - "리트"
  - "추리논증"
  - "법학적성"
  - "소재 찾아"
  - "소재 발굴"
  - "지문 만들어"
  - "지문 생성"
  - "문항 설계"
  - "검수"
  - "풀 파이프라인"
  - "sourcer"
  - "analyze"
  - "design"
  - "review"
  - "ra-pipeline"
  - "40문항"
  - "세트 만들어"
argument-hint: "<영역 또는 소재 또는 지문 텍스트>"
requires: ["omc"]
---

# LEET-RA: 추리논증 출제 시스템 (마스터 오케스트레이터)

**OMC 전제 시스템.** 모든 하위 에이전트는 Claude Code의 Agent 도구로 opus 서브에이전트로 spawn되며, 각 단계마다 `leet_ra/data/`의 기출 JSON에서 **타깃 RAG**를 주입한다.

## When to Activate

- LEET/리트/추리논증/법학적성 관련 출제 작업 요청
- "지문 만들어줘", "문항 설계해줘", "검수해줘", "풀 파이프라인" 등의 자연어 명령
- sourcer/analyze/design/review 키워드
- 세트 단위 요청("법 3문항", "40문항 세트 만들어")

## RAG 주입 원칙 (핵심)

각 에이전트는 spawn 직전에 관련 few-shot만 타깃 주입한다.

| 에이전트 | 주입 대상 | 선별 규칙 |
|---------|---------|----------|
| ra-sourcer | `2024/2025_merged.json`의 `passage_text` 2~3개 | 영역 → leet_type 매핑 (법→D*, 인문→A*, 사회→C*/E*, 과학→C*, 논쟁→E*) |
| ra-analyze | 동일 유형 기출 2개 전체 구조 + W코드 21종 메타 + `taxonomy.md` | 사전 유형 추정 → 매칭 leet_type의 questions |
| ra-design | analyze W코드 후보별 examples 2개씩 + 선지 구성 규칙 16개 + AP/CP 패턴 | **타깃 W코드에만** 매칭 (21개 전체 뿌리지 않음) |
| ra-review | 동일 leet_type 고품질 기출 1~2개 + W코드 진단 카탈로그 + 16규칙 체크리스트 | 기대 수준 비교 + Rule별 검증 |
| ra-exporter | (RAG 불필요. Bash로 `leet_ra/exporter/export_hwpx.py` 실행) | review ✅ 문항 JSON → 시대인재 3종 양식 hwpx (default/jeonguk/serva) + docx |

**가중치 원칙 90/10**: 2025 기출 우선, 2024는 보충.

## Workflow

### Step 0: 모드 자동 판별

| 입력 유형 | 판별 기준 | 모드 |
|----------|----------|------|
| 500자+ 지문 | 지문이 붙여넣기됨 | **분석 모드** (analyze → design → review) |
| 짧은 키워드/영역명 | "특별법 환경", "귀납 추리" 등 | **생성 모드** (sourcer → analyze → design → review) |
| 세트 요청 | "법 3문항", "40문항 1세트" | **세트 모드** (sourcer 반복 → …) |
| 명시적 단계 지정 | "analyze만", "검수만" | **단일 모드** |

### Step 1: 에이전트 위임 체인

```
[생성 모드]
  ra-sourcer (opus) — 영역 기반 passage RAG 주입 → 지문 초안
         ↓ (사용자 승인)
  ra-analyze (opus) — 유형 매칭 기출 + W코드 카탈로그 주입 → 분석 데이터
         ↓
  ra-design (opus) — W코드 타깃 few-shot + 16규칙 주입 → 문항 세트
         ↓
  ra-review (opus, 독립 세션!) — 기대 수준 기출 + 진단 카탈로그 주입 → 검수 리포트
         ↓
  ❌ 0개 → 확정 / ❌ 있음 → 해당 단계로 루프
         ↓ (확정 후, 출력 요청 시)
  ra-exporter — "서바/전국/기본" 양식 자동 판별 → export_hwpx.py --format {default|jeonguk|serva}
               → output/문제지_<fmt>.hwpx + output/해설지_<fmt>.hwpx
```

## 양식 선택 (ra-exporter 전용)

사용자 자연어에서 양식 자동 판별:

| 자연어 | 양식 |
|--------|------|
| "서바 양식" / "서바로" | `serva` (서바이벌 모의고사) |
| "전국 양식" / "전국으로" | `jeonguk` (전국 모의고사) |
| 그 외 / "시대인재 양식" / 명시 없음 | `default` (26추리 실제 제작본 기반) |

자세한 매핑·스타일·교열 규칙은 `.omc/skills/ra-exporter/SKILL.md` 참조.

### Step 2: 각 에이전트 spawn은 하위 스킬 위임

메인 컨텍스트는 모드 판별과 데이터 릴레이만 담당. 실제 프롬프트 조립 + RAG 필터링은 각 하위 스킬이 자체적으로 수행 (ra-sourcer, ra-analyze, ra-design, ra-review SKILL.md 참조).

## 핵심 원칙

1. **sourcer가 병목이다.** 좋은 소재 = 좋은 문항.
2. **analyze가 엔진이다.** 출제 포인트 추출이 전체 품질을 결정.
3. **review는 독립 에이전트.** design과 같은 세션에서 절대 실행하지 않는다.
4. **모든 핵심 에이전트는 opus.**
5. **RAG는 타깃 주입.** 관련 없는 예시는 오염을 일으킨다.
6. **기출 가중치 90/10.** 최근 3~5개년 기출 90% 비중.

## 지문 빌드 3대 원칙 (전 에이전트 공통 — 절대 규칙)

1. **일반화**: 고교 수준 배경지식으로 지문 자체는 편하게 이해 가능. 변별은 선지 판단에서 발생.
2. **실명 금지**: 실제 학자명·이론명 절대 금지. '갑/을/병', `<이론>`, 'X국' 등으로 일반화.
3. **한국어 전용**: 영어·외국어·학술 약어 금지.

## 영역별 절대 금지

| 영역 | 절대 금지 |
|------|---------|
| **법 (규범)** | 민법·형법·행정법 등 변호사시험 빈출 소재 ❌. 특별법 영역 사용. |
| **인문** | 기호 논리학 과도 사용 ❌. '대우' 정도만 허용. |
| **사회/과학** | 특별한 금지 없음. |

## Examples

```
# 영역 지정 생성 (생성 모드)
사용자: 특별법 영역으로 법 1문항 만들어줘
  → ra가 ra-sourcer(D1/D2/D3 기출 주입) spawn

# 세트 모드
사용자: 인문 5문항 세트 만들어줘
  → ra-sourcer × 5 (A1/A2/A3 기출 주입, 중복 방지 리스트 전달)

# 분석 모드
사용자: 이 지문으로 문항 만들어줘 [지문]
  → ra-analyze(유형 추정 → 동일 유형 기출 2개 주입) → ra-design → ra-review

# 단일 에이전트
사용자: 검수해줘
  → ra-review(기대 수준 기출 + 진단 카탈로그 주입, 독립 세션)
```

## Notes

- 프롬프트 수정은 `leet_ra/prompts/*.md` 파일 편집. 재설치 불필요.
- 데이터 수정은 `leet_ra/data/*.json` 편집. 자동 반영.
- 버전: sourcer v1.6, analyze/design/review v1.5.
- 향후: DPO 세칙 보강, hwp 출력 파이프라인, 세트 간 소재 중복 방지 고도화.
