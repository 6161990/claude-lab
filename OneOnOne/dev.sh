#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
PID_FILE="$SCRIPT_DIR/.dev.pids"

start() {
  if [ -f "$PID_FILE" ]; then
    echo "이미 실행 중입니다. 'stop' 먼저 실행하세요."
    exit 1
  fi

  echo "백엔드 시작 중..."
  cd "$BACKEND_DIR"
  if [ -f ".env" ]; then
    set -a; source .env; set +a
  fi
  ./gradlew bootRun > "$SCRIPT_DIR/backend.log" 2>&1 &
  BACKEND_PID=$!

  echo "프론트엔드 시작 중..."
  cd "$FRONTEND_DIR"
  if [ ! -d "node_modules" ]; then
    echo "npm install 실행 중..."
    npm install
  fi
  npm run dev > "$SCRIPT_DIR/frontend.log" 2>&1 &
  FRONTEND_PID=$!

  echo "$BACKEND_PID $FRONTEND_PID" > "$PID_FILE"

  echo ""
  echo "실행 완료"
  echo "  백엔드:   http://localhost:8080  (PID: $BACKEND_PID)"
  echo "  프론트엔드: http://localhost:3000  (PID: $FRONTEND_PID)"
  echo ""
  echo "로그 확인:  tail -f $SCRIPT_DIR/backend.log"
  echo "           tail -f $SCRIPT_DIR/frontend.log"
  echo "종료:       ./dev.sh stop"
}

stop() {
  if [ ! -f "$PID_FILE" ]; then
    echo "실행 중인 프로세스가 없습니다."
    exit 0
  fi

  read -r BACKEND_PID FRONTEND_PID < "$PID_FILE"

  echo "백엔드 종료 중... (PID: $BACKEND_PID)"
  kill "$BACKEND_PID" 2>/dev/null
  # Gradle bootRun은 자식 프로세스(JVM)도 함께 종료
  pkill -P "$BACKEND_PID" 2>/dev/null

  echo "프론트엔드 종료 중... (PID: $FRONTEND_PID)"
  kill "$FRONTEND_PID" 2>/dev/null
  pkill -P "$FRONTEND_PID" 2>/dev/null

  rm -f "$PID_FILE"
  echo "종료 완료"
}

logs() {
  tail -f "$SCRIPT_DIR/backend.log" "$SCRIPT_DIR/frontend.log"
}

case "${1:-start}" in
  start) start ;;
  stop)  stop ;;
  logs)  logs ;;
  *)
    echo "사용법: ./dev.sh [start|stop|logs]"
    exit 1
    ;;
esac
