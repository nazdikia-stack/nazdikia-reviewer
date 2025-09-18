
# Nazdikia – Iranian List Reviewer (Web MVP)

This is a quick Streamlit-based web version of your Tkinter reviewer app.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
Then open the URL shown in the terminal (default: http://localhost:8501).

## How to use
1. Upload your `iranian_only_fa.csv` in the left sidebar.
2. Review rows:
   - **Approve & Next** marks the row as checked (`check? = checked`).
   - **Delete** removes matching rows (same name/city/website/link) from the dataset.
   - **Back** moves to the previous unchecked row.
3. Click **Download reviewed CSV** (sidebar) to save your updated file.

## Deploy fast

### Option A) Streamlit Community Cloud (fastest)
1. Push these files to a **public GitHub repo**.
2. Go to https://share.streamlit.io (Streamlit Community Cloud), click **New app**, connect your repo, choose `app.py`.
3. Share the URL with your team.

> Tip: For basic authentication, you can add the `streamlit-authenticator` package and a small login form later.

### Option B) Render (simple)
1. Create a new Web Service on https://render.com .
2. Repo: your GitHub repo.
3. Runtime: Python 3.x
4. Build command:
   ```
   pip install -r requirements.txt
   ```
5. Start command:
   ```
   streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```

### Notes on multi-user editing
- This MVP keeps user edits **in each user session**; users download their reviewed CSV afterwards.
- For true multi-user, centralize storage (e.g., PostgreSQL/SQLite on server, or a Google Sheet) and add user auth. That can be added next.
