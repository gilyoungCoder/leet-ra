LEET 추리논증 풀 파이프라인

소재 또는 지문을 입력받아 sourcer → analyze → design → review를 순차 실행하여 완성된 문항을 산출한다.

## 모드 판별
- 입력이 500자+ 지문 → 분석 모드 (analyze부터 시작)
- 입력이 짧은 키워드/영역 → 생성 모드 (sourcer부터 시작)

## 실행 순서

### Step 1: sourcer (생성 모드만)
`leet_ra/prompts/sourcer.md`를 읽고 지문 초안을 생성한다.
- 확인: 빌드 3대 원칙 준수(일반화, 실명 금지, 한국어 전용), 영역별 금지 소재 회피

### Step 2: analyze (Agent A)
`leet_ra/prompts/analyze.md`를 읽고 구성요소 · 출제 포인트 · W코드 후보 · 논증 구조를 해부한다.
- 확인: 출제 포인트 3개+, 영역 확정, W코드/T코드 매핑

### Step 3: design (Agent B)
`leet_ra/prompts/design.md`를 읽고 발문 + 선지 + 해설을 설계한다.
- 확인: 출제 포인트 전량 소모, 매력도 하 0개, W코드 다변화, 역풀이 정답 유일성

### Step 4: review (Agent C) — 독립 세션
`leet_ra/prompts/review.md`를 읽고 8항목을 교차 검수한다.
- ❌ 0개 → 최종 확정
- ❌ 있음 → 해당 단계로 루프

## 주의 사항
- 각 Step의 프롬프트 파일을 반드시 읽고 그 출력 형식을 완전히 따를 것.
- Step 간 데이터 전달: 이전 Step의 출력을 그대로 참조.
- review는 반드시 독립 에이전트로 spawn (design과 동일 세션 금지).
- 서술형 설명 최소화, 구조화된 형식으로만 출력.

## 입력

$ARGUMENTS
