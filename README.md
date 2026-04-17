# LEET-RA: LEET 추리논증 출제 시스템

LEET 추리논증(법학적성시험 추리논증 영역) 소재 발굴, 지문 생성, 문항 설계, 검수를 위한 AI 멀티에이전트 파이프라인.
Claude Code + OMC(oh-my-claudecode) 오케스트레이션.

---

## 한눈에 보기

```
Setup:      npm 설치 → OMC 설치 → git clone → claude 실행 → "법 1문항 만들어줘" 입력
               OMC가 알아서 opus 에이전트를 spawn하여 소재 발굴 → 지문 → 분석 → 문항 → 검수
```

---

## 1단계: Claude Code 설치

Node.js 18+ 필요. 없으면 먼저 설치.

```bash
# Node.js 확인
node --version   # v18 이상이어야 함

# Node.js 없으면 설치 (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS
brew install node

# Claude Code 설치
npm install -g @anthropic-ai/claude-code
```

설치 확인:
```bash
claude --version
```

처음 실행 시 Anthropic API 키 입력이 필요합니다:
```bash
claude
# 프롬프트가 뜨면 API 키 입력
# https://console.anthropic.com/settings/keys 에서 발급
```

---

## 2단계: OMC (oh-my-claudecode) 설치

OMC는 Claude Code 위에 올라가는 멀티에이전트 오케스트레이션 레이어입니다.
이 프로젝트의 `ra-*` 에이전트들은 OMC가 있어야 자연어 트리거로 작동합니다.

### 방법 A: Claude Code 플러그인으로 설치 (권장)

```bash
claude
```

Claude Code 프롬프트 안에서:
```
/plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode
/plugin install oh-my-claudecode
```

설치 후 셋업:
```
/setup
```
또는
```
/omc-setup
```

### 방법 B: npm으로 설치

```bash
npm i -g oh-my-claude-sisyphus@latest
```

설치 후 터미널에서:
```bash
omc setup
```

### 전제 조건

- **Claude Code CLI** 설치 완료
- **Claude Max/Pro 구독** 또는 **Anthropic API 키** (opus 사용 가능 플랜)
- (선택) **tmux** — 팀 오케스트레이션 등 일부 기능에 필요
  - macOS: `brew install tmux`
  - Ubuntu/Debian: `sudo apt install tmux`

### OMC 설치 확인

```bash
claude
```

Claude Code 실행 후 아래가 보이면 성공:
- 시작 시 `[OMC]` 관련 메시지
- `/oh-my-claudecode:` 로 시작하는 스킬 사용 가능

문제가 있으면:
```
# Claude Code 안에서
/oh-my-claudecode:omc-doctor
```

---

## 3단계: 이 레포 클론 + 원샷 셋업

```bash
git clone https://github.com/gilyoungCoder/leet-ra.git
cd leet-ra
bash setup.sh    # pip install + 샘플 hwpx 생성 테스트까지 자동
```

`setup.sh`가 하는 일:
1. `pip install -r requirements.txt` (python-hwpx, hwpx-mcp-server, python-docx)
2. 의존성 검증 (import + 실행 파일 경로)
3. `samples/v2_5questions.json` → `output/setup_test.hwpx` 샘플 생성

성공하면 `claude` 실행 시 `.mcp.json`의 hwpx MCP 서버가 자동 등록되어 **한글 출력이 전부 작동**합니다.

### 레포 구조

