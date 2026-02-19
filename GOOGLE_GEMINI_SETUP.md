# Google Gemini API Setup Guide

This guide covers the complete setup process for Google Gemini API access, which is required for the AI QA Assistant application to function.

## Prerequisites

Before setting up Google Gemini API access, ensure you have:

- A Google account (Gmail, Google Workspace, or personal)
- Access to Google Cloud Console

## Quick Setup Overview

1. **Access Google AI Studio (MakerSuite)**
2. **Generate API Key**
3. **Configure Environment Variables**

## Detailed Setup Steps

### Step 1: Access Google AI Studio

1. **Navigate to Google AI Studio:**
   - Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account if prompted

### Step 2: Generate API Key

1. **In Google AI Studio:**
   - Click on **"Get API key"** button
   - If you have existing projects, you may see a dropdown to select one
   - If no projects exist, a new one will be created automatically

2. **API Key Creation:**
   - The system will generate a new API key
   - **Important:** Copy this key immediately as it won't be shown again
   - The key will look like: `AIzaSyC1234567890abcdefghijklmnopqrstuvwxyz`

3. **Project Setup (if needed):**
   - If this is your first time, you may be prompted to:
     - Accept terms of service
     - Configure project settings

### Step 3: Configure Environment Variables

1. **Copy the API key** to your `.env` file:
   ```bash
   GOOGLE_API_KEY=AIzaSyC1234567890abcdefghijklmnopqrstuvwxyz
   ```

2. **Optional: Set custom model** (defaults to `gemini-2.0-flash`):
   ```bash
   GOOGLE_MODEL=gemini-2.0-flash
   ```

3. **Save the `.env` file** 
