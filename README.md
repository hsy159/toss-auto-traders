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

## 실행

```bash
toss-trader auth-token
toss-trader accounts
toss-trader holdings
toss-trader dry-run --symbol A005930 --prices 70000 70500 71000 72000 73000
```

## 구조

- `src/toss_auto_traders/api`: 인증, HTTP 요청, 계좌/시세/주문 API 래퍼
- `src/toss_auto_traders/strategy`: 주문 신호 생성
- `src/toss_auto_traders/engine`: 리스크 체크와 실행 흐름

토스증권 문서의 정확한 endpoint path가 변경되거나 확인되면 `src/toss_auto_traders/api/endpoints.py`만 우선 수정하면 됩니다.
