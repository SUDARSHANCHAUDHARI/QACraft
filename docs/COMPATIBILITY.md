# QACraft compatibility matrix

## Runtime

| Component | Supported | Notes |
|---|---:|---|
| Python | 3.10+ | Standard-library runtime only |
| macOS | Yes | Filesystem lifecycle and evaluator supported |
| Linux | Yes | Primary CI environment |
| Windows | Expected | Uses `pathlib`; validate locally before release-critical use |
| Network access | Not required | Installer and evaluator are local-only |

## CLI distribution modes

| Mode | Supported | Notes |
|---|---:|---|
| `python3 scripts/qacraft.py` | Yes | Direct source-checkout interface |
| `python -m qacraft` from checkout | Yes | Uses the local canonical asset tree |
| `pip install --no-deps -e .` | Yes | Provides `qacraft` and module entry points backed by the trusted checkout |
| Wheel installation | Not yet | Phase 3.2 must bundle and verify every required asset first |
| Source distribution | Not yet | Phase 3.2 must verify archive contents and installed behavior |
| PyPI/package-index installation | Not yet | No public package claim is made |
| Standalone executable | No | Not implemented |

The editable installation is intentionally source-bound. It refuses to operate when the checkout no longer contains the CLI runtime, catalog, skills, shared policies, or evaluation rubrics. This prevents an incomplete installed wrapper from silently acting as a complete QACraft distribution.

## Agent adapters

| Adapter | Discovery path | Manifest | Lifecycle |
|---|---|---|---|
| Generic | `skills/<slug>/` | `.qacraft-manifest.json` | install, verify, update, uninstall |
| Codex | `.agents/skills/<slug>/` | `.agents/qacraft/manifest.json` | install, verify, update, uninstall |
| Claude Code | `.claude/skills/<slug>/` | `.claude/qacraft/manifest.json` | install, verify, update, uninstall |

The destination passed to the CLI is always an explicit project or installation root. QACraft does not guess global directories or change agent configuration files.

## Behavior evaluations

Deterministic rubrics are included for:

- `/feature-qa`
- `/ticket-review`
- `/bug-report`
- `/verify-fix`
- `/release-qa`

The evaluator checks structured candidate reports for schema conformance, grounding, approvals, evidence, verdict discipline, safety declarations, and output contracts. It does not call an AI model and does not authenticate evidence against external systems.

## Compatibility guarantees

- Existing unowned files are never overwritten.
- Modified managed files block update and uninstall.
- Agent manifests are independent and may coexist in one project.
- Canonical QACraft source files remain unchanged.
- Agent copies receive deterministic standards-compatible frontmatter normalization.
- Failed installs and updates roll back QACraft-managed changes.
- Editable CLI entry points delegate to the existing reviewed runtime instead of duplicating installer logic.

## Intentionally unsupported

- Automatic agent detection
- User-global installation
- Force overwrite or force deletion
- Symlink-based installation
- Unverified wheel, source-distribution, or package-index installation
- Production/customer system access
- Runtime permission enforcement through prompt text
- Automatic GitHub Pages deployment

The generated documentation already lives under `/docs`. Repository owners may enable branch-based GitHub Pages manually when their GitHub plan and repository visibility support it, without adding another automatic Actions workflow.
