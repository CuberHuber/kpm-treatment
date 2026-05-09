# Shortcuts for `detect-secrets` in this repository.
# The bare `detect-secrets audit` subcommand cannot resolve the KPM
# custom plugin from the baseline, so every audit-mode target here
# invokes the wrapper at `tools/detect_secrets_audit.py`.
# Scan-mode targets call `detect-secrets` directly because `scan`
# accepts `--plugin` natively.
# See docs/runbooks/secrets.md for the full procedure.

BASELINE  := .secrets.baseline
PLUGIN    := tools/detect_secrets_plugins/kpm_password.py
WRAPPER   := tools/detect_secrets_audit.py
NORMALIZE := uv run python tools/normalize_secrets_baseline.py $(BASELINE)

SCAN := uv run detect-secrets scan \
  --plugin $(PLUGIN) \
  --exclude-files '^\.secrets\.baseline$$'

.PHONY: help \
        audit audit-stats audit-report \
        scan scan-update scan-init hook

help:
	@echo "Audit targets:"
	@echo "  make audit         Interactive review of $(BASELINE)"
	@echo "  make audit-stats   Per-plugin precision and recall summary"
	@echo "  make audit-report  JSON report of every finding and decision"
	@echo ""
	@echo "Scan targets:"
	@echo "  make scan          Dry-run scan of the tracked tree"
	@echo "  make scan-update   Merge new findings into $(BASELINE) (preserves audit decisions)"
	@echo "  make scan-init     Regenerate $(BASELINE) from scratch (drops audit decisions)"
	@echo "  make hook          Run the pre-commit detect-secrets hook on every tracked file"

audit:
	uv run python $(WRAPPER) audit $(BASELINE)

audit-stats:
	uv run python $(WRAPPER) audit --stats $(BASELINE)

audit-report:
	@uv run python $(WRAPPER) audit --report $(BASELINE)

scan:
	@$(SCAN)

scan-update:
	$(SCAN) --baseline $(BASELINE)
	@$(NORMALIZE)

scan-init:
	$(SCAN) > $(BASELINE)
	@$(NORMALIZE)

hook:
	uv run pre-commit run detect-secrets --all-files
