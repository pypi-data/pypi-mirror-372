# CurrentTime MCP Server

IP 기반 타임존 감지를 통해 정확한 현재 시간을 제공하는 MCP(Model Context Protocol) 서버입니다.

## 기능

- **자동 타임존 감지**: 클라이언트의 IP 주소를 기반으로 자동으로 타임존을 감지합니다
- **정확한 시간 제공**: pytz 라이브러리를 사용하여 정확한 현재 시간을 계산합니다
- **다양한 타임존 지원**: 전 세계 597개의 타임존을 지원합니다
- **클라이언트 정보**: IP 기반 위치 정보와 타임존 정보를 제공합니다

## 제공되는 Tools

### 1. `get_current_time`
클라이언트의 IP를 기반으로 타임존을 자동 감지하고 현재 시간을 반환합니다.

**매개변수:**
- `client_ip` (선택사항): 특정 IP 주소를 지정할 수 있습니다.

**반환값:**
- `current_time`: ISO 형식의 현재 시간
- `timezone`: 감지된 타임존 (예: "Asia/Seoul")
- `formatted_time`: 읽기 쉬운 형식의 시간 (예: "2025-08-27 21:55:40 KST")
- `location`: 도시, 지역, 국가 정보
- `utc_offset`: UTC 오프셋
- `is_dst`: 일광절약시간 적용 여부

### 2. `get_time_for_timezone`
특정 타임존의 현재 시간을 반환합니다.

**매개변수:**
- `timezone_name`: 타임존 이름 (예: "America/New_York", "Europe/London")

### 3. `get_client_info`
클라이언트의 IP 기반 위치 정보와 타임존을 반환합니다.

**매개변수:**
- `client_ip` (선택사항): 특정 IP 주소를 지정할 수 있습니다.

### 4. `list_common_timezones`
지역별로 정리된 일반적인 타임존 목록을 반환합니다.

## 빠른 설치

Claude Code 또는 다른 MCP 클라이언트에서 한 줄로 설치할 수 있습니다:

```bash
claude mcp add currenttime-mcp
```

## 수동 설치

### 1. PyPI에서 설치

```bash
# uvx로 즉시 실행 (설치 없이 권장)
uvx currenttime-mcp

# 또는 uv로 시스템 설치
uv tool install currenttime-mcp

# 또는 pip 사용
pip install currenttime-mcp
```

### 2. Claude Code 설정

Claude Code에서 `config.toml` 파일에 다음과 같이 추가하세요:

```toml
[mcp_servers.currenttime]
command = "uvx"
args = ["currenttime-mcp"]

# 또는 pip으로 설치한 경우
[mcp_servers.currenttime]  
command = "currenttime-mcp"
```

### 3. 테스트

```bash
# 함수 테스트
source venv/bin/activate
python test_server.py
```

## 사용 예시

Claude Code에서 다음과 같이 사용할 수 있습니다:

- "현재 시간이 몇 시야?" 
- "뉴욕의 현재 시간을 알려줘"
- "내 타임존 정보를 보여줘"
- "사용 가능한 타임존 목록을 보여줘"

## API 정보

이 MCP 서버는 다음 외부 서비스를 사용합니다:
- **ipapi.co**: IP 기반 지리적 위치 및 타임존 감지 (월 30,000회 무료)

환경변수로 설정을 조정할 수 있습니다:
- `IPAPI_BASE`: 기본 API 엔드포인트(기본값: `https://ipapi.co`)
- `IPAPI_KEY`: ipapi 유료/개인 키(있을 경우 쿼터 증가)

## 기술 스택

- **Python 3.8+**
- **MCP (Model Context Protocol)**: AI 모델과의 표준화된 통신
- **FastMCP**: MCP 서버 구현을 위한 고수준 프레임워크
- **requests**: HTTP 클라이언트
- **pytz**: 타임존 처리

## 라이센스

이 프로젝트는 MIT 라이센스 하에 있습니다.