```
leet-ra/
├── CLAUDE.md                    # 프로젝트 인스트럭션 (자동 로드)
├── README.md                    # 이 파일
├── .claude/
│   ├── commands/                # 슬래시 커맨드 5개
│   │   ├── source.md            # /project:source
│   │   ├── analyze.md           # /project:analyze
│   │   ├── design.md            # /project:design
│   │   ├── review.md            # /project:review
│   │   └── pipeline.md          # /project:pipeline
│   └── settings.local.json
├── .omc/
│   └── skills/                  # OMC 에이전트 5개 (자동 감지)
│       ├── ra/                  # 마스터 오케스트레이터
│       ├── ra-sourcer/          # 소재 발굴 + 지문 초안 생성
│       ├── ra-analyze/          # Agent A — 지문 분석 (핵심 엔진)
│       ├── ra-design/           # Agent B — 선지 설계
│       └── ra-review/           # Agent C — 독립 검수
├── leet_ra/
│   ├── prompts/                 # 에이전트 프롬프트 (수정은 여기서)
│   │   ├── sourcer.md           # Sourcer v1.6
│   │   ├── analyze.md           # Agent A v1.5
│   │   ├── design.md            # Agent B v1.5
│   │   └── review.md            # Agent C v1.5
│   ├── taxonomy/
│   │   └── taxonomy.md          # 유형 분류 체계 v0.3
│   ├── data/                    # 기출 파싱 데이터 (참조용)
│   │   ├── 2024_merged.json     # 2024 40문항 태깅
│   │   ├── 2025_merged.json     # 2025 40문항 태깅
│   │   ├── w_codes_merged.json  # W코드 21개 + 93 few-shot
│   │   └── choice_logic_analysis.json  # CP 7종 + AP 11종 + 규칙 16개
│   ├── README_개발가이드.md
│   ├── 참고_LEET-RA_초기보고서.md
│   └── 참고_SNG-KO_보고서.md
└── samples/                     # 통합 테스트 샘플 출력
    ├── v1_5questions.json
    ├── v2_5questions.json
    └── LEET_RA_통합테스트_v2.docx
```

---

## 4단계: 실행

```bash
cd leet-ra
claude
```

실행하면:
1. `CLAUDE.md`가 자동 로드 → 에이전트 위임 규칙 활성화
2. `.omc/skills/ra-*`이 OMC에 의해 자동 감지 → 트리거 등록
3. `.claude/commands/*`가 슬래시 커맨드로 등록

---

## 사용법

### 자연어 명령 (OMC 트리거)

OMC가 자연어를 인식하고 자동으로 해당 에이전트를 opus로 spawn합니다:

```
"특별법 영역으로 법 1문항 만들어줘"       → ra-sourcer → ra-analyze → ra-design → ra-review
"이 지문 분석해줘"                       → ra-analyze 트리거 (Agent A)
[지문 텍스트 붙여넣기]

"문항 설계해줘"                          → ra-design 트리거 (Agent B)

"검수해줘"                               → ra-review 트리거 (Agent C, 독립)

"인문 5문항 세트 만들어줘"                → 세트 모드 (sourcer 반복)

"풀 파이프라인 돌려줘"                    → ra 마스터 트리거 (전체 순차 실행)
```

### 단계별 RAG 주입 (자동)

각 에이전트는 spawn 직전에 `leet_ra/data/`의 기출 JSON에서 타깃 few-shot을 필터해 prompt에 주입합니다:

| 에이전트 | 자동 주입되는 RAG |
|---------|-----------------|
| ra-sourcer | 영역 → leet_type 매핑으로 동일 유형 `passage_text` 2~3개 (2025 우선) |
| ra-analyze | 사전 유형 추정 → 동일 leet_type 기출 2개 전체 구조 + W코드 21종 메타 카탈로그 + taxonomy |
| ra-design | analyze가 뽑은 W코드 후보 × examples 2개씩 (총 8~10개) + 선지 구성 규칙 16개 + AP/CP 패턴 |
| ra-review | 동일 leet_type 고품질 기출 1~2개(기대 수준) + W코드 진단 카탈로그 + 16규칙 체크리스트 |

**타깃 주입 원칙**: W코드 21종을 전체 뿌리지 않고, analyze가 추출한 후보에만 매칭되는 examples만 주입 → 선지가 해당 W코드 패턴으로 정밀 생성됨.

### 슬래시 커맨드 (OMC 전제)

커맨드도 내부적으로 Agent 도구로 opus 서브에이전트를 spawn합니다. OMC 미설치 시 라우팅이 동작하지 않습니다:

