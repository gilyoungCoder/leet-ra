#!/usr/bin/env bash
# LEET-RA 원샷 셋업 스크립트
# 사용: bash setup.sh

set -e
cd "$(dirname "$0")"

echo "[1/3] Python 의존성 설치 (python-hwpx, hwpx-mcp-server, python-docx)"
pip install -r requirements.txt

echo ""
echo "[2/3] 검증 — python-hwpx import + MCP 서버 실행 파일 확인"
python3 -c "from hwpx import HwpxDocument; print('python-hwpx:', HwpxDocument.__module__)"
which hwpx-mcp-server || (echo "hwpx-mcp-server 실행 파일 없음. pip 경로 확인 필요." && exit 1)

echo ""
echo "[3/3] 샘플 hwpx 생성 테스트"
python3 leet_ra/exporter/export_hwpx.py \
  -i samples/v2_5questions.json \
  -o output/setup_test.hwpx \
  -t "LEET-RA 셋업 테스트" 2>&1 | grep -v "manifest에서"
ls -la output/setup_test.hwpx

echo ""
echo "✅ 셋업 완료"
echo ""
echo "다음 단계:"
echo "  1) Claude Code 미설치 시:  npm install -g @anthropic-ai/claude-code"
echo "  2) OMC 미설치 시:          claude 실행 후 /plugin install oh-my-claudecode"
echo "  3) 프로젝트 시작:          claude  (.mcp.json 자동 로드)"
echo ""
echo "자연어 예시:"
echo "  - '특별법 영역으로 법 1문항 만들어줘'"
echo "  - '풀 파이프라인 돌려줘'"
echo "  - 'hwpx로 뽑아줘'"
