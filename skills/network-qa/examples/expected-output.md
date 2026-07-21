# Example output excerpt

```text
Network conclusion: NETWORK OWNER ACTION

Isolation:
- Wi-Fi: DNS, TLS, and application requests succeed.
- Ethernet VLAN: DNS succeeds, TCP connects, but TLS sessions are closed during handshake for required CloudFront and Google origins.
- Same device, build, content, and time.

Classification:
Proxy, firewall, or TLS interception on the Ethernet path.

Customer-safe request:
Ask network IT to review TLS inspection and allow the documented required domains for the affected VLAN.
```
