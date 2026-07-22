# QACraft end-to-end demo

This demo uses a temporary project and exercises installation, verification, behavior evaluation, update, and uninstall without contacting external systems.

Run the commands from the QACraft repository root.

## 1. Validate QACraft

```bash
python3 scripts/qacraft.py doctor
python3 scripts/qacraft.py release-check
```

Both commands should exit with code `0`.

## 2. Create an isolated demo project

```bash
DEMO_PROJECT="$(mktemp -d)/qacraft-demo"
mkdir -p "$DEMO_PROJECT"
printf '# Demo project\n' > "$DEMO_PROJECT/README.md"
```

The existing project README is intentionally unrelated and must remain untouched throughout the demo.

## 3. Preview a Codex installation

```bash
python3 scripts/qacraft.py install feature-qa \
  --agent codex \
  --destination "$DEMO_PROJECT"
```

Expected behavior:

- JSON reports `mode` as `preview-only`;
- `writes_performed` is `false`;
- the target path is `.agents/skills/feature-qa/`;
- no files are created.

## 4. Apply and verify

```bash
python3 scripts/qacraft.py install feature-qa \
  --agent codex \
  --destination "$DEMO_PROJECT" \
  --apply

python3 scripts/qacraft.py verify-install \
  --agent codex \
  --destination "$DEMO_PROJECT"
```

Expected files:

```text
$DEMO_PROJECT/.agents/skills/feature-qa/SKILL.md
$DEMO_PROJECT/.agents/skills/feature-qa/examples/request.md
$DEMO_PROJECT/.agents/skills/feature-qa/examples/expected-output.md
$DEMO_PROJECT/.agents/skills/feature-qa/templates/report.yaml
$DEMO_PROJECT/.agents/qacraft/shared/
$DEMO_PROJECT/.agents/qacraft/manifest.json
```

Verification should report `healthy: true`.

## 5. Evaluate a structured candidate

```bash
python3 scripts/qacraft.py evaluate \
  --input evaluations/examples/feature-qa-pass.json
```

Expected result:

- `passed` is `true`;
- `score` equals `max_score`;
- all seven checks are listed in `passed_checks`.

## 6. Update the installed skill set

Preview adding `/bug-report`:

```bash
python3 scripts/qacraft.py update feature-qa bug-report \
  --agent codex \
  --destination "$DEMO_PROJECT"
```

Apply and verify:

```bash
python3 scripts/qacraft.py update feature-qa bug-report \
  --agent codex \
  --destination "$DEMO_PROJECT" \
  --apply

python3 scripts/qacraft.py verify-install \
  --agent codex \
  --destination "$DEMO_PROJECT"
```

The Codex manifest should now list `bug-report` and `feature-qa`.

## 7. Demonstrate conflict protection

Create a separate project containing an unowned target file:

```bash
CONFLICT_PROJECT="$(mktemp -d)/qacraft-conflict"
mkdir -p "$CONFLICT_PROJECT/.agents/skills/feature-qa"
printf 'unowned file\n' > "$CONFLICT_PROJECT/.agents/skills/feature-qa/SKILL.md"

python3 scripts/qacraft.py install feature-qa \
  --agent codex \
  --destination "$CONFLICT_PROJECT" \
  --apply
```

Expected behavior:

- installation exits with code `1`;
- the unowned file remains unchanged;
- no QACraft manifest is created.

## 8. Uninstall safely

Preview and apply:

```bash
python3 scripts/qacraft.py uninstall \
  --agent codex \
  --destination "$DEMO_PROJECT"

python3 scripts/qacraft.py uninstall \
  --agent codex \
  --destination "$DEMO_PROJECT" \
  --apply
```

Expected behavior:

- QACraft-managed Codex files and empty managed directories are removed;
- `$DEMO_PROJECT/README.md` remains untouched;
- no Claude Code or generic files are affected.

## Claude Code variation

Repeat the lifecycle with `--agent claude-code`. Skills will be installed under `.claude/skills/` and tracked by `.claude/qacraft/manifest.json`.

## Cleanup

```bash
rm -rf "$(dirname "$DEMO_PROJECT")" "$(dirname "$CONFLICT_PROJECT")"
```

The demo does not use network access, external models, customer data, production systems, or external writes.
