# Certificate Transparency in production

- Author: Certificate Transparency project (Google / Linux
  Foundation).
- Source: "How CT Works",
  <https://certificate.transparency.dev/howctworks/>; underlying
  structures: RFC 6962 (Laurie, Langley, Kasper, IETF 2013,
  <https://www.rfc-editor.org/rfc/rfc6962>).
- Accessed: 2026-07-19.
- Status: summarised from the source by a research agent; re-verify
  before citing.

## Core content

- Production CT logs are append-only Merkle trees per RFC 6962:
  "Certificates can only be added to a log, not deleted, modified, or
  retroactively inserted."
- A CA submits a (pre)certificate and receives a Signed Certificate
  Timestamp (SCT), a promise to add the certificate within the
  Maximum Merge Delay (standard 24 hours); SCTs are embedded in
  certificates and delivered in TLS handshakes.
- Logs periodically publish Signed Tree Heads; monitors and auditors
  use RFC 6962 consistency proofs (earlier tree is a prefix of the
  later one) and inclusion proofs; anyone can query a log and verify
  it is well behaved.
- Scale: billions of certificates across Google, Cloudflare, Let's
  Encrypt and other operators' logs (the page gives no exact count).

## Understanding and use in the paper

- One-paragraph production grounding for Section 4 (append-only logs):
  CT is the largest deployed authenticated append-only Merkle log
  with third-party verifiability.
- The RFC 6962 audit/consistency proof definitions themselves are
  covered by the theory digest (RFC 6962 note, pending).
