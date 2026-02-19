# Environment Setup Guide

This guide covers the complete environment setup for the AI QA Assistant application, including all required environment variables and their configuration.

## Prerequisites

Before setting up the environment, ensure you have:

- Docker and Docker Compose installed
- Access to your Jira instance
- Access to your TestRail instance
- Google Cloud account with Gemini API access
- Basic understanding of environment variables

## Quick Setup

1. **Copy the environment template:**
   ```bash
   cp ENV_TEMPLATE.md .env
   ```

2. **Edit the `.env` file** with your actual credentials and configuration

3. **Start the application:**
   ```bash
   docker-compose up --build
   ```

## Environment Variables Reference

### Google Gemini API Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `GOOGLE_MODEL` | Google Gemini model to use | No | `gemini-2.0-flash` | `gemini-2.0-flash` |
| `GOOGLE_API_KEY` | Your Google Cloud API key for Gemini | **Yes** | - | `AIzaSyC...` |

**Note:** This is the primary AI model used for all text generation and analysis tasks.

### Jira Integration

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `JIRA_BASE_URL` | Your Jira instance URL | **Yes** | - | `https://company.atlassian.net` |
| `JIRA_EMAIL` | Your Jira account email | **Yes** | - | `john.doe@company.com` |
| `JIRA_API_TOKEN` | Your Jira API token | **Yes** | - | `your_api_token_here` |
| `JIRA_PROJECT_KEY` | Jira project key for user stories and bugs | **Yes** | - | `CM` |

**Note:** The application currently supports a single Jira project key for both user stories and bug reports.

### TestRail Integration

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `TESTRAIL_URL` | Your TestRail instance URL | **Yes** | - | `https://company.testrail.io` |
| `TESTRAIL_USERNAME` | Your TestRail username | **Yes** | - | `john.doe@company.com` |
| `TESTRAIL_PASSWORD` | Your TestRail password or API key | **Yes** | - | `your_api_token_here` |

## Detailed Setup Instructions

### 1. Google Gemini API Setup

See [GOOGLE_GEMINI_SETUP.md](GOOGLE_GEMINI_SETUP.md) for detailed instructions on obtaining and configuring your Google API key.

### 2. Jira Setup

See [JIRA_SETUP.md](JIRA_SETUP.md) for detailed instructions on configuring Jira integration.

### 3. TestRail Setup

See [TESTRAIL_SETUP.md](TESTRAIL_SETUP.md) for detailed instructions on configuring TestRail integration.

### 4. Environment File Creation

1. **Create the `.env` file:**
   ```bash
   # Copy the template
   cp ENV_TEMPLATE.md .env
   
   # Edit the file with your credentials using your preferred editor (e.g. VSCode)
   ```

2. **Set required variables first:**

### 5. Environment File Security

**Important Security Notes:**

- **Never commit `.env` files** to version control
- **Use strong, unique passwords** for each service
- **Rotate API keys regularly** for production environments
- **Restrict file permissions** on the `.env` file:
  ```bash
  chmod 600 .env
  ```

### 6. Validation

After setting up your environment variables, validate the configuration:

1. **Start the application:**
   ```bash
   docker-compose up --build
   ```

2. **Check the application logs** for any configuration errors:
   ```bash
   docker-compose logs streamlit_app
   ```

3. **Access the application** at `http://localhost:8501` and verify:
   - Google Gemini API connection status
   - Jira connection status
   - TestRail connection status

## Troubleshooting

### Common Environment Issues

1. **"Environment variable not found" errors:**
   - Ensure `.env` file exists in the project root
   - Check variable names match exactly (case-sensitive)
   - Verify no extra spaces or quotes around values

2. **Docker environment loading issues:**
   - Ensure `.env` file is in the same directory as `docker-compose.yml`
   - Check file permissions
   - Restart Docker containers after environment changes

3. **API key validation errors:**
   - Verify API keys are correct and active
   - Check service account permissions
   - Ensure no extra characters or whitespace
   ```

For additional help, refer to the specific setup guides:
- [GOOGLE_GEMINI_SETUP.md](GOOGLE_GEMINI_SETUP.md)
- [JIRA_SETUP.md](JIRA_SETUP.md)
- [TESTRAIL_SETUP.md](TESTRAIL_SETUP.md)
