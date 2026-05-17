# Done

Docs-derived decisions already settled for the initial build.

1. [x] Project direction: terminal-first modern BBS with live chat, forums, ANSI art, file libraries, and doors/modules.
2. [x] Initial implementation language: Python first, with a possible Rust core later.
3. [x] Transport direction: WebSocket API over HTTPS, with file downloads allowed over HTTPS.
4. [x] Rendering model: client-rendered UI with server-provided ANSI art and theme content.
5. [x] Terminal UX direction: hybrid-capable client, starting from a line-oriented shell.
6. [x] Access model: multiple invite codes rather than a single shared server password.
7. [x] Identity model: server-secret HMAC tripcodes for display identity.
8. [x] Admin direction: public/private key based admin authentication, not tripcode-based admin powers.
9. [x] Live chat retention: ephemeral live chat with no old chat shown by default.
10. [x] Persistent storage choice: SQLite for forums, file metadata, settings-like state, and other durable MVP data.
11. [x] File library scope: read-only sysop-managed file library with path traversal protection.
12. [x] File download direction: HTTPS downloads using expiring signed access tokens or invite-backed access.
13. [x] ANSI customization: template-driven `.ans` screens in a theme directory.
14. [x] Plugin model: trusted in-process Python plugins first.
15. [x] Privacy/logging direction: minimal structured event logs, no secrets, no chat bodies.
16. [x] Python scaffold: package layout, default theme files, test package, console entrypoints, dependency metadata, and local ignore rules.
