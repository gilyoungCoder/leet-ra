LEET 추리논증 문항 출력 (hwpx / docx)

**OMC 전제.** `ra-exporter` 스킬을 호출하여 review 통과한 문항 JSON을 한글 파일로 출력한다.

## 실행 지시

`.omc/skills/ra-exporter/SKILL.md` Workflow를 그대로 따른다:

1. 이전 대화에서 review ❌ 0개 통과한 문항 세트를 확인한다 (미통과 시 export 거부)
2. 사용자 입력에서 양식 판별:
   - "서바" 단어 포함 → `--format serva`
   - "전국" 단어 포함 → `--format jeonguk`
   - 그 외 / "시대인재" / 명시 없음 → `--format default`
3. 문항 JSON을 `output/tmp_<timestamp>.json` 으로 저장 (또는 사용자 지정 경로)
4. Bash로 exporter 실행:

```bash
python3 leet_ra/exporter/export_hwpx.py \
  --input <JSON 경로> \
  --format <default|jeonguk|serva> \
  --title "<제목>"

# docx 대체 출력(옵션)
python3 leet_ra/exporter/export_docx.py -i <JSON> -o output/<레이블>.docx -t "<제목>"
```

5. 생성된 파일 경로를 사용자에게 전달

## 주의

- 양식별 템플릿은 시대인재 실제 제작 hwpx에서 본문 텍스트만 비운 빈 템플릿 — 표/2단/헤더 레이아웃은 그대로 유지.
- 완벽한 스타일 재현은 한컴에서 후처리 가능.
- review 미통과 문항은 export 금지.

## 입력

$ARGUMENTS
