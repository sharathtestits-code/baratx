# Security Policy

## Reporting a vulnerability

Email **hello@barathx.com** with a description of the issue, steps to reproduce, and impact.

Please do **not** open a public GitHub issue for security bugs until a fix is available.

## What is in this repository

This monorepo contains application **source code** and documentation. It does **not** include production secrets.

Never commit:

- `.env` files with real passwords, `ADMIN_SECRET`, `JWT_SECRET`, Resend/MSG91 keys
- Railway / Cloudflare / GitHub tokens
- Database dumps or user PII

Use `.env.example` / `brand/qa/env.qa.example` as templates only.
