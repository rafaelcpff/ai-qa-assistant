# Environment Variables Template

Copy this file to `.env` and fill in your actual values. Remove the `#` comments and replace the placeholder values with your real credentials.

## Core Application Settings
# Google Gemini model to use (default: gemini-2.0-flash)
GOOGLE_MODEL=gemini-2.0-flash

## Google Gemini API Configuration
# Your Google Cloud API key for Gemini (REQUIRED)
# Get this from: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=your_google_api_key_here

## Jira Integration Configuration
# Your Jira instance URL (REQUIRED)
# Example: https://your_company.atlassian.net
JIRA_BASE_URL=https://company.atlassian.net

# Your Jira account email (REQUIRED)
# Example: john.doe@company.com
JIRA_EMAIL=your.email@company.com

# Your Jira API token (REQUIRED)
# Get this from: https://id.atlassian.com/manage-profile/security/api-tokens
JIRA_API_TOKEN=your_jira_api_token_here

# Jira project key for user stories and bugs (REQUIRED)
# Example: CM, PROJ, TEST
JIRA_PROJECT_KEY=CM

## TestRail Integration Configuration
# Your TestRail instance URL (REQUIRED)
# Example: https://yourcompany.testrail.io
TESTRAIL_URL=https://company.testrail.io

# Your TestRail username (REQUIRED)
# Example: rafael.fernandes@company.com
TESTRAIL_USERNAME=your_testrail_username

# Your TestRail API key (REQUIRED)
# Get this from: https://company.testrail.io/index.php?/mysettings
TESTRAIL_PASSWORD=your_testrail_api_token_here

## Example Configuration (Uncomment and modify as needed)

# # Google Gemini API
# GOOGLE_API_KEY=key
# GOOGLE_MODEL=gemini-2.0-flash

# # Jira Configuration
# JIRA_BASE_URL=https://company.atlassian.net
# JIRA_EMAIL=john.doe@company.com
# JIRA_API_TOKEN=token
# JIRA_PROJECT_KEY=CM

# # TestRail Configuration
# TESTRAIL_URL=https://company.testrail.io
# TESTRAIL_USERNAME=john.doe@company.com
# TESTRAIL_PASSWORD=password