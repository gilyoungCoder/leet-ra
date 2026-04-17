LEET 추리논증 선지 설계 (Agent B v1.5)

**OMC 전제.** 이 커맨드는 `ra-design` OMC 스킬을 통해 opus 서브에이전트를 spawn한다.

## 실행 지시

`.omc/skills/ra-design/SKILL.md` Workflow를 그대로 따른다:

1. Read `leet_ra/prompts/design.md`
2. **analyze 출력에서 W코드 후보 추출** (3~6개)
3. **타깃 RAG 주입**:
   - `leet_ra/data/w_codes_merged.json` → 각 W코드 후보의 `examples` 2개씩 (2025 우선) — 약 8~10 few-shot
     - 필드: passage_excerpt, choice_text, w_code, error_pattern, official_explanation
   - `leet_ra/data/choice_logic_analysis.json`:
     - `choice_construction_rules` 16개 **전체**
     - `attractiveness_patterns` 11개 (w_codes_related 겹치는 패턴의 examples 우선)
     - `correct_choice_patterns` 7개 메타
   - `leet_ra/data/2025_merged.json` → 동일 leet_type 문항 1개의 발문/선지 구조 참조
4. `Agent(name="ra-design", model="opus", mode="auto", prompt=...)` spawn
5. 결과를 사용자에게 전달. 이후 ra-review를 **반드시 독립 세션**에서 spawn.

## 지시 원칙

- **W코드 21종 전체를 뿌리지 않는다.** analyze 후보에만 타깃 주입.
- Rule 4 (매력도 하 금지), Rule 16 (패러프레이징) 절대.
- W코드 다변화 (한 문항 내 2~3종 이상).
- 역풀이 정답 유일성 자가 검증.

## 분석 결과

$ARGUMENTS
