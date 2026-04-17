LEET 추리논증 문항 검수 (Agent C v1.5)

**OMC 전제.** 이 커맨드는 `ra-review` OMC 스킬을 통해 **독립 세션**에서 opus 서브에이전트를 spawn한다.
design과 같은 세션에서 실행 금지 — 편향 차단이 핵심.

## 실행 지시

`.omc/skills/ra-review/SKILL.md` Workflow를 그대로 따른다:

1. Read `leet_ra/prompts/review.md`
2. design/analyze 출력에서 `leet_type` 식별
3. **RAG 주입**:
   - `leet_ra/data/2025_merged.json` → 동일 leet_type 고품질 기출 1~2개 전체 구조 (기대 수준 비교)
   - `leet_ra/data/w_codes_merged.json` → W코드 21개 메타 (진단 카탈로그)
   - `leet_ra/data/choice_logic_analysis.json` → `choice_construction_rules` 16개 (Rule별 체크리스트)
4. `Agent(name="ra-review", model="opus", mode="auto", prompt=...)` spawn — **별도 세션**
5. 0단계(직접 풀이) → 검증 8항목 → 판정

## 검증 8항목
1. 정답 유일성
2. 복수 정답 위험
3. 오답 매력도 (어느 W코드로도 안 잡히는 오답 = 매력도 의심)
4. 지문 근거
5. W코드 다변화
6. 패러프레이징 (Rule 16)
7. 발문-선지 정합성
8. 해설 논리

## 판정
- ❌ 0개 → 최종 확정
- ❌ 있음 → 해당 단계로 루프 (sourcer / analyze / design)

## 검수 대상

$ARGUMENTS
