#!/bin/bash

# ============================================================
# OneOnOne 개발 서버 실행 스크립트
# 백엔드(Spring Boot :8080) + 프론트엔드(Next.js :3000) 동시 실행
# 종료: Ctrl+C  |  외부 종료: ./stop.sh
# ============================================================

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/starter-kit"
PID_FILE="$ROOT_DIR/.dev-pids"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ============================================================
# 포트로 프로세스 종료 (Gradle은 자식 JVM을 생성하므로 PID보다 포트가 신뢰성 높음)
# ============================================================
kill_port() {
    local port=$1
    local pids
    pids=$(lsof -ti:"$port" 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill -TERM 2>/dev/null
        sleep 1
        # 아직 살아있으면 강제 종료
        pids=$(lsof -ti:"$port" 2>/dev/null)
        [ -n "$pids" ] && echo "$pids" | xargs kill -9 2>/dev/null
    fi
}

cleanup() {
    echo ""
    echo -e "${YELLOW}서버를 종료합니다...${NC}"
    kill_port 8080 && echo -e "${BLUE}[백엔드]${NC} 종료됨 (포트 8080)"
    kill_port 3000 && echo -e "${CYAN}[프론트]${NC} 종료됨 (포트 3000)"
    rm -f "$PID_FILE"
    exit 0
}

trap cleanup SIGINT SIGTERM

# ============================================================
# 포트 선점 확인
# ============================================================
check_port_free() {
    local port=$1
    if lsof -ti:"$port" &>/dev/null; then
        echo -e "${YELLOW}[경고]${NC} 포트 $port 이미 사용 중 → 기존 프로세스 종료"
        kill_port "$port"
        sleep 1
    fi
}

# ============================================================
# 사전 확인
# ============================================================
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  OneOnOne 개발 서버 시작${NC}"
echo -e "${GREEN}=====================================${NC}"

command -v java &>/dev/null || { echo -e "${RED}[오류] Java 미설치${NC}"; exit 1; }
command -v node &>/dev/null || { echo -e "${RED}[오류] Node.js 미설치${NC}"; exit 1; }

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${CYAN}[프론트]${NC} node_modules 없음 → npm install 실행 중..."
    (cd "$FRONTEND_DIR" && npm install --silent)
fi

check_port_free 8080
check_port_free 3000

# ============================================================
# 환경변수 로드
# ============================================================
if [ -f "$BACKEND_DIR/.env" ]; then
    echo -e "${BLUE}[백엔드]${NC} .env 파일 로드됨"
    set -a; source "$BACKEND_DIR/.env"; set +a
else
    echo -e "${YELLOW}[백엔드]${NC} .env 없음 → Jira 연동 비활성화 상태"
    echo -e "         ($BACKEND_DIR/.env.example 참조)"
fi

# ============================================================
# 백엔드 실행
# ============================================================
echo ""
echo -e "${BLUE}[백엔드]${NC} Spring Boot 시작 중... (포트 8080)"

(
    cd "$BACKEND_DIR"
    ./gradlew bootRun --console=plain 2>&1 | while IFS= read -r line; do
        echo -e "${BLUE}[BE]${NC} $line"
    done
) &
echo $! >> "$PID_FILE"

# 백엔드 준비 대기 (최대 90초)
echo -e "${BLUE}[백엔드]${NC} 헬스체크 대기 중..."
for i in $(seq 2 2 90); do
    sleep 2
    if curl -sf http://localhost:8080/api/health >/dev/null 2>&1; then
        echo -e "${GREEN}[백엔드]${NC} 준비 완료 (${i}s) → http://localhost:8080"
        break
    fi
    if [ "$i" -ge 90 ]; then
        echo -e "${RED}[오류]${NC} 백엔드가 90초 내에 시작되지 않았습니다"
        cleanup; exit 1
    fi
    [ $((i % 10)) -eq 0 ] && echo -e "${BLUE}[백엔드]${NC} 대기 중... (${i}s)"
done

# ============================================================
# 프론트엔드 실행
# ============================================================
echo ""
echo -e "${CYAN}[프론트]${NC} Next.js 시작 중... (포트 3000)"

(
    cd "$FRONTEND_DIR"
    npm run dev 2>&1 | while IFS= read -r line; do
        echo -e "${CYAN}[FE]${NC} $line"
    done
) &
echo $! >> "$PID_FILE"

sleep 3

# ============================================================
# 실행 정보
# ============================================================
echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  실행 완료${NC}"
echo -e "${GREEN}=====================================${NC}"
echo -e "  프론트엔드  → ${CYAN}http://localhost:3000${NC}"
echo -e "  백엔드 API  → ${BLUE}http://localhost:8080${NC}"
echo -e "  H2 콘솔     → ${BLUE}http://localhost:8080/h2-console${NC}"
echo ""
echo -e "  종료: ${YELLOW}Ctrl+C${NC}  또는  ${YELLOW}./stop.sh${NC}"
echo -e "${GREEN}=====================================${NC}"

wait
