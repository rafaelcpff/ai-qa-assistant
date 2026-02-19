# TestRail Integration Setup Guide

This guide covers the complete setup process for TestRail integration with the AI QA Assistant application, including API access configuration, user permissions, and troubleshooting.

## Prerequisites

Before setting up TestRail integration, ensure you have:

- Access to a TestRail instance (cloud or on-premises)
- TestRail user account with appropriate permissions
- Network access to your TestRail instance
- Understanding of TestRail project structure

## Quick Setup Overview

1. **Create Testrail API Token**
2. **Configure Environment Variables**

## Detailed Setup Steps

### Step 1: Create TestRail API Token

1. **Navigate to your TestRail instance:**
   - Cloud: `https://company.testrail.io`

2. **Sign in with your credentials:**
   - Username (usually email address)
   - Password

3. **Create New API Token:**
   - Click on your user on top right and then on **My Settings**
   - Select **API Keys** on the left sidebar
   - Click on **Add Key**
   - Enter a label (e.g., "AI QA Assistant")
   - Click on **Generate Key**

4. **Copy the Token**:
   - **Important:** Copy the token immediately
   - It will look like: `ofa7h58lue0Q0.yrwGin-sadas` 
   - Store it securely - you won't see it again

### Step 2: Configure Environment Variables

1. **Set TestRail URL** in your `.env` file:
   ```bash
   TESTRAIL_URL=https://company.testrail.io
   ```

2. **Set TestRail username:**
   ```bash
   TESTRAIL_USERNAME=john.doe@company.com
   ```

3. **Set TestRail API key:**
   ```bash
   TESTRAIL_PASSWORD=your_api_key
   ```
