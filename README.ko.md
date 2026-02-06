# BrainStream

> **주의**: 이 프로젝트는 현재 개발 중이며 아직 공개되지 않았습니다. API와 기능은 사전 통지 없이 변경될 수 있습니다.

<p align="center">
  <img src="docs/logo.png" alt="BrainStream Logo" width="200">
</p>

<p align="center">
  <strong>몰랐던 것을 발견하다</strong>
</p>

<p align="center">
  <a href="README.md">English</a> |
  <a href="README.ja.md">日本語</a> |
  <a href="README.zh.md">中文</a> |
  <a href="README.ko.md">한국어</a>
</p>

---

## 왜 BrainStream인가?

LLM에게 무엇이든 물어볼 수 있습니다 -- 하지만 무엇을 물어봐야 하는지 알아야 합니다. BrainStream은 **"알지 못하는 것을 모르는" 문제**를 해결합니다: 찾으려고 하지도 않았던 기술과 트렌드를 발견하게 해줍니다.

### 양방향 발견

BrainStream은 두 가지 상호보완적인 방향으로 발견을 가속합니다:

**방향 A: 알려진 것 → 알려지지 않은 것** (필터 버블 탈피)
- Lambda 전문가라도 WASM 런타임이 서버리스를 변화시키고 있다는 것을 모를 수 있습니다
- 동시출현 분석이 당신의 스택 주변의 떠오르는 기술을 식별합니다 -- LLM 불필요, 데이터가 많을수록 정확도 향상

**방향 B: 알려지지 않은 것 → 알려진 것** (이해 가속)
- WASM 기사가 피드에 나타나면, 당신의 Lambda 경험과 어떻게 연관되는지 설명합니다
- AI 기반 컨텍스트 앵커링이 새로운 정보를 이미 알고 있는 것과 연결합니다

> 한 사용자가 한 도메인에서는 방향 A(전문가), 다른 도메인에서는 방향 B(학습자)일 수 있습니다. BrainStream은 양쪽 모두를 지원합니다.

### 주요 기능

- **발견 가속**: 당신의 분야에서 트렌딩 기술 + 개인화된 기술 연결
- **다중 소스 집계**: AWS, GCP, OpenAI, Anthropic, GitHub Releases, GitHub OSS
- **AI 분석**: 기존 Claude Code CLI 구독 활용 (온디맨드, 백그라운드 비용 없음)
- **개인화된 피드**: 기술 스택, 도메인, 역할, 목표 기반 관련성 점수
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

## 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│                        BrainStream                           │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │   플러그인    │───>│   프로세서    │───>│    스토리지   │   │
│  │  (RSS, API)  │    │  (LLM CLI)   │    │  (SQLite)    │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│                              │                    │          │
│                   ┌──────────┴──────────┐         │          │
│                   │  동시출현 분석       │         │          │
│                   │  (방향 A)           │         │          │
│                   └─────────────────────┘         │          │
│                                                   ▼          │
│                                           ┌──────────────┐   │
│                                           │   대시보드    │   │
│                                           │  (React)     │   │
│                                           └──────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## 요구 사항

- Python 3.11+
- Node.js 18+ (프론트엔드 개발용)
- Claude Code CLI (AI 분석용, 선택 사항)

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