```
/project:source [영역/소재]       → 소재 발굴 + 지문 초안
/project:analyze [지문]           → 구조 분석 + 출제 포인트 추출
/project:design                   → 발문 + 선지 + 해설 설계
/project:review                   → 교차 검수
/project:pipeline [소재/지문]     → 풀 파이프라인
/project:export [JSON/제목]       → hwpx + docx 출력
```

---

## 워크플로우

### A. 소재/영역부터 시작 (생성 모드)

```
Step 1: "특별법 영역으로 법 1문항 만들어줘"
        → ra-sourcer (Sourcer v1.6, opus) 실행
        → 빌드 3대 원칙(일반화/실명 금지/한국어 전용) 준수 확인
        → 지문 초안 승인

Step 2: "분석해줘"
        → ra-analyze (Agent A v1.5, opus) 실행
        → 출제 포인트 3개+ 추출, W코드 후보 매핑

Step 3: "문항 설계해줘"
        → ra-design (Agent B v1.5, opus) 실행
        → 발문 + 5지선다(또는 ㄱㄴㄷ) + 해설
        → 매력도 하 = 0개, W코드 다변화 확인

Step 4: "검수해줘"
        → ra-review (Agent C v1.5, opus) 실행 — 독립 에이전트
        → 8항목 검증
        → ❌ 0개면 확정
        → ❌ 있으면 해당 단계로 루프
```

### B. 기존 지문에서 문항 생성 (분석 모드)

지문을 이미 갖고 있을 때는 ra-sourcer를 건너뛰고 ra-analyze부터:

```
Step 1: "이 지문 분석해줘" + 지문 붙여넣기
        → ra-analyze

Step 2~4: design → review (위와 동일)
```

### C. 세트 모드 (40문항 1세트)

```
"법 8문항, 인문 12문항, 사회 10문항, 과학 6문항, 논쟁 4문항 세트 만들어줘"
→ 영역별 sourcer 반복 spawn (소재 중복 방지)
→ 각 라운드마다 sourcer → analyze → design → review
```

---

## 에이전트 상세

### ra-sourcer (Sourcer v1.6) — 병목 단계

소재 발굴과 지문 초안 생성을 통합한 에이전트. **여기 품질이 전체 결과를 좌우합니다.**

- 영역: 법(규범) / 인문 / 사회 / 과학 / 논쟁
- 지문 빌드 3대 원칙 절대 준수
- 세칙: 규정(R) 시간 표현 명확화, '아니한다' → '않는다', '만 원' 띄어쓰기
- 소재는 '환각' 허용 (큰 수준의 일반화 전제)

### ra-analyze (Agent A v1.5) — 핵심 엔진

지문을 구성요소·출제 포인트·W코드 후보·논증 구조로 해부. **design의 유일한 입력.**

**LEET 유형 체계 (5대 영역)**:

| 대유형 | 소분류 | 핵심 |
|--------|--------|------|
| A. 논증 분석·평가 | A1 전제·결론 / A2 강화·약화 / A3 오류 식별 | 숨은 전제, 논증 평가 |
| B. 연역 추리 | B1 명제 논리 / B2 양화 논리 / B3 논리 퍼즐 | 조건문, 규칙 복원, 배치 |
| C. 귀납·유비 추리 | C1 귀납 / C2 유비 / C3 인과 | 밀의 방법, 구조적 유사성 |
| D. 법적 추론 | D1 법 적용 / D2 판례 / D3 다견해 | 조문→사례, 해석 대립 |
| E. 논쟁 평가 | E1 다입장 강화·약화 / E2 입장 비교 | 3자 대립, 일치/차이 |

### ra-design (Agent B v1.5) — 선지 설계

analyze 데이터로 발문 + 선지 + 해설을 설계.

- **Rule 4 (절대)**: 매력도 하 선지 금지
- **Rule 16**: 2~3어절 이상 동일 인용 금지 (패러프레이징 필수)
- W코드 다변화 (같은 W코드 반복 금지)
- 역풀이 정답 유일성 자가 검증
- 기출 전형 발문 그대로 사용 (변형 금지)

### ra-exporter — 한글 파일 출력기 (python-hwpx + MCP 서버)

