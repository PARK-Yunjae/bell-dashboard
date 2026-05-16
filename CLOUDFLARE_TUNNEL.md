# 외부에서 대시보드 보기 — Cloudflare Tunnel 가이드

`bell-dashboard` Streamlit 앱을 외부(휴대폰·다른 PC·외부 네트워크)에서 안전하게 접속하는 가장 빠른 방법.

## 왜 Cloudflare Tunnel?

- ✅ **무료** (도메인 없어도 임시 URL 발급, 도메인 있으면 영구 URL)
- ✅ **포트 포워딩 / 공유기 설정 불필요** — 아웃바운드 연결만 사용
- ✅ **HTTPS 자동** + DDoS 보호
- ✅ 본인 PC에서 streamlit이 돌고 있는 동안만 외부 접속 가능 (PC 끄면 자동 차단)
- ⚠️ 본인 PC가 켜져 있어야 함. 24/7 필요하면 별도 VM 검토.

## 1단계: cloudflared 설치 (Windows)

PowerShell에서:

```powershell
winget install --id Cloudflare.cloudflared
# 또는 https://github.com/cloudflare/cloudflared/releases 에서 cloudflared-windows-amd64.exe 다운로드 → PATH 등록
```

확인:

```powershell
cloudflared --version
```

## 2단계: Streamlit 실행

별도 PowerShell 창에서:

```powershell
cd C:\Coding\projects\bell-dashboard
.\scripts\run_dashboard.ps1
```

`http://127.0.0.1:8501` 에서 로컬 동작 확인.

## 3단계: Tunnel 띄우기 (임시 URL — 가장 빠름)

또 다른 PowerShell 창:

```powershell
cloudflared tunnel --url http://127.0.0.1:8501
```

콘솔에 다음 같은 줄이 나옴:

```
Your quick Tunnel has been created! Visit it at:
https://random-words-1234.trycloudflare.com
```

이 URL을 휴대폰·태블릿 어디서든 열면 대시보드 표시. 매번 다른 URL 발급되고, 명령어 종료 시 자동 만료.

## 4단계 (선택): 영구 URL — 도메인 보유 시

도메인이 Cloudflare에 등록되어 있다면:

```powershell
cloudflared tunnel login                                # 브라우저 인증
cloudflared tunnel create closingbell-dashboard          # 터널 생성
cloudflared tunnel route dns closingbell-dashboard dashboard.example.com
```

`%USERPROFILE%\.cloudflared\config.yml`:

```yaml
tunnel: closingbell-dashboard
credentials-file: C:\Users\<USER>\.cloudflared\<UUID>.json

ingress:
  - hostname: dashboard.example.com
    service: http://127.0.0.1:8501
  - service: http_status:404
```

실행:

```powershell
cloudflared tunnel run closingbell-dashboard
```

→ `https://dashboard.example.com` 영구 접속.

## 5단계 (선택): 자동 시작 — Windows 서비스

```powershell
cloudflared service install
```

부팅 시 자동 시작. Streamlit도 작업 스케줄러로 등록하면 PC 켜두기만 하면 항상 외부 접속 가능.

## 보안 주의

- **데이터 무단 노출 위험**: tunnel URL을 알면 누구나 접속 가능. 임시 URL은 추측이 거의 불가능하지만, 영구 도메인 사용 시 [Cloudflare Access](https://developers.cloudflare.com/cloudflare-one/applications/) 로 이메일 OTP 인증 추가 권장
- **메모 입력 가능**: 1년치 복기 탭의 메모 저장이 외부에서도 가능. 본인만 접속하는 게 맞음
- **민감 데이터**: 종목 코드·수급·실거래 정보가 노출됨. 공개 SNS에 URL 공유 금지

## 트러블슈팅

| 증상 | 원인 / 해결 |
|---|---|
| `Connection refused` | streamlit이 안 떠 있음 → 2단계 다시 실행 |
| 외부 URL은 열리는데 차트가 안 보임 | streamlit이 `--server.address localhost`로 떴는지 확인. `127.0.0.1` 사용 필요 |
| 한국어가 깨짐 | 브라우저 인코딩 자동, 거의 발생 안 함. HTML `<meta charset="utf-8">`은 streamlit이 자동 추가 |
| 분봉 차트가 느림 | 본인 PC 디스크 → tunnel → 외부 네트워크 경로. 첫 로드 후 streamlit 캐시로 빨라짐 |
| Plotly 인터랙션이 끊김 | 무료 임시 URL은 트래픽 제한 있을 수 있음. 영구 도메인 권장 |

## 다른 옵션과 비교

| 옵션 | 비용 | 세팅 시간 | 데이터 동기화 | 24/7 |
|---|---|---|---|---|
| **Cloudflare Tunnel (이 가이드)** | 무료 | 10분 | 불필요 (PC 데이터 그대로) | ❌ PC 켜야 함 |
| Streamlit Community Cloud | 무료 | 30분 | GitHub repo 필요, 분봉 parquet 못 올림 | ✅ |
| 클라우드 VM + S3 | 월 $5~10 | 2시간 | S3 업로드 자동화 필요 | ✅ |
| ngrok | 무료/유료 | 5분 | 불필요 | ❌ PC 켜야 함 |

ngrok은 무료 한도가 작고 URL이 자주 바뀜. Cloudflare Tunnel이 모든 면에서 우수.
