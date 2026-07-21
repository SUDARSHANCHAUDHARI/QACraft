# Example output excerpt

```text
Outcome: ENVIRONMENT-SPECIFIC

Evidence:
- Same device and content work over Ethernet.
- Wi-Fi obtains an IP address but TLS requests fail.
- A laboratory device on another Wi-Fi network works.
- No cache or pairing reset was performed.

Next customer-safe step:
Test the affected device on a mobile hotspot and collect the exact time of the attempt.

Internal direction:
Investigate customer Wi-Fi proxy, firewall, DNS, or TLS interception before treating this as a player defect.
```
