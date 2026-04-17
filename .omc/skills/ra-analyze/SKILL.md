---
name: ra-analyze
description: "LEET 추리논증 지문 분석기 (Agent A v1.5) — 유형 매핑 RAG + W코드 21종 카탈로그로 구조·출제 포인트 해부"
triggers:
  - "분석해줘"
  - "지문 분석"
  - "analyze"
  - "Agent A"
  - "출제 포인트"
  - "논증 구조"
argument-hint: "<지문 텍스트>"
requires: ["omc"]
---

# RA-ANALYZE: 지문 분석기 (Agent A)

**OMC 전제.** Agent 도구로 opus 서브에이전트를 spawn한다.

LEET 추리논증 지문을 해부하여 **구성요소 코드**, **출제 포인트**, **W코드 매핑**, **논증 구조**를 구조화된 데이터로 출력한다.
design 단계의 **유일한 입력**이 되므로 이 에이전트의 품질이 문항 품질을 결정한다.

## When to Activate

- 지문이 준비된 상태에서 문항 설계에 들어가기 전 단계
- 사용자가 "분석해줘", "출제 포인트 뽑아줘" 등을 요청할 때
- 풀 파이프라인의 2단계 (sourcer 이후)

## Workflow

### Step 1: 프롬프트 및 유형 체계 로드

- Read `leet_ra/prompts/analyze.md` 전문
- Read `leet_ra/taxonomy/taxonomy.md` 전문

### Step 1b: 유형 사전 추정 + 기출 분석 예시 + W코드 카탈로그 RAG 주입 (필수)

**사전 추정 규칙** (본 spawn 전에 Claude 메인 컨텍스트에서 경량 판별):

| 지문 특징 | 예상 leet_type |
|---------|---------------|
| 견해 독립/대화 + 강화·약화 발문 | E1, E2 |
| 규정(R) + 사례(C) | D1 |
| 판례·해석 대립 | D2, D3 |
| 논증 1개 + 전제·결론 구조 | A1, A2, A3 |
| 명제·양화 조건문 | B1, B2 |
| 배치·규칙 복원 퍼즐 | B3 |
| 인과·유비·귀납 | C1, C2, C3 |

**주입 절차**:

1. Read `leet_ra/data/2025_merged.json` → `questions` (가중치 90%)
2. Read `leet_ra/data/2024_merged.json` → `questions` (가중치 10%)
3. 추정 `leet_type` 후보 1~2개와 일치하는 questions 중 2개 선별 (2025 우선)
4. 각 선별 질문의 **전체 구조**를 주입:
   - `leet_type`, `question_type`, `passage_topic`, `passage_components`
   - `passage_text`, `stem`, `choices`, `choices_box` (있는 경우), `view_format`, `views` (있는 경우)
5. Read `leet_ra/data/w_codes_merged.json` → `w_codes` 배열
6. W코드 21개를 메타 카탈로그로 주입: 각 항목의 `code`, `name_ko`, `description`, `frequency_total`
   (여기서는 examples 미주입. design 단계에서 상세 주입함.)

### Step 2: 에이전트 Spawn

```
Agent(
  name="ra-analyze",
  description="LEET 추리논증 지문 분석",
  model="opus",
  mode="auto",
  prompt="{analyze.md 전문}\n\n"
        "## 유형 체계 참조\n\n{taxonomy.md}\n\n"
        "## W코드 21종 카탈로그 (매핑 후보)\n\n{w_codes 메타 블록}\n\n"
        "## 기출 유사 유형 분석 참조 (동일 leet_type 2개)\n\n{questions 전체 구조 블록}\n\n"
        "## 분석 대상 지문\n\n{지문}"
)
```

### Step 3: 결과 전달

구조화된 분석 데이터를 사용자에게 전달한다. design의 유일한 입력이므로 빈 필드가 없어야 한다.

## LEET 유형 체계 (5대 영역)

| 대유형 | 소분류 | 핵심 |
|--------|--------|------|
| A. 논증 분석·평가 | A1 전제·결론 / A2 강화·약화 / A3 오류 식별 | 숨은 전제, 논증 평가 |
| B. 연역 추리 | B1 명제 논리 / B2 양화 논리 / B3 논리 퍼즐 | 조건문, 규칙 복원, 배치 |
| C. 귀납·유비 추리 | C1 귀납 / C2 유비 / C3 인과 | 밀의 방법, 구조적 유사성 |
| D. 법적 추론 | D1 법 적용 / D2 판례 / D3 다견해 | 조문→사례, 해석 대립 |
| E. 논쟁 평가 | E1 다입장 강화·약화 / E2 입장 비교 | 3자 대립, 일치/차이 |

## 품질 체크

- 구성요소 코드 전량 태깅 (P/V/R/C/PR/AS/MR/MK/T)
- 출제 포인트 **3개 이상** 추출
- 각 출제 포인트에 W코드 후보 1~2개 매핑
- 논증 구조(전제-결론-숨은전제-반론) 해부 완료
- 영역 및 발문 유형 판별 완료
- 오답 함정 T1~T10 후보 카탈로그 작성

## Notes

- 이 에이전트는 **판단하지 않는다.** 추출·매핑만 한다. 문항 설계는 design의 몫.
- W코드 examples는 이 단계에서 주입 **안 함**. design 단계에서 analyze가 뽑은 W코드 후보에 해당하는 examples만 타깃 주입.
