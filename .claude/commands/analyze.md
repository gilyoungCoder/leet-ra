LEET 추리논증 지문 분석 (Agent A v1.5)

**OMC 전제.** 이 커맨드는 `ra-analyze` OMC 스킬을 통해 opus 서브에이전트를 spawn한다.

## 실행 지시

`.omc/skills/ra-analyze/SKILL.md` Workflow를 그대로 따른다:

1. Read `leet_ra/prompts/analyze.md` + `leet_ra/taxonomy/taxonomy.md`
2. **사전 유형 추정**: 지문 특징으로 leet_type 후보 1~2개 추정
3. **RAG 주입**:
   - `leet_ra/data/2025_merged.json` + `2024_merged.json` → 추정 leet_type 매칭 questions 2개 **전체 구조** (passage_text, stem, choices, choices_box, views, components 등)
   - `leet_ra/data/w_codes_merged.json` → W코드 21종 메타 카탈로그 (code/name_ko/description/frequency_total)
4. `Agent(name="ra-analyze", model="opus", mode="auto", prompt=...)` spawn
5. 결과를 사용자에게 전달

## 지시 원칙

- W코드 examples는 **이 단계에서 주입하지 않는다.** design 단계에서 타깃 주입.
- 구조화된 출력만. 서술형 설명 최소화.
- 출제 포인트 3개+, 구성요소 전량 태깅, W코드 후보 1~2개씩 매핑 필수.

## 분석 대상 지문

$ARGUMENTS
