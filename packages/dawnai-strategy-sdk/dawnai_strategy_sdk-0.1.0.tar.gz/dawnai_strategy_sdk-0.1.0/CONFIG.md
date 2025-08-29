# SDK Configuration Guide

The DawnAI SDK supports multiple ways to configure your connection and context settings. Configuration values are loaded in priority order, with environment variables taking the highest priority.

## Configuration Options

| Setting | Environment Variable | Description | Default |
|---------|---------------------|-------------|---------|
| `base_url` | `DAWNAI_BASE_URL` | API server URL | `http://localhost:3000` |
| `api_key` | `DAWNAI_API_KEY` | API authentication key | `None` |
| `user_id` | `DAWNAI_USER_ID` | User identifier | `sdk-user` |
| `strategy_id` | `DAWNAI_STRATEGY_ID` | Strategy identifier | `None` |
| `agent_session_id` | `DAWNAI_SESSION_ID` | Agent session ID | `None` |
| `is_paper` | `DAWNAI_IS_PAPER` | Paper trading mode | `true` |

## Configuration Methods

### 1. Environment Variables (Highest Priority)

Set environment variables in your shell or `.bashrc`/`.zshrc`:

```bash
export DAWNAI_USER_ID='your-user-id'
export DAWNAI_STRATEGY_ID='strategy-123'
export DAWNAI_SESSION_ID='session-456'
export DAWNAI_IS_PAPER=false
export DAWNAI_BASE_URL='https://api.example.com'
export DAWNAI_API_KEY='your-api-key'
```

### 2. Configuration File

Create a `.dawnai` file in your project directory or home directory:

```json
{
  "base_url": "http://localhost:3000",
  "user_id": "my-user-id",
  "strategy_id": "my-strategy-123",
  "agent_session_id": "session-456",
  "is_paper": true,
  "api_key": "optional-api-key"
}
```

The SDK looks for config files in this order:
1. `./.dawnai` (current directory)
2. `~/.dawnai` (home directory)

### 3. Programmatic Configuration

Configure in your Python code:

```python
from dawnai.strategy.functions import configure

# Configure with specific values
configure(
    base_url="http://localhost:3000",
    api_key="your-api-key"
)

# The configure function will merge with existing config
# from environment variables and config files
```

### 4. Interactive Configuration

Create a config file interactively:

```bash
python -m dawnai.config create
```

## Priority Order

Configuration is loaded in this priority order (highest to lowest):

1. **Environment variables** (`DAWNAI_*`)
2. **Config file in current directory** (`./.dawnai`)
3. **Config file in home directory** (`~/.dawnai`)
4. **Default values**

## Usage Example

```python
from dawnai.strategy import Strategy
from dawnai.strategy.triggers import cron
from dawnai.strategy.functions import polymarket_smart_search

# No need to call configure() if using env vars or config files
# The SDK will automatically load configuration

class MyStrategy(Strategy):
    @cron(interval="5m")
    def check_markets(self):
        # This will use the configured context automatically
        markets = polymarket_smart_search("trending", limit=5)
        return markets

# The API calls will include the context from your configuration:
# {
#   "userId": "your-user-id",
#   "strategyId": "your-strategy-id", 
#   "agentSessionId": "your-session-id",
#   "isPaper": false
# }
```

## Checking Current Configuration

View your current configuration:

```bash
python -m dawnai.config
```

Or in Python:

```python
from dawnai.config import get_config

config = get_config()
print(config)
```

## Security Notes

- Never commit `.dawnai` files containing API keys to version control
- Add `.dawnai` to your `.gitignore` file
- Use environment variables for sensitive values in production
- The example file `.dawnai.example` can be committed as a template