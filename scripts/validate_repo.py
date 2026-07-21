#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.aria_refs = []
        self.hrefs = []
        self.srcs = []
        self.tables = 0
        self.captions = 0
        self.meta_csp = False
        self.meta_robots = False
        self.in_table = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if "aria-labelledby" in a:
            self.aria_refs.extend(a["aria-labelledby"].split())
        if "href" in a:
            self.hrefs.append(a["href"])
        if "src" in a:
            self.srcs.append(a["src"])
        if tag == "table":
            self.tables += 1
            self.in_table += 1
        if tag == "caption" and self.in_table:
            self.captions += 1
        if tag == "meta" and a.get("http-equiv", "").lower() == "content-security-policy":
            self.meta_csp = True
        if tag == "meta" and a.get("name", "").lower() == "robots":
            self.meta_robots = True

    def handle_endtag(self, tag):
        if tag == "table" and self.in_table:
            self.in_table -= 1

def fail(errors, message):
    errors.append(message)

def validate_html(path, errors):
    text = path.read_text(encoding="utf-8")
    p = AuditParser()
    try:
        p.feed(text)
    except Exception as exc:
        fail(errors, f"{path}: HTML parser error: {exc}")
        return

    if not text.lower().startswith("<!doctype html>"):
        fail(errors, f"{path}: missing HTML5 doctype")
    if len(p.ids) != len(set(p.ids)):
        duplicates = sorted({x for x in p.ids if p.ids.count(x) > 1})
        fail(errors, f"{path}: duplicate ids: {duplicates}")
    missing = sorted(set(p.aria_refs) - set(p.ids))
    if missing:
        fail(errors, f"{path}: broken aria-labelledby references: {missing}")
    if p.tables != p.captions:
        fail(errors, f"{path}: {p.tables} tables but {p.captions} captions")
    if not p.meta_csp:
        fail(errors, f"{path}: missing Content Security Policy")
    if not p.meta_robots:
        fail(errors, f"{path}: missing robots policy")
    if "<script" in text.lower():
        fail(errors, f"{path}: scripts are not allowed in static documentation")
    if "TODO" in text or "FIXME" in text:
        fail(errors, f"{path}: unresolved TODO or FIXME")
    if "@media print" not in text:
        fail(errors, f"{path}: missing print stylesheet")
    if path.name != "index.html" and len(text) < 18000:
        fail(errors, f"{path}: overview is unexpectedly small ({len(text)} bytes)")

    for value in p.srcs:
        parsed = urlparse(value)
        if parsed.scheme not in ("", "data"):
            fail(errors, f"{path}: external source not allowed: {value}")
    for value in p.hrefs:
        if value.startswith("data:"):
            continue
        if value.startswith("#"):
            target = value[1:]
            if target and target not in p.ids:
                fail(errors, f"{path}: broken anchor #{target}")
            continue
        parsed = urlparse(value)
        if parsed.scheme in ("http", "https", "javascript", "file"):
            fail(errors, f"{path}: external or unsafe link not allowed: {value}")
            continue
        local = value.split("#", 1)[0]
        if local:
            resolved = (path.parent / local).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                fail(errors, f"{path}: link escapes repository: {value}")
                continue
            if not resolved.exists():
                fail(errors, f"{path}: broken local link: {value}")

