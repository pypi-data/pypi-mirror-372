# ML expert Platform SDK

Python ML expert Platform CLI 제품군을 구현하기 위한 공통 SDK 를 제공합니다.

## 사용 방법

### API Key 설정

ML expert Platform SDK를 사용하기 전에 API Key를 설정해야 합니다. 다음 3가지 방법 중 하나를 선택하세요:

#### 1. 환경변수로 설정
```bash
export MLX_APIKEY="your-api-key"
export MLX_ENDPOINT_URL="https://your-api-server.com"
```

#### 2. CLI 명령어로 설정
```bash
mlx configure
```

#### 3. 코드에서 직접 설정
```python
from mlx.sdk.core.config import ConfigFile

config = ConfigFile()
config.apikey = "your-api-key"
config.endpoint_url = "https://your-api-server.com"
```

### 기본 사용법

```python
from mlx.sdk.core.base import api_client, BaseMLXWebappAPI

# Method 1: API key를 직접 전달
client = api_client(
    mlx_webapp_endpoint="https://your-api-server.com",
    api_key="your-api-key",
    api_cls=BaseMLXWebappAPI
)

# Method 2: 환경변수나 config에서 자동 로드
client = api_client(
    mlx_webapp_endpoint="https://your-api-server.com",
    api_cls=BaseMLXWebappAPI
)
```

## 개발 환경 구성

### 1. uv 설치

[설치 가이드](https://docs.astral.sh/uv/getting-started/installation/) 참고.

pip 를 통해서도 설치 가능합니다.

```bash
pip install uv
```

### 2. build

```bash
make lock
make build
```

### 3. 단위 테스트 실행

```bash
make test
```
