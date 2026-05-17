# TODO

Next 10 tasks derived from `docs/pre_design_doc.md`, `docs/pre_design_doc_decisions.md`, and `README.md`.

1. [x] Scaffold the Python project layout.
   - Create the package structure for `bbs/server`, `bbs/client`, `bbs/plugins`, `bbs/themes/default`, and `tests`.
   - Add project metadata and dependency definitions for FastAPI, Uvicorn, Pydantic, SQLite access, Typer, and terminal UI helpers.

2. [ ] Define configuration loading and runtime settings.
   - Add config for server name, database path, invite-code settings, tripcode secret, admin public keys, file library root, theme path, and plugin paths.
   - Ensure secrets are loaded from local config or environment and are never committed by default.

3. [ ] Implement SQLite schema and repository layer.
   - Create tables for boards, threads, replies, file metadata, invite codes, download tokens, moderation state, and minimal audit events.
   - Keep live chat and presence out of persistent storage.

4. [ ] Implement invite-code access control.
   - Support multiple Discord-style invite codes.
   - Allow the terminal client to store accepted access details in a local `.dialect` file for future sessions.
   - Design revocation without introducing full user accounts.

5. [ ] Implement identity primitives.
   - Generate display tripcodes with server-secret HMAC.
   - Add key-based admin authentication using configured public keys.
   - Leave room for optional user public/private key identities later.

6. [ ] Build the FastAPI server and WebSocket protocol skeleton.
   - Add `/ws` connection handling with typed JSON messages.
   - Implement `hello`, auth failure, session ready, error, and ping/pong message flows.
   - Keep the protocol explicit and testable with Pydantic schemas.

7. [ ] Implement session and presence management.
   - Track active sessions in memory.
   - Add `/who` protocol support.
   - Broadcast join/leave events without storing unnecessary metadata.

8. [ ] Implement ephemeral live chat.
   - Add `chat.send` and `chat.message` protocol messages.
   - Broadcast only to users currently online.
   - Follow the decisions file: no old chat scrollback by default.

9. [ ] Build the first terminal client.
   - Start with a hybrid-friendly line-oriented shell.
   - Support connect, persisted local access settings, `/help`, `/who`, `/chat`, and `/quit`.
   - Keep rendering client-side while accepting server-provided ANSI content.

10. [ ] Add the first ANSI theme pipeline.
    - Create `themes/default` with `login.ans`, `motd.ans`, `main_menu.ans`, `boards.ans`, `files.ans`, and `error.ans`.
    - Implement safe template variables such as `{server_name}` and `{online_count}`.
    - Send login/MOTD content through the server protocol for the client to render.
