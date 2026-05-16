# Streamlit Community Cloud 배포 가이드

이 대시보드를 [share.streamlit.io](https://share.streamlit.io) 에 무료 배포하는 방법.

---

## 🚀 옵션 D: V2 Top3 경량 배포 (NEW · 가장 간단 · 권장)

2026-05-14 부터 `app.py` 가 **온라인 모드 자동 감지** 를 지원합니다.

- 큰 원본 데이터 (`data/market/daily_ohlcv/*.parquet`, `data/market/minute_ohlcv/`, `data/dart/`) 가 없으면 자동으로 **V2 Top3 paper watch 화면만** 표시
- repo 안에 동봉되는 데이터는 **`data/closingbell/online_v2/latest/`** (수 MB) 만
- 일봉/분봉 차트 같은 무거운 기능은 자동으로 숨김 — 코드 수정 불필요

### 5 분 절차

```powershell
# 1) git 초기화 (한 번만)
cd C:\Coding\projects\bell-dashboard
git init
git add app.py requirements.txt README.md STREAMLIT_CLOUD.md ONLINE_V2_DATA.md `
        CLOUDFLARE_TUNNEL.md .gitignore data/closingbell/online_v2 scripts
git commit -m "Initial commit — V2 Top3 paper watch dashboard"

# 2) GitHub 새 repo 생성 (예: closingbell-dashboard) 후
git remote add origin https://github.com/<YOUR_USER>/closingbell-dashboard.git
git branch -M main
git push -u origin main

# 3) https://share.streamlit.io → New app
#    - Repository: <YOUR_USER>/closingbell-dashboard
#    - Branch: main
#    - Main file path: app.py
#    - Python version: 3.12 (또는 3.11)
#    Deploy 클릭 — 1~2분 후 URL 발급
```

### 매일 V2 스냅샷 갱신

로컬 PC 의 `bell-data` 가 매일 14:55 preclose / 15:02 V2 minute / 17:05 postclose 실행 시 자동으로 `data/closingbell/online_v2/` 폴더를 갱신합니다.
이후:

```powershell
cd C:\Coding\projects\bell-dashboard
.\scripts\publish_online_v2_to_github.ps1 -Push
# 또는 환경변수: $env:CLOSINGBELL_ONLINE_V2_GIT_PUSH = "true"
```

Streamlit Cloud 는 GitHub push 감지 시 1~2분 안에 자동 재배포됩니다.

### 동작 확인

- 로컬: `streamlit run app.py` → 7 탭 다 보임 (`IS_ONLINE_MODE=False`)
- Streamlit Cloud: 자동 감지 → "🌐 온라인 모드" 안내 + V2 Top3 paper watch 화면만 (`IS_ONLINE_MODE=True`)
- 분봉/일봉 차트가 없는 것 외에는 V2 Top3 카드·점수 등급·진입 가이드·백데이터 요약·overlay·제외 후보 모두 정상

> ⚠ Streamlit Cloud 는 미국·EU 리전 서버라 한국 시간 14:55 슬롯 직후 접속 시 약간의 지연이 있을 수 있습니다. 매일 1~2회 확인용으로는 충분합니다.

---

## 데이터 동기화 — 가장 큰 결정

대시보드는 `C:\Coding\data` 아래 약 **수GB의 parquet/csv** 를 읽습니다. Streamlit Cloud는 GitHub repo 안의 파일만 읽을 수 있어 분봉 parquet(수천 종목 × 수년치)을 통째로 올리는 건 비현실적입니다.

3가지 옵션:

### 옵션 A: 핵심 CSV만 GitHub repo에 — 분봉 차트 비활성 (권장 시작점)
- repo에 포함: 1년치 backdata CSV (`*_1y.csv`), 글로벌 지수 CSV, stock_mapping.csv
- repo에서 제외: `data/market/daily_ohlcv/*.parquet`, `data/market/minute_ohlcv/*.parquet`, `data/dart/*` (수GB)
- **결과**: 통계/메모/오늘 후보 텍스트는 동작, 일봉/분봉/매매주체 차트는 빈 안내
- **장점**: 무료, 0원, 5분 세팅
- **용량**: ~10MB

### 옵션 B: S3 / GCS / R2 에 데이터 업로드 + Streamlit Cloud는 코드만
- 클라우드 스토리지에 `data/` 트리 업로드
- 앱이 `boto3` / `gcsfs` / `s3fs` 로 읽음 — `BELL_DATA_ROOT=s3://my-bucket/closingbell/` 같은 URI
- **장점**: 풀 기능
- **단점**: 월 $1~5 비용, fsspec/boto3 코드 추가 필요, 첫 로드 느림

### 옵션 C: Cloudflare Tunnel (별도 가이드 [CLOUDFLARE_TUNNEL.md](CLOUDFLARE_TUNNEL.md))
- Streamlit Cloud 배포 안 함, 본인 PC에서 streamlit 띄우고 외부 접속
- **장점**: 데이터 그대로, 풀 기능, 무료
- **단점**: PC가 켜져 있어야 함

**현재 추천**: 우선 **옵션 C**(Cloudflare Tunnel)로 시작 → 데이터 동기화 자동화 끝나면 옵션 B로 전환.

## 옵션 A 상세 절차

### 1. GitHub repo 생성

```powershell
cd C:\Coding\projects\bell-dashboard
git init
git add app.py requirements.txt README.md *.md
```

`.gitignore` 작성:

```
__pycache__/
.venv/
*.pyc
# 큰 데이터는 별도 저장소 / 클라우드로
```

`requirements.txt` 추가:

```
streamlit==1.45.0
plotly==6.0.1
pandas>=2.2
pyarrow>=15
```

### 2. 데이터 sub-repo (선택)

큰 데이터는 별도 repo `closingbell-data` 에 넣고 git submodule 로 연결하거나, 빌드 시 다운로드.

가장 단순한 방법: `data/closingbell/backtests/one_year_non_ai_*/`,
`data/closingbell/shared/watchlists/`, `data/market/global/global_merged.csv`,
`data/market/universe/stock_mapping.csv` 만 commit.

### 3. Streamlit Cloud 연결

1. GitHub에 push
2. https://share.streamlit.io → New app → repo 선택
3. **Main file path**: `app.py`
4. **Python version**: 3.11 (또는 3.12)
5. **Secrets** (옵션 — 데이터 루트가 다른 경우):

```toml
bell_data_root = "/mount/src/your-repo"
```

### 4. 환경변수 / secrets

이 앱은 다음 우선순위로 데이터 루트를 결정:
1. `BELL_DATA_ROOT` 환경변수
2. `st.secrets["bell_data_root"]`
3. 기본값 `C:\Coding`

Streamlit Cloud에서는 secrets 에 다음 추가:

```toml
bell_data_root = "/mount/src/<github-repo-name>"
```

### 5. 분봉/일봉 데이터 누락 시 동작

- `load_daily()`, `load_minute()` 모두 파일 없으면 빈 DataFrame 반환
- 차트는 "parquet 파일이 없습니다" 안내만 표시 — **앱이 죽지 않음**
- 통계/메모/홈은 정상 동작

## 옵션 B 상세 (S3 사용 예시)

`requirements.txt` 추가:
```
s3fs
```

[app.py:240](app.py) 의 `load_daily()`/`load_minute()`/`load_inst_trade()` 등에서 `pd.read_parquet(path)` 호출이 path가 `s3://...` URI 면 자동으로 s3fs 사용. `Path()` 객체 대신 문자열 URI를 전달.

수정 예시 (app.py에 추가):

```python
def _read_parquet_anywhere(path):
    """S3/GCS/로컬 자동 분기."""
    text = str(path)
    if text.startswith(("s3://", "gs://", "https://")):
        return pd.read_parquet(text)
    if not Path(text).exists():
        return pd.DataFrame()
    return pd.read_parquet(text)
```

그리고 모든 `pd.read_parquet(path)` 호출을 `_read_parquet_anywhere(path)` 로 교체.

S3 credentials 는 `st.secrets`:
```toml
[s3]
aws_access_key_id = "AKIA..."
aws_secret_access_key = "..."
```

## 보안 / 비용

| 항목 | 옵션 A (Cloud + GitHub) | 옵션 B (S3) | 옵션 C (Tunnel) |
|---|---|---|---|
| 비용 | 무료 | $1~5/월 | 무료 |
| 분봉 차트 | ❌ | ✅ | ✅ |
| 24/7 | ✅ | ✅ | ❌ (PC 켜야) |
| 데이터 노출 | GitHub public이면 위험 | private bucket OK | tunnel URL만 |
| 세팅 시간 | 30분 | 2~3시간 | 10분 |

**권장 진행**: Cloudflare Tunnel 먼저 → 운영 안정되면 S3로 마이그레이션.