review ✅ 통과한 문항 JSON을 **hwpx(한컴오피스)** 와 **docx(워드)** 로 출력합니다. 두 경로 지원:

#### 경로 1: 배치 출력 (기본, 시대인재 템플릿 기반)
- `leet_ra/exporter/export_hwpx.py` — **시대인재 양식 hwpx 템플릿**(`leet_ra/templates/문제지_템플릿.hwpx`, `해설지_템플릿.hwpx`)을 복제 → 본문 XML 비우기 → 시대인재 등록 스타일명(`문제`, `선택지`, `보기박스`, `보기내용(내어쓰기)`, `지문 (테두리)`, `문항번호`, `정답_10pt`, `해시태그`, `정오판단_설명` 등)으로 문단 삽입
- 교열 매뉴얼 자동 반영: **묶음 빈 칸(U+2060)** 문항번호↔발문, 선지기호↔내용, ㄱㄴㄷ↔내용
- `leet_ra/exporter/export_docx.py` — python-docx 2단 레이아웃 대체 출력
- 출력 디렉터리: `output/` (gitignore 대상)

#### 경로 2: HWPX MCP 서버 (인터랙티브 편집)
- 레포 루트의 `.mcp.json`에 등록된 `hwpx` MCP 서버가 **33개 도구**를 노출
- `create_document`, `add_table`, `search_and_replace`, `fill_by_path`, `find_cell_by_label` 등
- Claude가 자연어로 문서 조작 가능: "3번 문항 해설 바꿔줘", "표 셀 내용 수정해줘"

#### 설치

```bash
pip install python-hwpx hwpx-mcp-server
```

`.mcp.json`이 레포 루트에 있으므로 `claude` 실행 시 자동 등록됩니다. 도구 prefix: `mcp__hwpx__*`.

#### 사용

**자연어 트리거**: "hwpx로 뽑아줘", "한글로 출력", "문제지 만들어줘"
**슬래시 커맨드**: `/project:export`

```bash
# 수동 실행 예시
python3 leet_ra/exporter/export_hwpx.py \
  -i samples/v2_5questions.json \
  -o output/v2_문제지.hwpx \
  -t "LEET-RA 연습 1회"
```

#### 검증 (이 레포에서 실제 테스트됨)

- `samples/v2_5questions.json` (5문항) → `output/leet_v2_real.hwpx` (15.5KB)
- `HwpxDocument.open().export_text()` readback 9,675자 정상 추출
- 한컴오피스에서 바로 열림 (python-hwpx는 Open XML 표준 준수)

#### 현재 반영/미반영 범위 (솔직 체크)

| 항목 | 상태 | 비고 |
|------|------|------|
| 문항 논리 구조 (지문/보기/선지/해설) | ✅ 반영 | python-hwpx로 한컴 호환 hwpx 생성 |
| 기출 few-shot RAG (2024/2025, W코드 21종) | ✅ 반영 | 각 에이전트 spawn 시 자동 주입 |
| **시대인재 양식 스타일 (폰트/여백/2단 컬럼/표 테두리)** | ❌ **미반영** | `데이터/시대인재/*.hwp` 전부 바이너리 → Linux에서 읽기 불가. 한컴에서 .hwpx 변환 1회 필요 |
| **교열 매뉴얼 (`[교열] 시대인재 LEET팀 업무 매뉴얼_추리논증.ver.hwp`)** | ❌ **미반영 (의도적)** | 승규님 카톡 지침: "내부에 교열 담당자 따로 있어서 굳이 신경 쓸 필요 없어보입니다" |

#### 시대인재 양식 완벽 재현 경로 (요청 시)

시대인재 .hwp 중 하나(예: `26추리_서바 13_문제.hwp`)를 한컴에서 **"다른 이름으로 저장 → HWPX"** 한 번만 해서 `leet_ra/templates/시대인재_문제지.hwpx` 로 커밋하시면:
- MCP 도구 `search_and_replace` / `fill_by_path` / `set_table_cell_text` 로 슬롯 치환
- 스타일(폰트/여백/2단/표 테두리) 완전 유지
- 10분 분량의 추가 스크립트 작업으로 적용 가능

