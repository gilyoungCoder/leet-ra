LEET 추리논증 소재 발굴 + 지문 초안 생성 (Sourcer v1.6)

**OMC 전제.** 이 커맨드는 `ra-sourcer` OMC 스킬을 통해 opus 서브에이전트를 spawn한다.

## 실행 지시

1. `/mnt/home3/yhgil99/.claude/` 또는 프로젝트 `.omc/skills/ra-sourcer/SKILL.md`의 Workflow를 **그대로** 따른다.
2. 즉, 아래 순서를 지킨다:
   - Step 1: `leet_ra/prompts/sourcer.md` 전문 Read
   - Step 1b: 입력 영역 → leet_type 매핑(법→D*, 인문→A*, 사회→C*/E*, 과학→C*, 논쟁→E*)으로 `leet_ra/data/2025_merged.json`과 `2024_merged.json`에서 동일 유형 `passage_text` 2~3개 필터 (2025 우선)
   - Step 2: `Agent(name="ra-sourcer", model="opus", mode="auto", prompt=...)` — prompt에 sourcer.md 전문 + 입력 + few-shot 참조 + 중복 방지 리스트 포함
   - Step 3: 결과를 사용자에게 전달, 승인 후 ra-analyze로 릴레이

## 지시 원칙

- 빌드 3대 원칙(일반화 / 실명 금지 / 한국어 전용) 절대 준수.
- 영역별 금지(법: 민·형·행정 ❌ → 특별법 / 인문: 기호 논리학 과도 사용 ❌).
- 서브에이전트 호출 전에 RAG 주입을 **반드시** 수행. 주입 없이 spawn 금지.

## 입력

$ARGUMENTS
