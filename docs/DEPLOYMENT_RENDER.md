# Deploying Signify on Render (Complete Guide)

This guide walks you through deploying **Signify** (both the FastAPI Python backend and the Vite React frontend) on [Render](https://render.com).

---

## Method 1: Instant 1-Click Deployment via Render Blueprint (Recommended)

Render Blueprints read the `render.yaml` file in the root of the repository to provision both services automatically with live environment linking.

### Step 1: Push Code to GitHub
Ensure all your files and `render.yaml` are committed and pushed to your GitHub repository:
```bash
git add .
git commit -m "chore(deploy): prepare render.yaml and dynamic api url"
git push origin master
```

### Step 2: Open Render Dashboard
1. Go to **[https://dashboard.render.com/](https://dashboard.render.com/)**.
2. Click the **"New +"** button in the top right.
3. Select **"Blueprint"**.

### Step 3: Connect Your Repository
1. Select your GitHub repository (`Signify`).
2. Render will automatically detect `render.yaml`.
3. Click **"Apply"**.

### Step 4: Configure Secrets
When prompted for environment variables:
- **`VERBX_API_KEY`**: Paste your authenticated VerbX API key from your IvishAI account.
- Render will automatically generate `JWT_SECRET` and link `VITE_API_URL` to your backend's live URL.

Render will now build and deploy both services!

---

## Method 2: Manual Setup on Render (Step-by-Step)

If you prefer to configure the services manually in the Render dashboard:

### Service 1: The FastAPI Backend (Web Service)
1. In the Render Dashboard, click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Configure the settings:
   - **Name:** `signify-api`
   - **Language:** `Python 3`
   - **Region:** `Oregon (US West)` or your preferred region
   - **Branch:** `master`
   - **Root Directory:** *(leave blank)*
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free`
4. Add **Environment Variables**:
   - `PYTHON_VERSION`: `3.11.7`
   - `ENVIRONMENT`: `production`
   - `PROVIDER_MODE`: `verbx`
   - `VERBX_API_KEY`: *(paste your private VerbX key)*
   - `VERBX_API_BASE_URL`: `https://api.verbxeco.com`
   - `CORS_ORIGINS`: `*`
   - `JWT_SECRET`: *(generate any random 32-character string)*
5. Click **Create Web Service**.
6. Once deployed, copy your backend URL (e.g. `https://signify-api.onrender.com`).

---

### Service 2: The Vite React Frontend (Static Site)
1. In the Render Dashboard, click **New +** -> **Static Site**.
2. Connect the same GitHub repository.
3. Configure the settings:
   - **Name:** `signify-frontend`
   - **Branch:** `master`
   - **Root Directory:** *(leave blank)*
   - **Build Command:** `npm --prefix frontend install && npm --prefix frontend run build`
   - **Publish Directory:** `frontend/dist`
4. Add **Environment Variables**:
   - `VITE_API_URL`: Paste your backend URL from Service 1 (e.g. `https://signify-api.onrender.com`).
5. Configure **Redirects / Rewrites** (under settings):
   - **Type:** `Rewrite`
   - **Source:** `/*`
   - **Destination:** `/index.html`
   *(This ensures refreshing on subpages won't result in a 404)*
6. Click **Create Static Site**.

---

## Verification Checklist After Deployment

Once both services show **"Live"**:
1. Open the frontend URL in your browser (e.g. `https://signify-frontend.onrender.com`).
2. Open DevTools (F12) -> Console.
3. Verify that requests go to `https://signify-api.onrender.com/api/v1/health` and return:
   ```json
   { "status": "healthy", "sign_language": "Indian Sign Language (ISL)", ... }
   ```
4. Test the **Consent Gate**, **Interactive Gesture Simulator**, and **Microphone Speech Recognition**.

