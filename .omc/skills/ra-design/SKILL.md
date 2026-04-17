---
name: ra-design
description: "LEET 추리논증 선지 설계기 (Agent B v1.5) — analyze W코드 기반 타깃 few-shot RAG + 선지 구성 규칙 16개 주입"
triggers:
  - "문항 설계"
  - "문항 만들어"
  - "선지 설계"
  - "design"
  - "Agent B"
  - "발문"
argument-hint: "(analyze 결과 참조)"
requires: ["omc"]
---

# RA-DESIGN: 선지 설계기 (Agent B)

**OMC 전제.** Agent 도구로 opus 서브에이전트를 spawn한다.

Agent A(analyze)가 추출한 W코드 후보·출제 포인트·논증 구조를 바탕으로, 각 W코드에 매칭된 **기출 오답 few-shot**을 주입하고 실전 LEET 수준의 발문 + 선지 + 해설을 설계한다.

## When to Activate

- analyze 실행 후, 문항 설계를 요청할 때
- "문항 만들어줘", "선지 설계해줘" 등
- 풀 파이프라인의 3단계

## Workflow

### Step 1: 프롬프트 로드

- Read `leet_ra/prompts/design.md` 전문

### Step 1b: W코드 타깃 few-shot + 선지 구성 규칙 RAG 주입 (필수)

**핵심 전략**: analyze가 뽑은 W코드 후보에 **해당하는 실제 오답 예시만** 타깃 주입. 21개 전체 뿌리면 토큰 낭비, 관련 없는 패턴이 오염을 일으킨다.

**주입 절차**:

1. **analyze 출력에서 W코드 후보 리스트 추출** (보통 3~6개)
2. Read `leet_ra/data/w_codes_merged.json` → `w_codes` 배열
3. 각 W코드 후보에 대해 `examples` 배열에서 **2개씩** 선별:
   - 우선순위: `year=="2025"` → `year=="2024"` (90/10 가중치)
   - 각 example에서 주입 필드: `passage_excerpt`, `choice_text`, `w_code`, `error_pattern`, `official_explanation`
   - 결과: 약 W코드 4~5개 × 2 = **8~10 few-shot 오답 예시**
4. Read `leet_ra/data/choice_logic_analysis.json`:
   - `choice_construction_rules` 16개 **전체** 주입 (전 규칙 준수 필수)
   - `attractiveness_patterns` 11개 주입. 각 패턴의 `w_codes_related`가 analyze W코드 후보와 겹치면 그 패턴의 `examples` 1~2개 추가 주입
   - `correct_choice_patterns` 7개 메타(`pattern_id`, `name_ko`, `description`, `frequency`)
5. **발문 형식 참조**: analyze 출력의 `leet_type`이 분명하면 `leet_ra/data/2025_merged.json`에서 동일 `leet_type` 문항 1개의 `stem`, `choices`, `choices_box`, `view_format` 구조를 참조로 주입

### Step 2: 에이전트 Spawn

```
Agent(
  name="ra-design",
  description="LEET 추리논증 선지 설계",
  model="opus",
  mode="auto",
  prompt="{design.md 전문}\n\n"
        "## 원본 지문\n\n{지문}\n\n"
        "## Agent A 분석 데이터\n\n{analyze 출력}\n\n"
        "## 매칭 W코드 few-shot (analyze 후보 × 2 예시)\n\n{w_codes_merged.json에서 타깃 추출 8~10개}\n\n"
        "## 선지 구성 규칙 16개 (전량 준수)\n\n{choice_construction_rules}\n\n"
        "## 매력도 패턴 AP1~AP11 (매칭 우선)\n\n{attractiveness_patterns + 타깃 examples}\n\n"
        "## 정답 선지 패턴 CP1~CP7\n\n{correct_choice_patterns 메타}\n\n"
        "## 동일 leet_type 기출 발문/선지 구조 참조\n\n{2025 매칭 문항 1개}"
)
```

### Step 3: 결과 전달

발문 + 선지 + 해설을 사용자에게 전달한다. 이후 **ra-review를 반드시 독립 세션에서** spawn.

## 선지 구성 핵심 규칙

- **Rule 4 (절대)**: 매력도 하 선지 출력 금지. 지문을 한 번 읽으면 즉시 배제 가능한 오답은 폐기.
- **Rule 16**: 지문 표현 2~3어절 이상 동일 인용 금지. 반드시 패러프레이징. (규범 영역 예외 가능)
- **W코드 다변화**: 한 문항 내에서 같은 W코드 반복 금지. 서로 다른 W코드 2~3종 배치.
- **정답 유일성 자가 검증**: 설계 후 모든 선지를 역으로 풀어 정답이 유일한지 확인.
- **지문 근거 제한**: 정답/오답 판정 근거는 반드시 지문 내. 배경지식으로만 풀리는 선지 금지.
- **발문 고정**: 기출의 전형적 발문을 그대로 사용. 변형 금지.

## 기출 발문 패턴

| 영역 | 전형 발문 |
|------|----------|
| 법 적용 (D1) | "~에 따라 바르게 추론한 것은?" |
| 논리 퍼즐 (B3) | "옳지 않은 것은?" |
| 견해 비교 (D3/E2) | "견해에 대한 평가로 옳은 것은?" |
| 논쟁 평가 (E1) | "진술로 옳지 않은 것은?" |

## 품질 체크

- 출제 포인트 **전량 소모** (미소모 = 설계 결함)
- 매력도 하 선지 **0개** (Rule 4 절대)
- 오답 W코드 **2~3종 이상** 다변화
- 역풀이 정답 유일성 통과
- 모든 선지 근거가 지문 내

## Notes

- W코드 21종 **전체를 뿌리지 않는다.** analyze가 뽑은 후보에만 타깃 주입. 그래야 선지가 해당 W코드 패턴으로 정밀 생성된다.
- 보기 조합형(ㄱㄴㄷ) 문항은 각 진술의 옳고 그름이 지문에서 일의적으로 확정되어야 한다.
