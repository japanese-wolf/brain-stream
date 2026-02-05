# BrainStream

<p align="center">
  <img src="docs/logo.png" alt="BrainStream Logo" width="200">
</p>

<p align="center">
  <strong>클라우드 및 AI 업데이트를 위한 인텔리전스 허브</strong>
</p>

<p align="center">
  <a href="README.md">English</a> |
  <a href="docs/README.ja.md">日本語</a> |
  <a href="docs/README.zh.md">中文</a> |
  <a href="docs/README.ko.md">한국어</a>
</p>

---

## BrainStream이란?

BrainStream은 엔지니어가 클라우드 제공업체와 AI 벤더의 업데이트를 수동적으로 집계할 수 있도록 도와주는 오픈소스 인텔리전스 허브입니다. 기술 스택에 따라 뉴스를 자동으로 수집, 요약 및 우선순위를 지정합니다.

### 주요 기능

- **다중 소스 집계**: AWS, GCP, OpenAI, Anthropic, GitHub Releases
- **AI 기반 요약**: 기존 Claude Code 또는 Copilot CLI 구독 활용
- **개인화된 피드**: 기술 스택 기반 관련성 점수
- **로컬 우선**: 데이터는 사용자의 머신에 저장
- **플러그인 아키텍처**: 새로운 데이터 소스를 쉽게 추가

## 빠른 시작

### 설치

```bash
pip install brainstream
```

### 설정

```bash
# 대화형 설정 마법사
brainstream setup

# 서버 시작 (브라우저 자동 열기)
brainstream open
```

### 기본 명령어

```bash
brainstream open          # 서버 시작 및 대시보드 열기
brainstream fetch         # 수동으로 새 기사 가져오기
brainstream status        # 수집 통계 표시
brainstream sources       # 사용 가능한 데이터 소스 목록
```

### 옵션

```bash
brainstream open --no-browser      # 브라우저 열지 않기
brainstream open --port 3000       # 포트 지정
brainstream open --no-scheduler    # 자동 가져오기 비활성화
brainstream open --fetch-interval 60  # 가져오기 간격을 60분으로 설정
brainstream fetch --skip-llm       # LLM 처리 건너뛰기
```

## 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                       BrainStream                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   플러그인    │───▶│   프로세서    │───▶│    스토리지   │  │
│  │  (RSS, API)  │    │  (LLM CLI)   │    │  (SQLite)    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│          │                                       │          │
│          ▼                                       ▼          │
│  ┌──────────────┐                       ┌──────────────┐   │
│  │   스케줄러    │                       │   대시보드    │   │
│  │  (30분 간격)  │                       │  (React)     │   │
│  └──────────────┘                       └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 요구 사항

- Python 3.11+
- Node.js 18+ (프론트엔드 개발용)
- Claude Code CLI 또는 GitHub Copilot CLI (AI 요약용, 선택 사항)

## 개발

```bash
# 저장소 클론
git clone https://github.com/xxx/brain-stream.git
cd brain-stream

# 백엔드 설정
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 프론트엔드 설정
cd ../frontend
npm install
npm run dev
```

## Docker

```bash
# 프로덕션
docker-compose up -d

# 개발 (핫 리로드 포함)
docker-compose -f docker-compose.dev.yml up
```

## 데이터 소스

| 소스 | 벤더 | 유형 | 설명 |
|--------|---------|--------|------|
| aws-whatsnew | AWS | RSS | AWS 새 소식 |
| gcp-release-notes | GCP | RSS | GCP 릴리스 노트 |
| openai-changelog | OpenAI | RSS | OpenAI 블로그 업데이트 |
| anthropic-changelog | Anthropic | Scrape | Anthropic 릴리스 노트 |
| github-releases | GitHub | API | GitHub 저장소 릴리스 |

## 기여

기여를 환영합니다! 가이드라인은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

## 라이선스

이 프로젝트는 GNU Affero General Public License v3.0에 따라 라이선스가 부여됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
