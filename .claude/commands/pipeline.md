LEET 추리논증 풀 파이프라인

**OMC 전제.** `ra` 마스터 스킬을 통해 단계별 opus 서브에이전트를 체인으로 spawn한다.

## 모드 판별
- 입력이 500자+ 지문 → 분석 모드 (ra-analyze부터 시작)
- 입력이 짧은 키워드/영역 → 생성 모드 (ra-sourcer부터 시작)

## 단계별 RAG 주입 체인

### Step 1: ra-sourcer (생성 모드만) — 영역 기반 passage RAG
- 영역 → leet_type 매핑 → 동일 유형 passage_text 2~3개 주입
- `Agent(name="ra-sourcer", model="opus", mode="auto")` spawn

### Step 2: ra-analyze — 유형 매칭 기출 + W코드 카탈로그 RAG
- 사전 유형 추정 → 매칭 leet_type 기출 2개 전체 구조 + W코드 21종 메타
- `Agent(name="ra-analyze", model="opus", mode="auto")` spawn

### Step 3: ra-design — W코드 타깃 few-shot + 16규칙 RAG
- analyze W코드 후보 × examples 2개씩 + 선지 구성 규칙 16개 + AP/CP 패턴
- `Agent(name="ra-design", model="opus", mode="auto")` spawn

### Step 4: ra-review — 기대 수준 기출 + 진단 카탈로그 RAG (독립 세션!)
- 동일 leet_type 고품질 기출 1~2개 + W코드 진단 + 16규칙 체크리스트
- `Agent(name="ra-review", model="opus", mode="auto")` spawn — **별도 세션**

## 주의 사항
- 각 Step의 SKILL.md를 반드시 참조하여 RAG 주입 규칙을 준수할 것.
- Step 간 데이터 전달: 이전 Step의 출력을 그대로 다음 spawn의 prompt에 포함.
- review는 반드시 독립 에이전트로 spawn.
- RAG 주입 없이 에이전트를 spawn하지 않는다.

## 입력

$ARGUMENTS
