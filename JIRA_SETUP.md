# Jira Integration Setup Guide

This guide covers the complete setup process for Jira integration with the AI QA Assistant application, including API token creation, project access configuration, and troubleshooting.

## Prerequisites

Before setting up Jira integration, ensure you have:

- Access to a Jira instance (cloud or on-premises)
- Jira user account with appropriate permissions

## Quick Setup Overview

1. **Create Jira API Token**
2. **Set Environment Variables**

## Detailed Setup Steps

### Step 1: Create Jira API Token

#### For Jira Cloud

1. **Navigate to Atlassian Account Settings:**
   - Go to [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
   - Sign in with your Atlassian account

2. **Create New API Token:**
   - Click **"Create API token"**
   - Enter a label (e.g., "AI QA Assistant")
   - Click **"Create"**

3. **Copy the Token:**
   - **Important:** Copy the token immediately
   - It will look like: `ATATT3xFfGF0abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz`
   - Store it securely - you won't see it again

### Step 2: Configure Environment Variables

1. **Set Jira base URL** in your `.env` file:
   ```bash
   JIRA_BASE_URL=https://company.atlassian.net
   ```

2. **Set Jira email:**
   ```bash
   JIRA_EMAIL=john.doe@company.com
   ```

3. **Set Jira API token:**
   ```bash
   JIRA_API_TOKEN=your_api_token_here
   ```

4. **Set Jira project key:**
   ```bash
   JIRA_PROJECT_KEY=CM
   ```

#### Example Configuration

```bash
# Jira Configuration
JIRA_BASE_URL=https://company.atlassian.net
JIRA_EMAIL=john.doe@company.com
JIRA_API_TOKEN=ATATT3xFfGF0abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz
JIRA_PROJECT_KEY=CM
```
