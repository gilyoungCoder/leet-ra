# LEET 추리논증 출제 시스템 (LEET-RA)

LEET 추리논증(법학적성시험) 지문 생성, 분석, 문항 설계, 검수를 위한 멀티 에이전트 파이프라인.
v1.5 기반.

---

## 파이프라인 구조

```
[생성 모드: 소재 → 지문 → 문항 → 검수]
  영역/소재 → sourcer → (사용자 승인) → analyze → design → review

[분석 모드: 기존 지문 → 문항 → 검수]
  지문 → analyze → design → review

[세트 모드: 영역별 N문항 반복]
  (영역 지정 + 중복 방지) × N → 생성 모드 반복
```

## 에이전트 위임 규칙 (OMC)

아래 자연어 트리거가 감지되면, **반드시 Agent 도구를 사용하여 서브에이전트를 spawn**한다.
각 에이전트의 프롬프트 파일을 먼저 Read한 뒤, 그 전문을 Agent의 prompt에 포함하여 위임한다.

### 라우팅 테이블

| 트리거 | 에이전트 | 프롬프트 파일 | 모델 | Agent 도구 설정 |
|--------|---------|-------------|------|----------------|
| "소재 찾아줘", "지문 만들어줘", "sourcer" | **ra-sourcer** | `leet_ra/prompts/sourcer.md` | `opus` | `Agent(name="ra-sourcer", model="opus", mode="auto")` |
| "분석해줘", "지문 분석", "analyze" | **ra-analyze** | `leet_ra/prompts/analyze.md` | `opus` | `Agent(name="ra-analyze", model="opus", mode="auto")` |
| "문항 설계", "문항 만들어줘", "design" | **ra-design** | `leet_ra/prompts/design.md` | `opus` | `Agent(name="ra-design", model="opus", mode="auto")` |
| "검수", "리뷰", "review" | **ra-review** | `leet_ra/prompts/review.md` | `opus` | `Agent(name="ra-review", model="opus", mode="auto")` |
| "풀 파이프라인", "세트 만들어줘", "pipeline" | sourcer → analyze → design → review | 위 4개 순차 | `opus` | 순차 spawn. 각 단계 출력을 다음에 전달 |
| "법 N문항", "인문 N문항", "40문항" | **ra-sourcer** (세트 모드) | `leet_ra/prompts/sourcer.md` | `opus` | 영역별 반복 spawn. 중복 방지 리스트 포함 |
| "hwpx로", "한글로 출력", "문제지로 뽑아", "export" | **ra-exporter** (`default` 양식) | `leet_ra/exporter/export_hwpx.py` | `-` (쉘 실행) | review ✅ 이후 `--format default` |
| "전국 양식으로", "전국으로 뽑아" | **ra-exporter** (`jeonguk` 양식) | 위와 동일 | `-` | `--format jeonguk` 로 전국 템플릿 사용 |
| "서바 양식으로", "서바로 뽑아" | **ra-exporter** (`serva` 양식) | 위와 동일 | `-` | `--format serva` 로 서바 템플릿 사용 |

### 위임 프로토콜

에이전트를 spawn할 때 아래 절차를 따른다:

1. **프롬프트 파일 Read**: 해당 에이전트의 프롬프트 파일(`leet_ra/prompts/*.md`)을 Read 도구로 읽는다.
2. **Agent 도구 호출**: 읽은 프롬프트 전문 + 사용자가 제공한 지문/소재/이전 단계 출력을 합쳐서 Agent의 prompt로 전달한다.
3. **결과 수신 후 사용자에게 전달**: 에이전트 결과를 사용자에게 그대로 전달한다.
4. **순차 파이프라인**: pipeline/세트 모드에서는 이전 에이전트의 출력을 다음 에이전트의 prompt에 포함한다.

```
# 위임 예시 (analyze)
1. Read("leet_ra/prompts/analyze.md") → prompt_text
2. Agent(
     name="ra-analyze",
     description="LEET 추리논증 지문 분석",
     model="opus",
     mode="auto",
     prompt="{prompt_text}\n\n## 분석 대상 지문\n\n{사용자 지문}"
   )
3. 결과를 사용자에게 전달
```

### 핵심 원칙

- **OMC 전제 시스템.** 모든 에이전트는 Claude Code의 Agent 도구로 opus 서브에이전트를 spawn한다. OMC 미설치 시 자연어 트리거가 작동하지 않는다.
- **sourcer가 병목이다.** 좋은 소재 = 좋은 문항. 빌드 3대 원칙 절대 준수.
- **analyze가 엔진이다.** 출제 포인트 추출이 전체 품질을 결정한다. 반드시 opus.
- **review는 독립 에이전트로 분리.** design과 같은 세션에서 실행하지 않는다. 편향 없는 검수를 위해 별도 spawn.
- **모든 핵심 에이전트는 opus.** 추론 품질이 생명이다.
- **기출 가중치 90/10.** 최근 3~5개년 기출이 90% 비중, 이전은 참고용 10%.

### 단계별 RAG 주입 (필수)

각 에이전트는 spawn **직전**에 `leet_ra/data/`에서 타깃 few-shot을 필터해 prompt에 주입한다. 주입 없이 spawn 금지.

