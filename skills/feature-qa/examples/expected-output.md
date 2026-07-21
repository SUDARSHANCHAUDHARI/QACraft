# Example output excerpt

```text
Outcome: BLOCKED

Reason:
Required Member permission scenario could not be completed because the preview API returned an environment-wide authentication error.

Verified:
- Deployment manifest contains the approved frontend and API commits.
- Admin happy path passed.
- No production origin was contacted.
- Test data remains isolated under run QA-1234-01.

Next action:
Restore preview authentication, revalidate the run context, and resume from scenario P0-03.
```
