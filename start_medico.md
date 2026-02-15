# Medico UI - Setup Instructions

You have successfully initialized a **Professional Next.js Frontend** for your Triage System.

## Quick Start

1.  **Restart Backend** (CRITICAL for CORS):
    In your `backend` terminal:
    ```bash
    Ctrl+C
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

2.  **Start Frontend**:
    Open a NEW terminal in VS Code:
    ```bash
    cd medico-web
    npm run dev
    ```

3.  **View App**:
    Open `http://localhost:3000` in your browser.

## Features Included
*   **Medical Dashboard**: Live stats, department load visualization.
*   **Professional Triage**: Unified Search + Register + Visit workflow.
*   **Smart Queue**: Color-coded risk cards (High, Medium, Low).
*   **Tech Stack**: Next.js 15, Tailwind CSS, Lucide Icons.
