# Deployment Guide: Local Backend + Vercel Frontend

This guide outlines the "Hybrid Edge" deployment strategy for the **Describe My Environment** project.

- **Frontend**: Hosted on Vercel (Free, Global CDN).
- **Backend**: Hosted locally on your Mac M4 (Edge Server) and exposed via a secure tunnel.

---

## Part 1: Prerequisites

1.  **Vercel Account**: [Sign up here](https://vercel.com/signup).
2.  **GitHub Repository**: Ensure your project is pushed to GitHub.
3.  **Cloudflared**: Tool to create a secure tunnel to your local machine.

    ```bash
    # Update brew first to avoid errors
    brew update

    # Install using the official Cloudflare tap
    brew install cloudflare/cloudflare/cloudflared
    ```

---

## Part 2: Backend Setup (Your Mac)

The backend must be running on your machine to serve the heavy AI models (YOLO11 + Llama 3.2).

### 1. Start the Backend

Open a terminal in your project root:

```bash
# Activate your virtual environment
source venv/bin/activate

# Navigate to backend directory
cd backend

# Start the FastAPI server
python main.py
```

_Verify it's running at `http://localhost:8000/docs`_

### 2. Start Ollama (if not running)

Open a new terminal:

```bash
ollama serve
```

### 3. Create the Public Tunnel

Open a new terminal to expose port 8000 to the internet:

```bash
cloudflared tunnel --url http://localhost:8000
```

**Copy the Output URL**:
Look for a line like this in the terminal output:

```
https://random-words-here.trycloudflare.com
```

_This is your temporary **Backend URL**._

---

## Part 3: Frontend Deployment (Vercel)

### 1. Create Project on Vercel

1.  Go to the [Vercel Dashboard](https://vercel.com/dashboard).
2.  Click **"Add New..."** -> **"Project"**.
3.  Import your `final-project` repository.

### 2. Configure Settings

1.  **Framework Preset**: Next.js (Should be auto-detected).
2.  **Root Directory**: Click "Edit" and select `frontend`. **(Crucial Step)**.

### 3. Set Environment Variables

Expand the **Environment Variables** section and add:

| Key                   | Value                                                     |
| --------------------- | --------------------------------------------------------- |
| `NEXT_PUBLIC_API_URL` | `https://<your-tunnel-url>.trycloudflare.com`             |
| `NEXT_PUBLIC_WS_URL`  | `wss://<your-tunnel-url>.trycloudflare.com/api/ws/camera` |

_Note: Replace `https://` with `wss://` for the WS_URL variable._

### 4. Deploy

Click **"Deploy"**. Vercel will build your site and give you a live URL (e.g., `https://describe-my-environment.vercel.app`).

---

## Part 4: Running a Live Demo

When you want to show the project to someone remotely:

1.  **Start Backend**: Run `python main.py` in `backend/`.
2.  **Start Tunnel**: Run `cloudflared tunnel --url http://localhost:8000`.
3.  **Update Frontend**:
    - Go to Vercel Dashboard -> Your Project -> Settings -> Environment Variables.
    - Update `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_WS_URL` with the new tunnel URL.
    - Go to **Deployments** tab -> Redeploy the latest commit (3 dots -> Redeploy).
    - _(Alternatively, use a persistent Cloudflare Tunnel domain to avoid updating variables every time)._

---

## Troubleshooting

- **"Backend Disconnected" Alert**:

  - Check if `cloudflared` is still running.
  - Check if the Vercel Environment Variables match your current tunnel URL.
  - Redeploying takes ~1 minute to update the variables.

- **Latency Issues**:
  - The tunnel adds a small amount of latency.
  - Ensure your Mac is connected to high-speed internet (Ethernet preferred).