def validate_skill(skill, errors):
    slug = skill["slug"]
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        fail(errors, f"catalog: unsafe slug {slug}")
    if skill.get("command") != f"/{slug}":
        fail(errors, f"catalog: command mismatch for {slug}")
    for field in ("title","summary","use_when","not_for","example_request","example_output"):
        if not str(skill.get(field, "")).strip():
            fail(errors, f"catalog: {slug} missing {field}")
    if len(skill.get("phases", [])) != 8:
        fail(errors, f"catalog: {slug} must have exactly 8 phases")
    gates = [p for p in skill.get("phases", []) if p.get("gate")]
    if len(gates) < 2:
        fail(errors, f"catalog: {slug} has too few approval gates")
    if len(skill.get("verdicts", [])) < 4:
        fail(errors, f"catalog: {slug} has too few verdicts")
    if len(skill.get("evidence", [])) < 5:
        fail(errors, f"catalog: {slug} has too few evidence rules")
    if len(skill.get("controls", [])) < 5:
        fail(errors, f"catalog: {slug} has too few runtime controls")
    if len(skill.get("decisions", [])) < 4:
        fail(errors, f"catalog: {slug} has too few decisions")
    if len(skill.get("boundaries", [])) < 5:
        fail(errors, f"catalog: {slug} has too few boundaries")
    if len(skill.get("outputs", [])) < 6:
        fail(errors, f"catalog: {slug} has too few outputs")
    if len(set(skill.get("outputs", []))) != len(skill.get("outputs", [])):
        fail(errors, f"catalog: {slug} has duplicate outputs")

    sd = ROOT / "skills" / slug
    required = [
        sd / "SKILL.md",
        sd / "overview.html",
        sd / "examples" / "request.md",
        sd / "examples" / "expected-output.md",
        sd / "templates" / "report.yaml",
        ROOT / "docs" / "skills" / f"{slug}.html",
    ]
    for path in required:
        if not path.exists():
            fail(errors, f"missing required file: {path}")

    skill_md = sd / "SKILL.md"
    if skill_md.exists():
        text = skill_md.read_text(encoding="utf-8")
        headings = [
            "# /", "## Purpose", "## Non-negotiable operating rules", "## Workflow",
            "## Approval gates", "## Result states", "## Evidence contract",
            "## Runtime controls", "## Ordered decision policy", "## Known limitations",
            "## Output contract", "## Failure handling", "## Completion criteria"
        ]
        for heading in headings:
            if heading not in text:
                fail(errors, f"{skill_md}: missing section {heading}")
        if len(text.splitlines()) < 140:
            fail(errors, f"{skill_md}: specification is unexpectedly short")
        if f"name: {slug}" not in text or f"command: /{slug}" not in text:
            fail(errors, f"{skill_md}: front matter mismatch")

def main():
    errors = []
    catalog_path = ROOT / "catalog" / "skills.json"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Cannot read catalog: {exc}", file=sys.stderr)
        return 2

    skills = catalog.get("skills", [])
    if len(skills) != 25:
        fail(errors, f"catalog: expected 25 skills, found {len(skills)}")
    slugs = [s.get("slug") for s in skills]
    if len(slugs) != len(set(slugs)):
        fail(errors, "catalog: duplicate skill slugs")

    for s in skills:
        validate_skill(s, errors)

    for schema in sorted((ROOT / "schemas").glob("*.json")):
        try:
            json.loads(schema.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(errors, f"{schema}: invalid JSON: {exc}")

    html_files = sorted(ROOT.glob("index.html")) + sorted((ROOT / "docs").rglob("*.html")) + sorted((ROOT / "skills").rglob("overview.html"))
    expected_html = 1 + 1 + 25 + 25
    if len(html_files) != expected_html:
        fail(errors, f"expected {expected_html} HTML files, found {len(html_files)}")
    for path in html_files:
        validate_html(path, errors)

    required_shared = {
        "qa-standards.md","evidence-policy.md","security-boundaries.md","approval-policy.md",
        "result-model.md","data-safety.md","release-policy.md","publication-policy.md"
    }
    actual_shared = {p.name for p in (ROOT / "shared").glob("*.md")}
    if not required_shared.issubset(actual_shared):
        fail(errors, f"shared policies missing: {sorted(required_shared - actual_shared)}")

    if errors:
        print(f"Validation failed with {len(errors)} issue(s):", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        return 1

    total_files = sum(1 for p in ROOT.rglob("*") if p.is_file())
    print(f"Validation passed: {len(skills)} skills, {len(html_files)} HTML files, {total_files} repository files.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