---

### ra-review (Agent C v1.5) — 독립 검수

**반드시 독립 에이전트로 실행.** design과 같은 세션에서 하지 않습니다.

**0단계: 직접 풀이** — 해설을 보기 전에 지문+발문만으로 직접 풀이

**검증 8항목**:
1. 정답 유일성
2. 복수 정답 위험 (보기 조합형 ㄱ/ㄴ/ㄷ 일의적 확정)
3. 오답 매력도 (자명한 오답 = Rule 4 위반)
4. 지문 근거 (배경지식만으로 풀리는 선지 금지)
5. W코드 다변화
6. 패러프레이징 (Rule 16)
7. 발문-선지 정합성
8. 해설 논리 (비약·순환 없음)

판정: ❌ 0개 → 확정 / ❌ 있음 → 루프

---

## 지문 빌드 3대 원칙 (프로젝트 총괄자 지침 — 절대 규칙)

1. **일반화**: 고교 수준 배경지식으로 지문 자체는 이해 가능. 변별은 선지 판단에서 발생.
2. **실명 금지**: 마르크스·칸트·하버마스 등 실제 학자명 절대 금지. 갑/을/병, `<이론>`, X국 등으로 일반화.
3. **한국어 전용**: 영어·외국어·학술 약어 금지.

## 영역별 절대 금지

| 영역 | 절대 금지 |
|------|---------|
| **법 (규범)** | 민법·형법·행정법 등 변호사시험 빈출 소재 **절대 금지.** 특별법 영역(환경/교육/소비자/전자상거래 등) 사용. |
| **인문** | 기호 논리학(∀, ∃, →) 과도 사용 금지. '대우' 정도만 허용. 전공 개념은 지문 내 충분한 설명 필수. |
| **사회/과학** | 특별한 금지 없음. 소재 다양화에 초점. |

## 기출 가중치 원칙

**최근 3~5개년 기출이 90% 비중, 이전 기출은 10% 참고용.**
LEET 출제 경향이 해마다 변하므로, 오래된 기출에서 발견된 새로운 W코드/유형을 최근 기출과 동등하게 다루면 안 됩니다.

---

## 코드 체계 요약

### 구성요소 코드 (Building Blocks)

지문은 아래 구성요소의 자유로운 조합:

| 코드 | 구성요소 | 세부 |
|------|---------|------|
| P | 줄글 | 연속 산문 |
| V1 | 견해 (독립) | 갑/을/병 각 1회 |
| V2 | 견해 (대화) | 갑-을-갑-을 교차 |
| R1~R4 | 규정 | 미번호/번호/번호+제목/비조문 |
| C | 사례 | 단일/복수 |
| PR | 원칙 | 해석 기준 |
| AS | 논증구조 | 원문자 문장 나열 |
| MR | 모형규칙 | 순수 추론 규칙 |
| MK | 마커 | ⓐⓑⓒ 참조 지점 |
| T | 표 | 실험/도식/대비/조건/수치 |

### W코드 (오답 생성 원리) — 21개

상위 빈출: W1(결론 방향 역전, 10회), W12(계산 오류, 7회), W15(전문 지식 오류, 6회), W5(규칙 누락, 6회)

전체: `leet_ra/data/w_codes_merged.json` (21개 W코드 + 93개 few-shot)

### AP코드 (매력도 패턴) — 11개

매력도 상: AP1(부분 진실), AP2(직관 부합), AP3(개념 근접), AP4(구조 모방), AP5(다단계 역전)

전체: `leet_ra/data/choice_logic_analysis.json`

### 선지 구성 규칙 — 16개

핵심: Rule 4(매력도 하 금지), Rule 16(패러프레이징 필수)

---

## OMC 전제 시스템

이 레포는 **OMC 설치를 전제**로 작동합니다. 슬래시 커맨드와 자연어 트리거 양쪽 다 Agent 도구로 opus 서브에이전트를 spawn하고, 각 단계마다 기출 JSON에서 타깃 RAG를 주입하는 구조이기 때문에 OMC 없이는 파이프라인이 제대로 돌지 않습니다.

