# GitHub Pages 배포 가이드

원온원(OneOnOne) 애플리케이션을 GitHub Pages에 배포하는 방법을 안내합니다.

## 📋 사전 준비사항

- GitHub 계정
- Git 설치
- 로컬에 프로젝트 저장소 클론

## 🚀 배포 단계

### 1. GitHub 저장소 생성

1. GitHub에 로그인
2. 새 저장소 생성 (예: `oneonone` 또는 `your-username.github.io`)
3. 공개(Public) 저장소로 설정

### 2. 로컬 저장소 연결

```bash
# 현재 디렉토리가 claude-lab인지 확인
pwd

# GitHub 저장소를 원격으로 추가 (아직 추가하지 않은 경우)
git remote add origin https://github.com/your-username/oneonone.git

# 또는 기존 원격 저장소 확인
git remote -v
```

### 3. 파일 커밋 및 푸시

```bash
# 변경사항 스테이징
git add docs/
git add RoadMap.md
git add GITHUB_PAGES_DEPLOY.md

# 커밋
git commit -m "원온원 프론트엔드 GitHub Pages 배포 준비"

# GitHub에 푸시
git push -u origin main
```

### 4. GitHub Pages 활성화

1. GitHub 저장소 페이지로 이동
2. **Settings** 탭 클릭
3. 왼쪽 메뉴에서 **Pages** 클릭
4. **Source** 섹션에서:
   - Branch: `main` 선택
   - Folder: `/docs` 선택
5. **Save** 버튼 클릭

### 5. 배포 확인

- 약 1-2분 후 배포 완료
- 페이지 상단에 배포 URL이 표시됩니다:
  ```
  Your site is live at https://your-username.github.io/oneonone/
  ```

## 🔧 백엔드 서버 설정

GitHub Pages는 정적 사이트만 호스팅하므로, Spring Boot 백엔드는 별도로 배포해야 합니다.

### 백엔드 배포 옵션

#### 옵션 1: Heroku (무료/유료)
```bash
# Heroku CLI 설치 후
heroku create oneonone-api
git push heroku main
```

#### 옵션 2: AWS EC2
- EC2 인스턴스 생성
- Spring Boot JAR 업로드
- 포트 8080 오픈

#### 옵션 3: Google Cloud Run
```bash
# Docker 이미지 빌드 및 배포
gcloud run deploy oneonone-api --source .
```

#### 옵션 4: Railway.app (추천 - 간편)
1. https://railway.app 접속
2. GitHub 저장소 연결
3. 자동 배포

### 백엔드 URL 설정

배포 후 프론트엔드에서 백엔드 URL을 업데이트하세요:

**docs/index.html** 파일에서:
```html
<input
    type="text"
    id="apiEndpoint"
    placeholder="https://your-backend-api.com"
    class="..."
    value="https://your-backend-api.herokuapp.com"  <!-- 여기를 실제 백엔드 URL로 변경 -->
>
```

## 📁 프로젝트 구조

배포 후 구조:

```
claude-lab/
├── docs/                        # GitHub Pages 소스 (이 폴더가 웹사이트로 배포됨)
│   ├── index.html              # 메인 페이지
│   ├── css/
│   │   └── styles.css          # 커스텀 스타일
│   ├── js/
│   │   ├── upload.js           # 파일 업로드 로직
│   │   ├── analysis.js         # 분석 결과 표시
│   │   └── document.js         # 문서 생성 UI
│   └── images/                 # 이미지 파일 (필요시)
├── backend/                     # Spring Boot 백엔드 (별도 배포)
├── RoadMap.md
└── GITHUB_PAGES_DEPLOY.md
```

## 🔄 업데이트 배포

코드를 수정한 후 다시 배포하려면:

```bash
# 변경사항 스테이징
git add docs/

# 커밋
git commit -m "UI 개선 및 버그 수정"

# 푸시 (자동으로 GitHub Pages 업데이트됨)
git push origin main
```

GitHub Pages는 푸시 후 자동으로 새 버전을 배포합니다 (1-2분 소요).

## 🌐 커스텀 도메인 설정 (선택사항)

본인 소유 도메인을 사용하려면:

1. GitHub Pages 설정에서 **Custom domain** 입력
2. 도메인 제공업체(가비아, 후이즈 등)에서 DNS 설정:
   ```
   Type: CNAME
   Name: www
   Value: your-username.github.io
   ```

## ✅ 배포 체크리스트

- [ ] `docs/` 폴더에 모든 프론트엔드 파일 준비
- [ ] GitHub 저장소 생성 및 코드 푸시
- [ ] GitHub Pages 설정 (Settings → Pages)
- [ ] 배포 URL 확인 및 테스트
- [ ] 백엔드 서버 별도 배포
- [ ] 프론트엔드에서 백엔드 API URL 설정
- [ ] CORS 설정 확인 (백엔드에서 프론트엔드 도메인 허용)
- [ ] 실제 데이터로 전체 플로우 테스트

## 🐛 문제 해결

### 404 에러가 발생하는 경우
- GitHub Pages 설정에서 `/docs` 폴더가 선택되었는지 확인
- 브랜치가 `main`으로 설정되었는지 확인

### CSS/JS 파일이 로드되지 않는 경우
- HTML의 리소스 경로가 상대 경로인지 확인
- 브라우저 콘솔에서 오류 메시지 확인

### API 호출이 실패하는 경우
- 백엔드 서버가 실행 중인지 확인
- CORS 설정 확인:
  ```kotlin
  // Spring Boot에서
  @CrossOrigin(origins = ["https://your-username.github.io"])
  ```

### 변경사항이 반영되지 않는 경우
- 브라우저 캐시 삭제 (Ctrl + Shift + R / Cmd + Shift + R)
- GitHub Actions 탭에서 배포 상태 확인

## 📞 추가 도움

- [GitHub Pages 공식 문서](https://docs.github.com/en/pages)
- [Tailwind CSS 문서](https://tailwindcss.com/docs)
- 이슈가 있다면 저장소의 Issues 탭에 문의

---

**축하합니다! 🎉**

원온원 애플리케이션이 성공적으로 배포되었습니다.
이제 전 세계 어디서나 접속할 수 있습니다!
