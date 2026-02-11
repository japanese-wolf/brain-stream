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

<p align="center">
  <a href="https://github.com/japanese-wolf/brain-stream/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-AGPL%20v3-blue.svg" alt="License"></a>
</p>

---

## 왜 BrainStream인가?

LLM에게 무엇이든 물어볼 수 있습니다 -- 하지만 무엇을 물어봐야 하는지 알아야 합니다. BrainStream은 **"알지 못하는 것을 모르는" 문제**를 해결합니다: 찾으려고 하지도 않았던 기술과 트렌드를 발견하게 해줍니다.

BrainStream은 **Claude Code 플러그인**으로 작동하는 개인 기술 정보 에이전트입니다. 여러 소스에서 기사를 수집하고, 구조화된 요약을 생성하고, 주제별로 클러스터링하고, 계층적 다이제스트를 제공합니다 — 모두 개발 워크플로 안에서.

### 주요 기능

- **에이전트 기반 수집**: LLM 에이전트가 구성된 소스에서 자율적으로 기사를 가져오고 처리
- **구조화된 요약**: 각 기사를 What / Who / Why it matters 형식으로 요약
- **계층적 다이제스트**: 전체 개요 → 클러스터 트렌드 → 개별 기사
- **1차 소스 감지**: 공식 벤더 발표 (🏷️)와 2차 커버리지 (📝)를 구분
- **다중 소스 집계**: AWS, GCP, OpenAI, Anthropic, GitHub
- **로컬 우선**: 데이터는 프로젝트의 `.claude/brainstream/` 디렉토리에 저장
- **외부 의존성 없음**: Claude Code의 내장 도구 (WebFetch, Read, Write) 사용

## 빠른 시작

### 설치

```bash
# Claude Code 플러그인으로 설치
claude plugin add github:japanese-wolf/brain-stream

# 또는 개발용으로 로컬 로드
claude --plugin-dir /path/to/brain-stream
```

### 사용법

```bash
# 오늘의 기술 다이제스트 생성
/brainstream:digest

# 특정 벤더에서만 가져오기
/brainstream:digest AWS

# 오늘의 캐시 데이터 사용
/brainstream:digest cached
```

### 출력 예시

```markdown
# Tech Digest — 2026-02-11

## 개요
6개 소스에서 24개 기사를 수집하여 5개 클러스터로 분류했습니다.
주요 트렌드: AI 모델 배포 비용 감소 추세; GitHub Actions에 대규모 보안 업데이트.

## AI Infrastructure
> 여러 벤더가 모델 서빙의 비용 최적화 기능을 출시.

### Amazon Bedrock Claude 모델 가격 인하 🏷️
**What**: AWS가 Anthropic 모델의 Bedrock 가격을 30% 인하.
**Who**: AWS
**Why it matters**: 프로덕션 LLM 배포의 장벽이 낮아짐.
🔗 https://aws.amazon.com/...
```

## 아키텍처

```
┌──────────────────────────────────────────────────────┐
│                  BrainStream Plugin                    │
├──────────────────────────────────────────────────────┤
│                                                       │
│  /brainstream:digest                                  │
│       │                                               │
│       ├── WebFetch ──> RSS/HTML 소스                   │
│       │                                               │
│       ├── LLM ──> 요약 (What/Who/Why)                 │
│       │                                               │
│       ├── LLM ──> 주제별 클러스터링                     │
│       │                                               │
│       └── Write ──> .claude/brainstream/              │
│                     ├── cache/YYYY-MM-DD.json         │
│                     └── digests/YYYY-MM-DD.md         │
└──────────────────────────────────────────────────────┘
```

## 데이터 소스

| 소스 | 벤더 | 유형 | 설명 |
|--------|---------|--------|------|
| aws-whatsnew | AWS | RSS | AWS 새 소식 |
| gcp-release-notes | GCP | RSS | GCP 릴리스 노트 |
| openai-blog | OpenAI | RSS | OpenAI 블로그 업데이트 |
| anthropic-news | Anthropic | Scrape | Anthropic 릴리스 노트 |
| github-blog | GitHub | RSS | GitHub Blog |
| github-changelog | GitHub | RSS | GitHub Changelog |

## 데이터 저장소

런타임 데이터는 프로젝트의 `.claude/brainstream/` 디렉토리에 저장됩니다:

```
.claude/brainstream/
├── cache/
│   └── 2026-02-11.json    # 기사 원본 데이터 (JSON)
└── digests/
    └── 2026-02-11.md      # 생성된 다이제스트 (Markdown)
```

## 요구 사항

- [Claude Code](https://claude.ai/code) 1.0.33+

## 기여

기여를 환영합니다! 가이드라인은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

## 라이선스

이 프로젝트는 GNU Affero General Public License v3.0에 따라 라이선스가 부여됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