- 자연어 "문항 만들어줘" → OMC가 트리거 감지 → 해당 스킬 활성화 → RAG 주입 → opus spawn
- `/project:*` 슬래시 커맨드 → 동일한 스킬 워크플로우 경유
- review는 반드시 독립 세션에서 별도 spawn (편향 차단)

---

## 프롬프트 수정

에이전트 동작을 바꾸고 싶으면 `leet_ra/prompts/` 안의 md 파일을 편집합니다:

| 파일 | 에이전트 | 수정하면 바뀌는 것 |
|------|---------|-------------------|
| `sourcer.md` | ra-sourcer | 소재 발굴 전략, 영역별 금지/권장, 지문 빌드 세칙 |
| `analyze.md` | ra-analyze (Agent A) | 구성요소 태깅 기준, 출제 포인트 추출 규칙, W코드 매핑 |
| `design.md` | ra-design (Agent B) | 선지 구성 규칙, W코드 다변화, 매력도 게이트 |
| `review.md` | ra-review (Agent C) | 검증 8항목, 직접 풀이 프로토콜, 판정 기준 |

수정 후 재설치 불필요. 다음 `claude` 실행 시 바로 반영됩니다.

---

## 현재 상태 (v1.5)

| 에이전트 | 버전 | 상태 |
|---------|------|------|
| sourcer | v1.6 | 작동 가능. 3대 원칙·세칙 반영 |
| analyze | v1.5 | 작동 가능. 5영역 14소분류 + W코드 + 논증 구조 |
| design | v1.5 | 작동 가능. 규칙 16개 + 매력도 게이트 |
| review | v1.5 | 작동 가능. 8항목 + 직접 풀이 |

**향후 과제**:
- DPO 세칙 보강 (SNG-KO v8.0 수준 목표)
- hwp 출력 파이프라인 구축 (실제 LEET 양식)
- 1세트(40문항) 자동 생성 워크플로우 안정화
- 소재 다양성 관리 (세트 간 중복 방지)

---

## 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| "문항 만들어줘"가 일반 응답으로 나옴 | OMC 미설치 | OMC 플러그인 설치 |
| opus가 아닌 모델로 실행됨 | OMC 미설치 또는 API 키 제한 | OMC 설치 + opus 사용 가능한 플랜 |
| `/project:analyze`이 안 보임 | 다른 디렉토리에서 실행 | `cd leet-ra` 후 `claude` |
| sourcer가 실명/영어를 섞음 | 3대 원칙 미체크 | "빌드 3대 원칙 체크 후 재생성" 요청 |
| review에서 ❌ 반복 | 지문 자체의 출제 포인트 부족 | sourcer로 돌아가 지문 재생성 |
| 오답이 너무 자명함 | 매력도 게이트 미작동 | "매력도 하 선지 제거, 상향 재설계" 지시 |

---

## 참고 사항

- **sourcer가 병목이다.** 좋은 소재 = 좋은 문항.
- **analyze가 엔진이다.** 출제 포인트 추출 품질이 전체를 결정.
- **review는 반드시 독립 세션.** 편향 차단 핵심.
- 패키지 내 원본 자료는 `leet_ra/README_개발가이드.md`와 초기 보고서 참조.
- LEET 09~26학년도 전 연도 기출 PDF·HWP, 시대인재 모의고사, 교열 매뉴얼 등은 용량 문제로 레포에 포함되지 않습니다. 필요 시 별도 전달.

---

## 버전

| 컴포넌트 | 버전 | 주요 특징 |
|---------|------|----------|
| sourcer | v1.6 | 빌드 3대 원칙 + 영역별 금지 + 규정 세칙 |
| analyze (Agent A) | v1.5 | 5영역 14소분류 + W코드 매핑 + 논증 구조 |
| design (Agent B) | v1.5 | 선지 구성 규칙 16개 + Rule 4/16 |
| review (Agent C) | v1.5 | 검증 8항목 + 직접 풀이 프로토콜 |
| taxonomy | v0.3 | 2024+2025 교차 검증 구성요소 통계 |
