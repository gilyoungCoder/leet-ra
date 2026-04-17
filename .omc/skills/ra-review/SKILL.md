---
name: ra-review
description: "LEET 추리논증 문항 검수기 (Agent C v1.5) — 기대 수준 기출 RAG + W코드 진단 카탈로그 + 16규칙 체크리스트로 독립 검수"
triggers:
  - "검수"
  - "리뷰"
  - "review"
  - "Agent C"
  - "검증"
  - "체크"
argument-hint: "(design 결과 참조)"
requires: ["omc"]
---

# RA-REVIEW: 문항 검수기 (Agent C)

**OMC 전제.** 반드시 독립 에이전트로 Agent 도구 spawn. design과 같은 세션에서 절대 실행 금지 — 편향 차단이 핵심.

원본 지문·analyze·design을 교차 검수하여 결함을 찾고 수정 권고를 산출한다.

## When to Activate

- design 실행 후, 검수를 요청할 때
- "검수해줘", "리뷰해줘" 등
- 풀 파이프라인의 4단계 (최종 게이트)

## Workflow

### Step 1: 프롬프트 로드

- Read `leet_ra/prompts/review.md` 전문

### Step 1b: 기대 수준 기출 + W코드 진단 + 규칙 체크리스트 RAG 주입 (필수)

**목적**: 검수자는 "이 문항이 실전 LEET 수준인가"를 판단해야 한다. 기출 고품질 문항을 기대 수준으로 함께 제시하지 않으면 절대적 기준이 모호해진다.

**주입 절차**:

1. design 출력 또는 이전 대화의 analyze 출력에서 `leet_type` 식별
2. Read `leet_ra/data/2025_merged.json` → 동일 `leet_type`의 문항 1~2개를 **기대 수준 기출 참조**로 주입 (전체 구조: `passage_text`, `stem`, `choices`, `choices_box`, `answer`)
   - 부족 시 `leet_ra/data/2024_merged.json`에서 보충
3. Read `leet_ra/data/w_codes_merged.json` → W코드 21개의 `code`, `name_ko`, `description`을 **진단 카탈로그**로 주입 (어느 W코드로도 안 잡히는 오답 = 매력도 의심)
4. Read `leet_ra/data/choice_logic_analysis.json`:
   - `choice_construction_rules` 16개를 **Rule별 검증 체크리스트**로 주입 (각 Rule 위반 여부를 항목별로 판정)

### Step 2: 에이전트 Spawn (독립 세션!)

```
Agent(
  name="ra-review",
  description="LEET 추리논증 문항 검수",
  model="opus",
  mode="auto",
  prompt="{review.md 전문}\n\n"
        "## W코드 21종 진단 카탈로그\n\n{w_codes 메타}\n\n"
        "## 선지 구성 규칙 16개 체크리스트 (Rule별 판정)\n\n{choice_construction_rules}\n\n"
        "## 기대 수준 기출 참조 (동일 leet_type 1~2문항)\n\n{2025 매칭 전체 구조}\n\n"
        "## 원본 지문\n\n{지문}\n\n"
        "## Agent A 분석 데이터\n\n{analyze}\n\n"
        "## Agent B 문항\n\n{design}"
)
```

### Step 3: 판정 + 루프

- **❌ 0개** → 최종 확정
- **❌ 있음** → 루프:
  - 정답 유일성/복수 정답 문제 → ra-design 재실행
  - 지문 근거 부족 → ra-analyze 재실행 또는 지문 보강
  - 출제 포인트 자체 부족 → ra-sourcer로 돌아가 지문 재생성
  - 수정 후 ra-review 재실행

## 검증 8항목

1. **정답 유일성** — 지문만으로 정답이 유일하게 도출되는가
2. **복수 정답 위험** — 보기 조합형에서 ㄱ/ㄴ/ㄷ 각각 일의적으로 확정되는가
3. **오답 매력도** — 자명한 오답 선지(Rule 4 위반) 있는가 (어느 W코드로도 안 잡히면 매력도 의심)
4. **지문 근거** — 모든 선지가 지문 내 정보만으로 판단 가능한가
5. **W코드 다변화** — 동일 W코드 2회 이상 반복되는가
6. **패러프레이징** — 2~3어절 이상 동일 인용 있는가 (Rule 16)
7. **발문-선지 정합성** — 발문과 선지 응답이 일치하는가
8. **해설 논리** — 해설만으로 정답/오답 판정이 가능한가

## 0단계: 직접 풀이 (핵심)

검수자는 해설을 보기 전에 지문과 발문만으로 직접 푼다. 도출 정답이 제시 정답과 갈리면 그 자체가 결함 신호.

## Notes

- **독립성이 핵심.** design 세션과 격리. 같은 Agent 호출에서 함께 실행 금지.
- 판정은 ✅ / ❌ / ⚠️ 셋 중 하나로만. 모호한 판정 금지.
- 기대 수준 기출 주입은 "실전 LEET 수준 미달"을 판정할 절대 기준을 제공한다.
