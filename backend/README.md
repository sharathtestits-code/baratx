# IndiaVoice backend (demo)

FastAPI backend for user signup/login — email+password and phone+OTP.

## Run

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Notes

- SQLite database (`indiavoice.db`) is created automatically on first run.
- Phone OTP is **not sent via real SMS** — the demo endpoint returns `dev_otp`
  directly in the response so you can test the flow without an SMS provider.
  Before shipping, wire in a provider (MSG91, Twilio Verify, etc.) and drop
  the `dev_otp` field from the response.
- JWT secret defaults to a dev value; set `JWT_SECRET` env var in production.
