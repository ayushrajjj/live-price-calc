# Unlisted Share Price System

## Name Resolution
- Uses deterministic canonical mapping
- No fuzzy guessing
- All aliases are explicitly defined

## Unknown Names
- Automatically logged to unknown_companies.csv
- Reviewed and added manually

## Data Integrity
- Raw data never modified
- Clean data generated via transform step
- Dashboard is read-only

This system prioritizes accuracy and auditability.

## Deployment & Admin Access

This project can be hosted on Streamlit Community Cloud, Render, or any container/VPS. Below are quick steps to deploy and how to access the admin panel.

### Streamlit Community Cloud (recommended for quick free hosting)

1. Push the repository to GitHub (public or private).
2. Ensure `requirements.txt` lists `streamlit` and `pandas` (and any other deps).
3. Visit https://share.streamlit.io and create a new app. Point it to your repo and branch and set the entrypoint to `app.py`.
4. In the Streamlit app settings, add secrets:

```
ADMIN_USER="<your_admin_user>"
ADMIN_PASS="<your_admin_password>"
```

5. Deploy and open the URL provided by Streamlit Cloud.

Accessing the Admin panel:
- Open: `https://<your-app>.streamlit.app/?admin=1` or visit `https://<your-app>.streamlit.app/admin` — the app will redirect `/admin` to `/?admin=1` and show the admin page.

Security recommendations:
- Do not keep `admin/admin` credentials in production. Use strong secrets.
- For production, consider using a proxy with access control or a paid Streamlit plan that supports private apps.

### Alternative: Render

1. Create a free Render account and connect your GitHub repository.
2. Create a Web Service and set the build command to: `pip install -r requirements.txt`.
3. Set the start command to: `streamlit run app.py --server.port $PORT`.
4. Add environment variables `ADMIN_USER` and `ADMIN_PASS` in Render's dashboard.

### Alternative: Docker / VPS

1. Add a Dockerfile similar to:

```
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

2. Build and run on your VM or cloud provider, secure with TLS and a reverse proxy for production.

If you want, I can add a short `README` section showing how to set up Streamlit Community Cloud step-by-step with screenshots or provide a `deploy.md` with screenshots.
