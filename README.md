# Toss Auto Traders

토스증권 Open API 기반 자동매매 골격입니다. 기본값은 실주문을 막는 `DRY_RUN=true`입니다.

## 준비

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

`.env`에 토스증권 API Key, Secret Key, 계좌 식별자를 입력하세요. 키를 채팅, Git, 로그에 남기지 마세요.
처음에는 계좌 식별자를 몰라도 됩니다. `toss-trader accounts`로 조회한 뒤 `TOSSINVEST_ACCOUNT`를 채우세요.

토스증권 서버가 `IP address not allowed`를 반환하면 코드 문제가 아니라 API Key의 허용 IP 설정 문제입니다. `toss-trader check-ip`로 나온 IP를 토스증권 WTS > 설정 > Open API에서 **지금 `.env`에 넣은 client_id와 같은 키**에 등록하세요. 브라우저에서 본 IP와 터미널에서 나가는 IP가 다를 수 있습니다.

## 실행

```bash
toss-trader check-ip
toss-trader auth-token
toss-trader accounts
toss-trader holdings
toss-trader dry-run --symbol A005930 --prices 70000 70500 71000 72000 73000
toss-trader web
```

웹 대시보드는 로컬에서만 열립니다.

```bash
toss-trader web
# 브라우저에서 http://127.0.0.1:8765
```

- **대시보드**: 국내/해외/전체 탭으로 보유종목 조회
- **API 테스트**: 각 API를 버튼으로 호출해 응답 확인

## 구조

- `src/toss_auto_traders/api`: 인증, HTTP 요청, 계좌/시세/주문 API 래퍼
- `src/toss_auto_traders/strategy`: 주문 신호 생성
- `src/toss_auto_traders/engine`: 리스크 체크와 실행 흐름
- `src/toss_auto_traders/web`: 로컬 대시보드

토스증권 문서의 정확한 endpoint path가 변경되거나 확인되면 `src/toss_auto_traders/api/endpoints.py`만 우선 수정하면 됩니다.
