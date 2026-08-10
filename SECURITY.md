# Security Policy

## Supported versions

This is a portfolio / sample project. Security fixes are applied on a best-effort basis on the default development branch.

## Reporting a vulnerability

Do **not** open a public issue with secrets, tokens, private keys, or production credentials.

Email the maintainer via the GitHub profile contact, or open a private security advisory on the repository if available.

Please include:

- Affected repo and commit/branch
- Steps to reproduce
- Impact assessment

## Secrets hygiene

- Never commit `.env`, `.env.deploy`, `*.pem`, or real AWS / registry credentials
- Use `*.example` files as templates only
- Rotate any credential that may have been exposed in git history before making the repository public
- Seed users in the README are local demo accounts only
