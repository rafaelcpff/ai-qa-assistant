# AI QA Assistant PoC

An AI-powered Quality Assurance assistant that helps with some testing tasks.

## Features

- **User Story Review**: Review user stories content
- **Test Analysis**: Analyse user stories from testing perspective
- **Test Design**: Generate comprehensive test cases from user stories
- **Test Automation**: Generate automation prompts for test cases
- **Bug Improvement**: Enhance bug reports with AI assistance
- **Model Evaluation**: Evaluate AI model performance
- **TestRail Integration**: Find similar existing test cases
- **Cache Management**: Intelligent caching system for improved performance

## Quick Start

### Prerequisites

1. Docker and Docker Compose installed
2. Required environment variables (see [ENV_SETUP.md](ENV_SETUP.md))

#### Checking Docker Installation

Before proceeding, verify that Docker and Docker Compose are installed:

   ```bash
   docker --version
   docker-compose --version
   ```

If any of the commands returns an error or "command not found", you will need to install Docker.

#### Installing Docker (if not installed)

**macOs**:
   ```bash
   brew install --cask docker
   ```

On `Kandji Self Service`, install `Docker Desktop`.

### Environment Setup

1. Copy `ENV_TEMPLATE.md` to `.env`:
   ```bash
   cp ENV_TEMPLATE.md .env
   ```

2. Configure your environment variables in `.env`:
   - Environment setup (see [ENV_SETUP.md](ENV_SETUP.md))
   - Google Gemini API key (see [GOOGLE_GEMINI_SETUP.md](GOOGLE_GEMINI_SETUP.md))
   - Jira credentials (see [JIRA_SETUP.md](JIRA_SETUP.md))
   - TestRail credentials (see [TESTRAIL_SETUP.md](/TESTRAIL_SETUP.md))

### Running the Application

```bash
# Build and start the application
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop the application
docker-compose down
```

### Accessing the Application

Once running, access the application at:
- **Local**: http://localhost:8501

## Development

### Building for Development
```bash
# Build with no cache (for development)
docker-compose build --no-cache

# Run with volume mount for live code changes
docker-compose up --build
```

### Viewing Logs
```bash
# View application logs
docker-compose logs -f streamlit_app

# View logs for specific service
docker logs ai_qa_assistant_app
```

### Common Issues

- **"Cannot hash argument 'self'" errors**: Fixed by adding leading underscores to cached method parameters
- **TestRail API compatibility**: Update to latest testrail-api package
- **Missing environment variables**: Check your .env file configuration

## Documentation

- `ENV_SETUP.md` - Environment setup instructions
- `GOOGLE_GEMINI_SETUP.md` - Google Gemini API setup
- `TESTRAIL_SETUP.md` - TestRail integration setup
- `ENV_TEMPLATE.md` - Environments file template
- `JIRA_SETUP.md` - Jira integration setup

## Troubleshooting

### Common Issues

1. **Port 8501 already in use**:
   ```bash
   # Change port in docker-compose.yml
   ports:
     - "8502:8501"  # Use port 8502 instead
   ```

2. **Environment variables not loading**:
   - Ensure `.env` file exists in the root directory
   - Check file permissions
   - Verify variable names match the template

3. **Container won't start**:
   ```bash
   # Check logs
   docker-compose logs streamlit_app
   
   # Rebuild without cache
   docker-compose build --no-cache
   ``` 