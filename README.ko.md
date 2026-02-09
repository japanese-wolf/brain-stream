# BrainStream

> **주의**: 이 프로젝트는 현재 개발 중이며 아직 공개되지 않았습니다. API와 기능은 사전 통지 없이 변경될 수 있습니다.

<p align="center">
  <img src="docs/icon/icon.svg" alt="BrainStream Logo" width="200">
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

### 토폴로지 기반 세렌디피티

BrainStream은 **정보 공간 토폴로지**를 활용하여 사용자 프로필이나 개인화 없이 자연스럽게 세렌디피티를 생성합니다:

- **밀집 클러스터**는 잘 다루어진 주제 -- 동료 엔지니어들이 이미 읽고 있는 기사
- **클러스터 경계의 희소 영역**이 분야 간 새로운 연결을 드러냄
- **Thompson Sampling**이 새로운 주제 탐색과 알려진 관심사 활용을 자동 조절

> 콜드 스타트 문제 없음. 필터 버블 없음. 정보의 구조 자체가 발견을 이끕니다.

### 주요 기능

- **설계에 의한 세렌디피티**: 토폴로지 기반 발견이 기술 도메인 간 예상치 못한 연결을 표면화
- **다중 소스 집계**: AWS, GCP, OpenAI, Anthropic, GitHub Releases, GitHub OSS
- **AI 분석**: 기존 Claude Code CLI 구독 활용 (온디맨드, 백그라운드 비용 없음)
- **1차 소스 감지**: 공식 벤더 발표와 2차 커버리지를 구분
- **로컬 우선**: 데이터는 사용자의 머신에 저장
- **플러그인 아키텍처**: 새로운 데이터 소스를 쉽게 추가

## 빠른 시작

### 설치

```bash
pip install brainstream
```

### 기본 명령어

```bash
brainstream serve         # API 서버 시작
brainstream fetch         # 모든 소스에서 기사 가져오기
brainstream status        # 기사 수, 클러스터, 토폴로지 정보 표시
brainstream sources       # 사용 가능한 데이터 소스 목록
```

## 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│                        BrainStream                           │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │   플러그인    │───>│   프로세서    │───>│    스토리지   │   │
│  │  (RSS, API)  │    │  (LLM CLI)   │    │(ChromaDB+SQL)│   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│                              │                    │          │
│                   ┌──────────┴──────────┐         │          │
│                   │ 토폴로지 엔진       │         │          │
│                   │ (HDBSCAN +          │         │          │
│                   │  Thompson Sampling) │         │          │
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
