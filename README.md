# EarnUGX — Lite UGX Earn v1

A mobile-first earning-platform MVP using Flask, SQLAlchemy and a simple HTML/CSS/JavaScript frontend.

## Included

- Registration and login
- Password hashing
- Session authentication
- Demo tasks
- One-time task completion
- Ledger-based earnings
- Dashboard balance calculated from the ledger
- Withdrawal request endpoint
- SQLite for local testing
- PostgreSQL-compatible database configuration

## Important

This is an MVP/demo foundation. Real MTN Mobile Money or Airtel Money payouts, production fraud controls, HTTPS deployment, admin authorization, rate limiting, audit logging and production secrets still need to be implemented before handling real money.

## Run backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The API starts on port 5000.

## Frontend

Open the files in `frontend/` from a suitable local web server and set `API_BASE` in `frontend/app.js` to the deployed Flask API URL.

Do not use the development SECRET_KEY or SQLite database for production.
