# GitHub to Render Deployment Guide for Telegram AI Bot

This guide will walk you through the process of deploying your Telegram AI Bot from a GitHub repository to Render, a cloud platform that offers continuous deployment.

## 1. Prepare Your GitHub Repository

Ensure your project directory contains the following files:

*   `bot.py`: The main Python script for your Telegram bot.
*   `requirements.txt`: Lists all Python dependencies.
*   `Dockerfile`: Defines the Docker image for your bot.
*   `.env`: **(IMPORTANT: DO NOT upload this to GitHub)** Contains your sensitive API keys. This file should be ignored by Git.
*   `.gitignore`: Specifies files and directories that Git should ignore (e.g., `.env`, `__pycache__`).

**Steps to prepare your GitHub repository:**

1.  **Initialize a Git Repository**: If you haven't already, navigate to your bot's project directory in your terminal and initialize a Git repository:
    ```bash
    cd /home/ubuntu/telegram_ai_bot
    git init
    ```

2.  **Add `.gitignore`**: Make sure your `.gitignore` file is present and correctly configured to exclude `.env`.
    ```
    .env
    __pycache__/
    *.pyc
    ```

3.  **Add Files to Git**: Add all necessary project files to your Git repository:
    ```bash
    git add bot.py requirements.txt Dockerfile .gitignore
    ```

4.  **Commit Changes**: Commit your files to the repository:
    ```bash
    git commit -m "Initial commit of Telegram AI Bot"
    ```

5.  **Create a GitHub Repository**: Go to [GitHub](https://github.com/) and create a new public or private repository. Do NOT initialize it with a README, .gitignore, or license, as you already have these files locally.

6.  **Link Local to GitHub Repository**: Connect your local repository to the newly created GitHub repository and push your code:
    ```bash
    git remote add origin <your_github_repository_url>
    git branch -M main
    git push -u origin main
    ```
    *Replace `<your_github_repository_url>` with the URL of your GitHub repository.*

## 2. Deploy to Render

Render will automatically build and deploy your Dockerized application from your GitHub repository.

**Steps to deploy on Render:**

1.  **Sign Up/Log In to Render**: Go to [Render.com](https://render.com/) and sign up for a new account or log in.

2.  **Connect GitHub**: In your Render dashboard, navigate to 
"New" -> "Blueprint" or "Web Service" (depending on Render's latest UI/workflow). For a bot that runs continuously, a "Background Worker" is usually the most appropriate choice.

3.  **Select Your Repository**: Choose the GitHub repository where you pushed your bot's code.

4.  **Configure Your Service**:
    *   **Name**: Give your service a descriptive name (e.g., `telegram-ai-bot`).
    *   **Region**: Select a region geographically close to your users for lower latency.
    *   **Branch**: Specify the branch you want to deploy from (e.g., `main`).
    *   **Root Directory**: If your `Dockerfile` and `bot.py` are in the root of your repository, leave this blank. Otherwise, specify the subdirectory.
    *   **Runtime**: Select `Docker` since we are using a `Dockerfile`.
    *   **Build Command**: Render will automatically detect the `Dockerfile` and use it. You might not need to specify a build command explicitly if your `Dockerfile` handles everything.
    *   **Start Command**: `python bot.py` (This command will be executed inside the Docker container).
    *   **Environment Variables**: This is crucial for your API keys. Add the following environment variables:
        *   `TELEGRAM_BOT_TOKEN`: Your Telegram Bot Token (e.g., `8709954952:AAFInuL5I35ZBK2_vvPPlPOH9kXUj0bN3Wg`)
        *   `OPENROUTER_API_KEY`: Your OpenRouter API Key (e.g., `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`)
        
        **Important**: These values should be entered directly into Render's environment variable settings, NOT committed to your GitHub repository.

5.  **Create Background Worker**: Click the "Create Background Worker" button. Render will then pull your code from GitHub, build the Docker image, and deploy your bot.

6.  **Monitor Deployment**: You can view the deployment logs in the Render dashboard to ensure your bot starts successfully. If there are any errors, the logs will help you diagnose them.

## 3. Post-Deployment Steps

1.  **Verify Bot Functionality**: Send a `/start` command to your bot on Telegram to ensure it's responding.
2.  **Add to Group and Grant Admin Permissions**: If you plan to use the bot in a group, add it to the group and grant it the necessary admin permissions (delete messages, ban users) as described in the initial `README.md`.

By following these steps, your Telegram AI bot will be running continuously on Render, powered by your GitHub repository.
