# AI Slackbot HR Assistant with OpenAI Assistant API

Build an interactive Slackbot HR Assistant using the OpenAI Assistant API, Python, and Flask. This guide will show you how to create a Slackbot that leverages OpenAI's powerful AI capabilities for generating responses and Airtable for data storage.

## Prerequisites

- **OpenAI Account**: Sign up for an account at [OpenAI](https://platform.openai.com/) if you don't have one. 
you should have knowledge of Assitant API how it works.
- **Slack App**: Create a Slack app at [Slack API](https://api.slack.com/).
- **Digital Ocean**: We'll use Digital Ocean for deployment.
- **Python Knowledge**: Basic understanding of Python programming.

## Getting Started

### Step 1: Create a Slack App

1. Visit [Slack API](https://api.slack.com/).
2. Create a new App with an App Manifest.
3. Configure your App Manifest as shown below:

    ```json
    {
        "display_information": {
            "name": "HR Assistant"
        },
        "features": {
            "bot_user": {
                "display_name": "HR Assistant",
                "always_online": true
            }
        },
        "oauth_config": {
            "scopes": {
                "bot": [
                    "app_mentions:read",
                    "chat:write",
                    "im:history",
                    "users:read"
                ]
            }
        },
        "settings": {
            "event_subscriptions": {
                "request_url": "https://url-to-server",
                "bot_events": [
                    "app_mention",
                    "message.im"
                ]
            },
            "org_deploy_enabled": false,
            "socket_mode_enabled": false,
            "token_rotation_enabled": false
        }
    }
    ```

### Step 2: Set Up the Project

1. **Establish a Virtual Environment**: Initialize a dedicated virtual environment for your project to efficiently manage package dependencies.
   - **Creation and Activation**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - **Install Dependencies**: Load necessary packages using the provided requirements file.
     ```bash
     pip install -r requirements.txt
     ```

2. **Setting Up Environment Variables**:
   - **.env File Creation**: Forge a `.env` file in the root of your project directory.
   - **Environment Configuration**: Populate the `.env` file with these keys, substituting in your specific credentials:
     ```plaintext
     OPENAI_API_KEY='<your_openai_api_key>'
     SLACK_BOT_TOKEN='<your_slack_bot_token>'
     SLACK_SIGNING_SECRET='<your_slack_signing_secret>'
     AIRTABLE_API_KEY='<your_airtable_api_key>'
     HR_CHANNEL_ID='<your_hr_channel_id>'
     ```

3. **Integrate Slack and OpenAI**:
   - **Acquire OpenAI API Key**: Secure your OpenAI API key for integration.
   - **Configure Project Settings**: Input your `SLACK_BOT_TOKEN` and `SLACK_SIGNING_SECRET` into the project's configuration.

4. **Airtable Integration Setup**:
   - **Create Airtable Base**: Develop a new table in Airtable via the [MY BASE link](https://airtable.com/appfLiSESj9pN2UXC/shryqafmJfQlCPUqF).
   - **Generate API Token**: Obtain an API token for Airtable.
   - **Update Project with Airtable Details**: Incorporate the Airtable API URL into your project setup.

5. **Configure Ngrok**: Set up Ngrok to enable secure tunnelling for local development.


### Step 3: Deployment

Deploy the application to the Digital Ocean App

### Step 4: Integrate with Slack
1. In your Slack App's settings, go to 'Event Subscriptions'.
2. Enter the URL of your deployed application to integrate it with Slack.
