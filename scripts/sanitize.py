#!/usr/bin/env python3
"""Try to redact common secret patterns from text so logs are safe to share.

CI/CD logs and Kubernetes output routinely contain credentials, tokens, and
internal hostnames. This helper redacts the most common patterns via a word list
of regexes and simple keyword matching. It is a first-pass filter, not a
guarantee: always review output manually before sharing.

Usage:
    python sanitize.py < input.log > output.log
    python sanitize.py input.log -o output.log
    python sanitize.py --diff input.log   # print changed lines only

Exit status: 0 if nothing was changed (input looked clean), 1 if redactions
occurred, 2 on error. This lets CI or manual workflows detect dirty inputs.
"""

from __future__ import annotations

import argparse
import base64
import re
import sys

__all__ = ["redact", "redact_line", "guess_b64_credentials"]

# Regex substitutions applied to every line. Order matters: longer/more specific
# patterns come first so they are not partially rewritten by generic ones.
REDACTIONS: list[tuple[re.Pattern[str], str]] = [
    # URL-embedded credentials: scheme://user:password@host/...
    (re.compile(r"://([^/\s:@]+):([^@\s/]+)@"), r"://\1:<redacted>@"),
    # Bearer / token-style auth headers.
    (re.compile(r"(?i)\b(authorization|api[_-]?key|api[_-]?token|bearer)\b\s*[:=]?\s*([A-Za-z0-9._~+/=-]{8,})"), r"\1=<redacted>"),
    # Cloud provider credential environment variables.
    (re.compile(r"(?i)\b(AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|AZURE_CLIENT_SECRET|GOOGLE_APPLICATION_CREDENTIALS)=[^\s]+"), r"\1=<redacted>"),
    # Database connection strings (postgres/mysql/redis-style).
    (re.compile(r"(?i)\b(host|password|secret|token|access[_-]?key)\s*[:=]\s*('[^']*'|\"[^\"]*\"|[^\s]+)"), r"\1=<redacted>"),
    # Kubernetes secret manifest values.
    (re.compile(r"(?i)^(\s*(?:stringData|data):\s*)(\S.*\S|\S)$"), r"\1<redacted>"),
    # Long hex strings that look like tokens/hashes (40-64+ chars).
    (re.compile(r"\b[a-f0-9]{40,}\b"), "<redacted>"),
    # JWT-like tokens.
    (re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.?[A-Za-z0-9_-]*"), "<redacted>"),
    # IPv4 addresses (internal, usually safe to drop from shared logs).
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "<ip-redacted>"),
]

# Base64-encoded values matching known secret shapes (e.g. dockerconfigjson,
# kubeconfig contents).
_SECRET_B64_KEYS = ("auth", "password", "token", "config", "ca.crt")


def guess_b64_credentials(value: str, key: str | None = None) -> bool:
    """Best-effort: try to decode base64 and see if it looks like a credential."""
    if len(value) < 20:
        return False
    try:
        decoded = base64.b64decode(value, validate=False)
    except Exception:
        return False
    try:
        text = decoded.decode("utf-8", errors="ignore")
    except Exception:
        return False
    lower = (key or "").lower()
    if any(s in lower for s in _SECRET_B64_KEYS) and any(c in text for c in "{}:\""):
        return True
    return bool(re.search(r"(?i)(password|secret|token|authorization|username)", text))


def redact_line(line: str) -> str:
    new = line
    for pattern, repl in REDACTIONS:
        new = pattern.sub(repl, new)
    # Extra pass: a key: <long-base64> that decodes into config-like text.
    def _maybe_b64(m: re.Match[str]) -> str:
        key = m.group(1)
        val = m.group(2)
        return f"{key}=<redacted>" if guess_b64_credentials(val, key) else m.group(0)

    return re.sub(r"(?i)\b([a-z0-9_.-]{2,20})\s*[:=]\s*([A-Za-z0-9+/=]{20,})", _maybe_b64, new)


def redact(text: str) -> str:
    return "".join(redact_line(line) for line in text.splitlines(keepends=True))


def _read(path: str | None) -> str:
    if path is None or path == "-":
        return sys.stdin.read()
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError as e:
        print(f"sanitize.py: cannot read {path}: {e}", file=sys.stderr)
        raise SystemExit(2)


def _write(text: str, out: str | None) -> None:
    if out is None or out == "-":
        sys.stdout.write(text)
    else:
        try:
            with open(out, "w", encoding="utf-8") as f:
                f.write(text)
        except OSError as e:
            print(f"sanitize.py: cannot write {out}: {e}", file=sys.stderr)
            raise SystemExit(2)


def main() -> None:
    ap = argparse.ArgumentParser(description="Best-effort redaction of secrets from logs.")
    ap.add_argument("input", nargs="?", default=None, help="input log file (default: stdin)")
    ap.add_argument("-o", "--output", default=None, help="output file (default: stdout)")
    ap.add_argument("--diff", action="store_true", help="print only changed lines")
    args = ap.parse_args()

    text = _read(args.input)
    result = "".join(redact_line(l) if l else l for l in text.splitlines(keepends=True))
    if args.diff:
        for orig, new in zip(text.splitlines(), result.splitlines()):
            if orig != new:
                print(f"- {orig[:200]}")
                print(f"+ {new[:200]}")
        changed = sum(1 for a, b in zip(text.splitlines(), result.splitlines()) if a != b)
        sys.exit(1 if changed else 0)
    _write(result, args.output)
    changed = any(l.strip() and redact_line(l) != l for l in text.splitlines())
    sys.exit(1 if changed else 0)


if __name__ == "__main__":
    main()
