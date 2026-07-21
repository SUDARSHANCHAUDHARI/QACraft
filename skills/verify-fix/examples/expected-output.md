# Example output excerpt

```text
Verification: PARTIALLY FIXED

Original issue:
The reboot loop no longer occurs.

Remaining problem:
After reconnection, the player displays the latest playlist but reports the previous playlist version for approximately three minutes.

Regression checks:
- Cached playback: PASS
- First reboot: PASS
- Reconnect metadata: FAIL
- Second reboot: PASS

Next action:
Keep QA-5520 open or split the remaining metadata issue after Product confirms impact.
```
