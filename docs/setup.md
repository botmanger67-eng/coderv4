# Setup Instructions

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for version control)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root directory:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration values:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# GitHub Configuration
GITHUB_TOKEN=your_github_token_here

# Database Configuration
DATABASE_PATH=data/bot_database.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
```

### 5. Database Setup

The database will be automatically created on first run. However, you can manually initialize it:

```bash
python scripts/init_database.py
```

### 6. Run the Application

```bash
python main.py
```

## Configuration Details

### Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to create a new bot
4. Copy the API token and add it to your `.env` file

### OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

### GitHub Token

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Click "Generate new token" (classic)
3. Select appropriate scopes (at minimum: `repo`, `user`)
4. Generate the token and copy it to your `.env` file

## Project Structure

```
project/
├── src/
│   ├── __init__.py
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── handlers.py
│   │   └── commands.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── openai_service.py
│   │   └── github_service.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── repository.py
│   └── utils/
│       ├── __init__.py
│       └── logger.py
├── tests/
│   ├── __init__.py
│   ├── test_bot.py
│   ├── test_services.py
│   └── test_database.py
├── data/
│   └── .gitkeep
├── logs/
│   └── .gitkeep
├── scripts/
│   └── init_database.py
├── .env.example
├── .gitignore
├── requirements.txt
├── main.py
└── README.md
```

## Running Tests

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_bot.py

# Run tests with coverage report
pytest --cov=src tests/
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Ensure you've activated the virtual environment and installed dependencies.

2. **Database Permission Error**: Check that the `data/` directory exists and has write permissions.

3. **API Authentication Errors**: Verify your API keys and tokens in the `.env` file.

4. **Port Already in Use**: If running locally, ensure no other application is using the required port.

### Logging

Logs are stored in the `logs/` directory. Check `bot.log` for detailed error information.

## Development

### Code Style

This project follows PEP 8 guidelines. Use the following tools for code quality:

```bash
# Format code
black .

# Check style
flake8

# Type checking
mypy .
```

### Pre-commit Hooks

Install pre-commit hooks to automatically check code quality:

```bash
pip install pre-commit
pre-commit install
```

## Deployment

For production deployment, consider:

1. Using a process manager like `supervisor` or `systemd`
2. Setting up proper logging rotation
3. Using environment variables instead of `.env` file
4. Implementing rate limiting
5. Setting up monitoring and alerting

## Support

For additional help, refer to:
- [python-telegram-bot Documentation](https://python-telegram-bot.org/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [PyGithub Documentation](https://pygithub.readthedocs.io/)