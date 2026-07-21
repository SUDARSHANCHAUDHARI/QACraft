# Example output excerpt

```text
Handoff status: READY WITH RISKS

Current state:
Two SCOS devices remain paired to the staging organisation and are on the current 3.1.14 candidate.

Completed:
- OTA update
- Reboot
- Wi-Fi to Ethernet switch
- Cached playback

Blocked:
SD flasher validation because the release image is missing.

First action:
Confirm the published artifact hash, then execute scenario SCOS-OTA-07.

Do not:
Clear cache, reset pairing, or overwrite the current SD card before preserving the existing logs.
```