| 에이전트 | 주입 대상 | 필터 규칙 |
|---------|---------|----------|
| ra-sourcer | `2024/2025_merged.json`의 `passage_text` 2~3개 | 영역 → leet_type 매핑 (법→D*, 인문→A*, 사회→C*/E*, 과학→C*, 논쟁→E*). 2025 우선. |
| ra-analyze | 동일 유형 기출 2개 **전체 구조** + W코드 21종 메타 + `taxonomy.md` | 사전 유형 추정 → 매칭 leet_type의 questions |
| ra-design | analyze W코드 후보 **× examples 2개씩** + 선지 구성 규칙 16개 + AP/CP 패턴 | 타깃 W코드에만 주입 (21개 전체 뿌리지 않음) |
| ra-review | 동일 leet_type 고품질 기출 1~2개 + W코드 진단 카탈로그 + 16규칙 체크리스트 | 기대 수준 비교 + Rule별 검증 |

구체 절차는 각 스킬의 `.omc/skills/ra-*/SKILL.md`의 **Step 1b** 참조.

---

## 지문 빌드 3대 원칙 (전 에이전트 공통 — 절대 규칙)

> 프로젝트 총괄자가 직접 지정한 원칙. 예외 없음.

1. **일반화**: 고교 수준 배경지식만 가진 IQ 높은 사람도 **지문 자체는** 편하게 이해 가능해야 한다. 변별은 "지문 이해"가 아니라 "선지 판단"에서 발생.
2. **실명/이론명 금지**: 마르크스·칸트·하버마스 등 실제 학자명 **절대** 등장 금지. '갑', '을', '병'으로 일반화. 이론도 `<이론>` 또는 '~라는 주장이 있다'로 일반화. 국가명도 'X국', 'Y국'으로.
3. **한국어 전용**: 한국어가 아닌 언어(특히 영어, 학술 약어) 사용 금지.

## 영역별 절대 금지

| 영역 | 절대 금지 |
|------|---------|
| **법 (규범)** | 민법·형법·행정법 등 변호사시험 빈출 소재 **절대 금지.** 특별법 영역(환경/교육/소비자/전자상거래 등) 사용. |
| **인문** | 기호 논리학(∀, ∃, →) 과도 사용 금지. '대우' 정도만 허용. 전공 개념 사용 시 지문 내 충분한 설명 필수. |
| **사회/과학** | 특별한 금지 없음. 소재 다양화에 초점. |

---

## 슬래시 커맨드

| 커맨드 | 설명 |
|--------|------|
| `/project:source` | 영역/소재 → 지문 초안 (Sourcer) |
| `/project:analyze` | 지문 → 구조 분석 + 출제 포인트 (Agent A) |
| `/project:design` | 분석 결과 → 발문 + 선지 + 해설 (Agent B) |
| `/project:review` | 원본 지문 + analyze + design 교차 검수 (Agent C) |
| `/project:pipeline` | 풀 파이프라인: 소재/지문 → sourcer → analyze → design → review |

## 운용 규칙

1. **sourcer 결과 확인 후 진행:** 빌드 3대 원칙 + 영역별 금지 소재 회피 체크.
2. **analyze 결과 확인 후 진행:** 출제 포인트 3개+ 확인.
3. **design 후 review 필수:** review에서 ❌가 0개일 때만 확정. ❌ 있으면 해당 단계로 루프.
4. **매력도 하 선지 금지 (Rule 4):** design에서 매력도 하 선지가 출력되면 즉시 상향 또는 재설계.
5. **패러프레이징 필수 (Rule 16):** 지문 2~3어절 이상 동일 인용 금지.

---

## 파일 구조

```
leet-ra/
├── CLAUDE.md                    # 이 파일 — 프로젝트 인스트럭션 (자동 로드)
├── README.md                    # 셋업/사용법 가이드
├── .claude/commands/            # 슬래시 커맨드 정의
├── .omc/skills/                 # OMC 스킬 (자연어 트리거)
├── leet_ra/
│   ├── prompts/                 # 에이전트 프롬프트 (수정은 여기서)
│   │   ├── sourcer.md           # Sourcer v1.6 — 소재 발굴 + 지문 초안
│   │   ├── analyze.md           # Agent A v1.5 — 지문 분석 (핵심 엔진)
│   │   ├── design.md            # Agent B v1.5 — 선지 설계
│   │   └── review.md            # Agent C v1.5 — 독립 검수
│   ├── taxonomy/
│   │   └── taxonomy.md          # 유형 분류 체계 v0.3
│   └── data/                    # 기출 파싱 데이터 (참조용)
│       ├── 2024_merged.json     # 2024 40문항 태깅
│       ├── 2025_merged.json     # 2025 40문항 태깅
│       ├── w_codes_merged.json  # W코드 21개 + 93 few-shot
│       └── choice_logic_analysis.json  # CP 7종 + AP 11종 + 규칙 16개
└── samples/                     # 통합 테스트 샘플 출력
    ├── v1_5questions.json       # v1 테스트
    └── v2_5questions.json       # v2 피드백 반영
```
