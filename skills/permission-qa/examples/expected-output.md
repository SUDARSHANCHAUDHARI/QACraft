# Example output excerpt

```text
Permission result: SECURITY ESCALATION

Finding:
A Member cannot see the Edit control in the UI but can update the playlist name through a direct API request after switching organisations.

Classification:
Cross-tenant over-permission.

Evidence:
Verified Member token, organisation membership map, request/response capture, and before/after resource state.

Publication:
Restricted security route required.
```
