# Push to GitHub and Deploy on Render

## Step 1: Create a new repository on GitHub

1. Go to [github.com/new](https://github.com/new) (or click **+** → **New repository**).
2. **Repository name:** `incident-knowledge-assistant` (or any name you prefer).
3. **Visibility:** Public.
4. **Do not** check "Add a README", "Add .gitignore", or "Choose a license" (this project already has them).
5. Click **Create repository**.

## Step 2: Push your code from your PC

Open PowerShell (or Git Bash) in the project folder and run (replace `YOUR_REPO_NAME` if you used a different name):

```powershell
cd c:\Users\ahame\incident-knowledge-assistant

git remote add origin https://github.com/kathijaafroseofficial/incident-knowledge-assistant.git
git push -u origin main
```

If you used a different repo name:

```powershell
git remote add origin https://github.com/kathijaafroseofficial/YOUR_REPO_NAME.git
git push -u origin main
```

When prompted, sign in to GitHub (browser or token). After this, your code will be on GitHub on the `main` branch.

## Step 3: Connect GitHub to Render and deploy the API

1. In Render, on the **Configure** step where it says "No repositories found", click ****GitHub**** (the big GitHub button).
2. Authorize Render to access your GitHub account (grant access to repos).
3. After connecting, you should see your repositories. Select **incident-knowledge-assistant** (or the name you used).
4. Render will show **Configure and deploy**:
   - **Branch:** `main`
   - **Root directory:** (leave blank)
   - **Runtime:** Python
   - **Build command:** `pip install -r requirements-api.txt`
   - **Start command:** `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
5. Click **Advanced** (or scroll) and add **Environment Variables**:
   - `API_BEARER_TOKEN` = (generate a random string, e.g. use [randomkeygen.com](https://randomkeygen.com) or `openssl rand -hex 24`)
   - `BOT_PROVIDER` = `openai_compatible`
   - `OPENAI_COMPATIBLE_URL` = `https://api.groq.com/openai/v1`
   - `OPENAI_COMPATIBLE_API_KEY` = (your Groq API key from [console.groq.com](https://console.groq.com); mark as **Secret**)
6. Click **Create Web Service**. Render will build and deploy; your API will be at `https://<your-service-name>.onrender.com`.
7. Test: open `https://<your-service-name>.onrender.com/docs` and call `POST /chat` with your `API_BEARER_TOKEN` in the header.

Done. Your POST API is now publicly deployed.
