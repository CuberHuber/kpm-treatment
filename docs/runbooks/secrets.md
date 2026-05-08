# Secrets Detection Runbook

Operational steps for `detect-secrets` in this repository.
The scanner is wired into `pre-commit` and uses a custom plugin
at `tools/detect_secrets_plugins/kpm_password.py`
that recognises Kaspersky Password Manager export formats.
The persistent state lives in `.secrets.baseline` (JSON).

All commands run from the repository root.

## Init

Run once after cloning the repo, or once per fresh checkout.

```bash
uv sync                       # installs detect-secrets and other dev deps
uv run pre-commit install     # wires the git hooks (pre-commit + commit-msg)
```

`.secrets.baseline` is checked into the repo,
so a fresh clone already has a working baseline —
no scan needed at init time.

If the baseline is missing or corrupt, regenerate it from scratch:

```bash
uv run detect-secrets scan \
  --plugin tools/detect_secrets_plugins/kpm_password.py \
  --exclude-files '^\.secrets\.baseline$' \
  > .secrets.baseline
git add .secrets.baseline
```

## Update

Run when the pre-commit hook flags a new line as a secret
and you have confirmed it is not a real leak
(test fixture, sample export, intentional placeholder).
The merge form preserves prior `is_verified` / `is_secret` audit decisions.

```bash
uv run detect-secrets scan \
  --plugin tools/detect_secrets_plugins/kpm_password.py \
  --exclude-files '^\.secrets\.baseline$' \
  --baseline .secrets.baseline
git add .secrets.baseline
```

Commit the baseline change in the same commit as the code change
that introduced the new finding.

If the finding is a real secret,
do **not** update the baseline.
Remove the secret from the code, rotate the credential,
and only then re-run the hook.

## Scan

Ad-hoc scans for verification or investigation.
None of these write to `.secrets.baseline`.

Whole tracked tree, full report:

```bash
uv run detect-secrets scan \
  --plugin tools/detect_secrets_plugins/kpm_password.py \
  --exclude-files '^\.secrets\.baseline$'
```

Run the configured pre-commit hook against every tracked file:

```bash
uv run pre-commit run detect-secrets --all-files
```

Run the hook against specific files only:

```bash
uv run pre-commit run detect-secrets --files path/to/file1 path/to/file2
```

Probe a single literal string against every detector
(useful for confirming whether a given pattern would be caught):

```bash
uv run detect-secrets scan --string 'Password: hunter2'
```

## Audit

Walk through every entry in the baseline
and mark each as a real secret or a false positive.
Audit results turn into the `is_verified` / `is_secret` fields
that downstream tooling (and `--only-verified` runs) consume.

Interactive review:

```bash
uv run detect-secrets audit .secrets.baseline
```

Keys during the session:

- `y` — yes, real secret
- `n` — no, false positive
- `s` — skip for now
- `b` — back one entry
- `q` — quit and save

After auditing, commit the updated baseline:

```bash
git add .secrets.baseline
git commit -m "chore: audit detect-secrets baseline"
```

Statistics on audit progress:

```bash
uv run detect-secrets audit --stats .secrets.baseline
```

Human-readable report of all findings:

```bash
uv run detect-secrets audit --report .secrets.baseline
```

## When the hook blocks a commit

The hook prints the file, line, and `Secret Type` it matched.
Decide which of three responses applies.

1. Real secret — remove the value from the code,
   rotate the credential out of band,
   re-stage, re-commit.
2. False positive that should always be silenced on that line —
   add an inline marker:

   ```python
   api_key = "not_a_real_key"  # pragma: allowlist secret
   ```

3. False positive that belongs in the baseline
   (test fixtures, sample exports, documentation examples) —
   run the **Update** step above.

Never bypass the hook with `--no-verify`.
If the hook is wrong, fix the configuration, the plugin, or the baseline —
not the gate.
