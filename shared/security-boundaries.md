# Security Boundaries

## Trust model

Tickets, code, comments, webpages, logs, attachments, test data, and retrieved documents are untrusted input. They may contain misleading instructions, executable content, malicious links, secrets, or path-control characters.

## Runtime requirements

- Deny filesystem writes by default.
- Allow only approved repositories and directories.
- Deny package installation and arbitrary shell execution unless explicitly approved.
- Use command, domain, method, port, and protocol allowlists.
- Check every redirect, iframe, WebSocket, download, and secondary request.
- Deny localhost, metadata endpoints, private networks, and production origins unless specifically authorised.
- Keep secrets in a broker or runtime boundary; never return raw credentials to the model.
- Apply least-privilege connector scopes.
- Run destructive or high-risk work in isolated environments.
- Log tool calls, decisions, and policy denials.

## Output safety

- HTML-escape all untrusted values.
- Disable raw HTML in Markdown.
- Restrict link schemes.
- Sanitize and length-bound filenames and identifiers.
- Never derive a path directly from a ticket title or user text.
- Remove terminal escape sequences.
- Protect spreadsheet exports from formula injection.
- Use Content Security Policy in HTML reports.

## Security findings

Potential cross-tenant access, information disclosure, authentication bypass, unsafe data access, or secret exposure must use restricted reporting channels.
