# Example output excerpt

```text
API result: REJECT

Release-blocking finding:
Two concurrent updates with the same version both return 200, and the earlier write silently overwrites the later one.

Other results:
- Validation: PASS
- Member read permission: PASS
- Member update permission: PASS
- Pagination continuity: PASS
- Idempotent create: PASS

Classification:
Data-integrity and concurrency failure.
```
