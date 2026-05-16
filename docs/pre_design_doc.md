# SIGIL//NODE / Modern BBS Design Doc

## 1. Project Intent

Build a modern, terminal-first BBS system: part live hangout, part forum, part file library, part weird cyberpunk/occult art object.

The system should feel like an old-school BBS or MUD, but with modern security expectations, encrypted traffic, modular extensibility, and a sysop-friendly culture of customization.

The first implementation should be in Python. Later, the project may split into a Rust core with Python as the scripting/extensibility layer.

---

## 2. Core Product Goals

### 2.1 Terminal-first social space

Users should connect from a terminal and be able to “hang out” while doing other work.

The experience should support:

* Long-running terminal sessions
* Tmux/screen-friendly usage
* Live presence
* Lightweight chat
* Forum/thread reading and posting
* ANSI/terminal art
* Keyboard-driven navigation
* Minimal browser dependency

### 2.2 Privacy-first, low-account architecture

The system should avoid traditional account storage where possible.

Current decision:

* No persistent user accounts
* Users identify using tripcode-style hashes
* Servers are passworded
* Traffic is encrypted

The system should not store unnecessary user metadata.

### 2.3 Modular BBS platform

Sysops should be able to extend the server with modules, doors, games, art screens, and local custom behavior.

This should feel like:

* Old BBS doors
* MUD plugins
* Discord bots, but terminal-native
* Web 1.0 community weirdness

### 2.4 Server-hosted files

Servers can host files, especially curated sysop collections like ebooks, zines, music, ANSI packs, game files, or local archives.

This should be safe, auditable, and permission-aware.

---

## 3. Already-Made Decisions

| Decision                       |      Status | Notes                                                         |
| ------------------------------ | ----------: | ------------------------------------------------------------- |
| Encrypted traffic              |     Decided | Required. No plaintext protocol for real use.                 |
| Passworded servers             |     Decided | Users need the server password to connect.                    |
| Tripcode-style identities      | Decided-ish | No normal account DB. Need details on exact mechanism.        |
| Live chat                      |     Decided | Only current online users. Minimal/no long-term chat history. |
| Forum/thread feature           |     Decided | Slack/Discord-ish forum channels with threads and replies.    |
| File hosting                   |     Decided | Server hosts files, initially ebook collection.               |
| ANSI art / sysop customization |     Decided | Important part of the vibe, not optional polish.              |
| Modular doors/games            |     Decided | Plugin-like extension system.                                 |
| Terminal-first UX              |     Decided | Primary client is terminal.                                   |
| Python first                   |     Decided | Rust core maybe later.                                        |
| Transmission protocol          |        Open | API, WebSocket, SSH-like, custom TCP/TLS, etc.                |

---

## 4. Major Design Areas

## 4.1 Transport / Protocol

This is the biggest early architectural decision.

The transport determines:

* How users connect
* How encryption works
* Whether a browser/web client is easy later
* Whether a custom terminal client is required
* How hard live chat is
* How hard file download is
* How natural “BBS session” behavior feels

### Option A: SSH-based BBS

Users connect using:

```bash
ssh bbs.example.net
```

The server runs an SSH server library in Python, such as AsyncSSH.

#### Pros

* Encryption is built in
* Terminal-native by default
* Users already understand SSH
* Works well with tmux/screen
* No browser required
* Feels extremely BBS/MUD-like
* Can potentially support SCP/SFTP-style file transfer later
* Authentication mechanisms are already well-understood

#### Cons

* Tripcode/password model may feel awkward on top of SSH
* SSH keys imply identity, which may conflict with “no accounts”
* Browser client becomes harder
* WebSocket/mobile clients become separate work
* Implementing custom UI over SSH requires terminal state handling

#### Good fit when

The goal is maximum terminal purity and fastest secure BBS vibe.

#### Bad fit when

The goal is shared protocol between terminal, browser, and mobile clients.

---

### Option B: WebSocket API over HTTPS

Users run a custom terminal client that connects to:

```text
wss://bbs.example.net/socket
```

The same backend can later support browser clients.

#### Pros

* Encryption via TLS/HTTPS
* Great fit for live chat and presence
* Easy to add browser client later
* Familiar Python stack: FastAPI + WebSockets
* Clean separation between server and client
* Easy JSON protocol
* Easy to test
* Easy to proxy/deploy behind Caddy/nginx

#### Cons

* Requires a custom terminal client
* Less “raw BBS” than SSH
* Users cannot just `ssh` in
* Terminal rendering becomes client-side work
* File downloads need separate HTTP endpoints

#### Good fit when

The project wants a real protocol and multiple future clients.

#### Bad fit when

The project wants users connecting with only stock terminal tools.

---

### Option C: Custom TCP protocol over TLS

Users run a terminal client that opens a TLS socket to the server.

#### Pros

* Maximum control
* Very BBS-like
* Can design exactly around terminal sessions
* No HTTP baggage
* Could be elegant and weird

#### Cons

* More custom protocol/security footguns
* Harder deployment
* Harder client support
* More work than needed for MVP
* Browser support later is awkward

#### Good fit when

The project wants to become a serious custom protocol eventually.

#### Bad fit when

The project needs to ship quickly and safely.

---

### Option D: HTTP API + polling terminal client

The terminal client uses normal HTTPS API calls. Live chat polls periodically.

#### Pros

* Simple to build
* Easy to debug
* Easy REST API
* No persistent socket complexity

#### Cons

* Live chat feels worse
* Presence is less natural
* More server chatter
* Not ideal for “hang out online” vibe

#### Good fit when

The first MVP is mostly forum/files, not live chat.

#### Bad fit when

Live presence is core.

---

### Recommended transport for MVP

Use **FastAPI + WebSockets over HTTPS**.

Reasoning:

* Python-friendly
* Secure with normal TLS
* Supports live chat naturally
* Supports terminal client now
* Supports browser client later
* Lets the protocol be explicit and testable
* Easier than building a custom SSH/TCP world immediately

Possible future:

* Add SSH frontend later as an alternate gateway
* Keep core server protocol/event model independent from transport
* Treat SSH, WebSocket, and future clients as adapters

---

## 4.2 Identity Model

Current decision:

* No traditional accounts
* Tripcode-style identities
* Server password required

### Basic tripcode model

User enters:

```text
name#secret
```

Server displays:

```text
name !triphash
```

The secret is hashed into a stable public tripcode.

Example:

```text
Kassie#mysecret
```

Becomes:

```text
Kassie !x7F92Qa
```

### Important security note

Classic tripcodes are not strong authentication. They are identity-flavored pseudonyms.

They answer:

> “Is this probably the same poster as before?”

They do **not** fully answer:

> “Is this securely authenticated user X?”

### Identity options

#### Option A: Classic insecure tripcodes

Hash the secret directly and display a shortened hash.

Pros:

* Simple
* Nostalgic
* Easy to explain

Cons:

* Brute-forceable
* Weak secrets are easy to guess
* Not suitable for privileged actions

Use for:

* Public display identity only

Do not use for:

* Admin powers
* File permissions
* Moderation powers

---

#### Option B: Server-salted tripcodes

Tripcode hash uses a server-side secret/salt:

```text
tripcode = HMAC(server_secret, user_secret)
```

Pros:

* Much harder to precompute/brute force externally
* Still no account DB
* Better than classic tripcodes

Cons:

* If server secret changes, tripcodes change
* Server compromise exposes ability to verify guesses
* Still not a full account system

Recommended for MVP.

---

#### Option C: Password-derived identity keys

User secret derives a local keypair. The public key becomes identity.

Pros:

* Stronger identity model
* No server-side account DB needed
* Could support signed messages

Cons:

* More complex
* Harder UX
* More crypto risk
* Probably too much for MVP

Good future direction.

---

### Recommended identity model for MVP

Use:

* Server password for access
* Display name chosen per session
* Tripcode generated from user secret using HMAC with server-side secret
* No user table
* No passwords stored per user

Example internal formula:

```text
tripcode = base32(HMAC-SHA256(server_tripcode_secret, user_trip_secret))[0:10]
```

Admin/sysop privileges should **not** be based only on tripcodes. Use a separate sysop config file or admin token.

---

## 4.3 Server Password / Access Control

Servers are passworded.

### Option A: Shared server password

Everyone uses the same invite password.

Pros:

* Simple
* No user account storage
* Easy to rotate
* Fits private BBS culture

Cons:

* Password can leak
* No per-user revocation
* Hard to ban one person without rotating everyone

Good MVP choice.

---

### Option B: Multiple invite codes

Server has a list of invite/access codes.

Pros:

* Can revoke individual codes
* Still no user accounts
* Can see which invite bucket got abused

Cons:

* More state
* More admin UI
* Slightly closer to account management

Good v2 choice.

---

### Option C: Public read, password write

Anyone can connect/read, but posting requires the password.

Pros:

* Good for public archive servers
* Easy discovery

Cons:

* Less private
* More moderation exposure

Not ideal for initial private hangout server.

---

### Recommended access control for MVP

Use a single shared server password, stored as a password hash in config.

Later add invite codes.

---

## 4.4 Live Chat

Feature:

* Users online now can chat with each other
* Chat is ephemeral by default
* Minimal/no persistent storage

### Design options

#### Option A: Pure ephemeral broadcast

Server keeps chat messages only in memory long enough to broadcast to current sessions.

Pros:

* Privacy-first
* Simple
* No chat database
* Good “IRC-ish” feeling

Cons:

* Users joining late see nothing
* No scrollback after reconnect
* Moderation/debugging harder

Recommended MVP.

---

#### Option B: Short rolling scrollback

Keep last N messages in memory only.

Pros:

* Better UX
* New joiners get context
* Still no permanent DB storage

Cons:

* Not truly zero-retention
* Need clear sysop policy

Good MVP if disclosed clearly.

---

#### Option C: Persisted chat history

Store chat history in DB.

Pros:

* Searchable
* Familiar Discord-like behavior

Cons:

* Conflicts with privacy-first vibe
* More moderation/storage burden
* More sensitive data

Not recommended for live chat.

---

### Recommended live chat design

Use ephemeral live chat with optional in-memory rolling scrollback configurable by sysop.

Example config:

```toml
[live_chat]
scrollback_messages = 50
persist_to_disk = false
```

---

## 4.5 Forum / Threads

Feature:

* Persistent forum-like posts
* Slack/Discord-style channels or boards
* Threads and replies

Unlike live chat, forum data is intentionally persisted.

### Basic data model

Entities:

* Board / channel
* Thread
* Reply
* Attachment link optional later
* Display name
* Tripcode
* Timestamps
* Moderation state

Example:

```text
Board
  Thread
    Reply
    Reply
    Reply
```

### Storage options

#### Option A: SQLite

Pros:

* Perfect for MVP
* Single-file database
* Easy backups
* Good enough for small communities
* Simple Python integration

Cons:

* Not ideal for huge multi-node deployments
* Need care with concurrent writes

Recommended MVP.

---

#### Option B: Postgres

Pros:

* More scalable
* Better concurrent writes
* Better future multi-user admin tooling

Cons:

* More operational complexity
* Less weekend-project friendly

Good future option.

---

#### Option C: Flat files / Markdown

Pros:

* Very sysop-friendly
* Easy to inspect
* Hacker zine vibes

Cons:

* Harder to query
* Harder concurrent writes
* Harder moderation state

Possible export format, not primary DB.

---

### Recommended forum storage

Use SQLite first.

Design repository interfaces so SQLite can be swapped later.

---

## 4.6 File Hosting

Feature:

* Server hosts files
* Users browse/download via terminal client
* Initial use case: ebook collection

### Key questions

* Are files public to anyone with server password?
* Are uploads allowed, or only sysop-managed files?
* Are files indexed with metadata?
* Are downloads over terminal protocol, HTTPS, or both?
* Are file paths sandboxed safely?

### Option A: Read-only sysop file library

Sysop places files on disk. Server indexes and exposes them.

Pros:

* Safer
* Simple
* Good for ebook collection
* No user upload abuse

Cons:

* Less community-driven

Recommended MVP.

---

### Option B: User uploads enabled

Pros:

* More BBS-like
* Community file drops

Cons:

* Abuse risk
* Malware risk
* Storage risk
* Moderation burden
* Copyright/liability mess

Not recommended until moderation exists.

---

### Recommended file design

MVP:

* Sysop-managed read-only file library
* Files live under a configured root directory
* Server prevents path traversal
* Metadata index stored in SQLite
* Downloads happen over HTTPS endpoint using expiring signed download tokens, or directly through client protocol for small files

Example config:

```toml
[files]
root = "./library"
allow_uploads = false
index_extensions = [".txt", ".pdf", ".epub", ".zip"]
```

---

## 4.7 ANSI Art / Sysop Customization

ANSI art is a core feature.

### Supported art surfaces

* Login banner
* Main menu
* Board headers
* Door/game splash screens
* Error pages
* User join/leave messages
* MOTD
* File library screens

### Art storage options

#### Option A: Static `.ans` files

Pros:

* Real ANSI workflow
* Compatible with PabloDraw/Moebius
* Easy for sysops

Cons:

* Terminal compatibility issues
* Width assumptions

Recommended.

---

#### Option B: Template-driven ANSI screens

ANSI files can include variables:

```text
Welcome to {server_name}
Users online: {online_count}
```

Pros:

* Dynamic and fun
* Sysop-customizable

Cons:

* Need safe templating

Good MVP/v1 feature.

---

### Recommended art system

Use a theme directory:

```text
themes/default/
  login.ans
  motd.ans
  main_menu.ans
  boards.ans
  files.ans
  error.ans
```

Use simple safe templating with a small allowed variable set.

---

## 4.8 Doors / Modules / Games

Feature:

Sysops can add interactive modules.

Examples:

* Games
* Fortune teller
* Zine browser
* Polls
* Tiny roguelike
* MUD room
* ANSI gallery
* Guestbook

### Plugin models

#### Option A: Python module plugins in-process

Plugins are Python files loaded by the server.

Pros:

* Easy
* Fast to develop
* Very flexible

Cons:

* Unsafe if plugins are untrusted
* Plugin can crash server
* Plugin can access filesystem/process unless sandboxed

Good for trusted sysop plugins only.

---

#### Option B: Subprocess doors

Doors are external programs spawned by the server.

Pros:

* More classic BBS feel
* Can write doors in any language
* Easier isolation boundary

Cons:

* Harder terminal/session plumbing
* Need timeouts/resource limits

Good future option.

---

#### Option C: RPC/plugin API

Plugins run as separate services and talk to the BBS over a protocol.

Pros:

* Clean isolation
* Language-agnostic
* Scales well

Cons:

* More architecture than MVP needs

Future option.

---

### Recommended module design

MVP:

* Simple trusted Python plugin interface
* Plugins can register commands/menu entries
* Plugins receive a limited `SessionContext`
* Plugins should use public APIs instead of DB access directly

Future:

* Add subprocess doors for safer/untrusted modules

Example plugin shape:

```python
def register(app):
    app.add_menu_item("fortune", "Read your fortune", run_fortune)

async def run_fortune(session):
    await session.write("The packet remembers you.\n")
```

---

## 4.9 Terminal Client UX

The client is not just a dumb transport. It defines the experience.

### UX modes

#### Mode A: Full-screen TUI

Use Textual, prompt_toolkit, or curses.

Pros:

* Rich UI
* Panels, scrollback, hotkeys
* Feels modern

Cons:

* More complexity
* Terminal compatibility issues
* Tmux weirdness possible

---

#### Mode B: Line-oriented shell

Feels like IRC/MUD/BBS command mode.

Example:

```text
[SIGIL//NODE] /boards
[SIGIL//NODE] /chat
[SIGIL//NODE] /files
```

Pros:

* Simple
* Very tmux-friendly
* Easy MVP
* Easy to script
* Familiar to terminal people

Cons:

* Less visually impressive at first

Recommended MVP.

---

#### Mode C: Hybrid

Line-oriented shell with optional full-screen views for boards/files.

Pros:

* Good balance
* Can evolve gradually

Cons:

* More design decisions

Recommended long-term.

---

### Recommended UX path

Start with line-oriented shell.

Add richer TUI screens later.

Core commands:

```text
/help
/who
/chat
/boards
/board <name>
/thread <id>
/reply <id>
/files
/download <file_id>
/doors
/quit
```

---

## 4.10 Server Architecture

Recommended Python stack:

* FastAPI for HTTP/WebSocket server
* Uvicorn for local/dev serving
* SQLite via SQLAlchemy or plain `sqlite3`/`aiosqlite`
* Pydantic for protocol schemas
* Rich/Textual/prompt_toolkit for terminal client later if desired
* Typer for CLI utilities

### High-level components

```text
Terminal Client
   |
   | WebSocket over TLS
   v
BBS Server
   |
   |-- Session Manager
   |-- Presence Manager
   |-- Live Chat Broker
   |-- Forum Service
   |-- File Library Service
   |-- Theme/ANSI Renderer
   |-- Plugin Manager
   |-- Auth/Access Gate
   |
   v
SQLite + File Library + Theme Directory
```

### Core server modules

```text
bbs/
  server/
    app.py
    config.py
    auth.py
    sessions.py
    presence.py
    protocol.py
    chat.py
    forums.py
    files.py
    ansi.py
    plugins.py
    db.py
  client/
    main.py
    terminal.py
    protocol.py
  plugins/
    fortune.py
  themes/
    default/
  tests/
```

---

## 5. Protocol Design

If using WebSockets, define messages as typed JSON.

### Client to server examples

```json
{ "type": "hello", "server_password": "...", "name": "Kassie", "trip_secret": "..." }
```

```json
{ "type": "chat.send", "body": "anyone alive?" }
```

```json
{ "type": "forum.thread.create", "board": "general", "title": "first post", "body": "hello bbs" }
```

```json
{ "type": "files.list", "path": "/ebooks" }
```

### Server to client examples

```json
{ "type": "session.ready", "display_name": "Kassie", "tripcode": "AB12CD34" }
```

```json
{ "type": "presence.update", "users_online": 4 }
```

```json
{ "type": "chat.message", "from": "Kassie", "tripcode": "AB12CD34", "body": "hi" }
```

```json
{ "type": "error", "code": "not_authorized", "message": "bad server password" }
```

### Protocol design principles

* Every message has a `type`
* Use versioned protocol eventually
* Validate all incoming messages with Pydantic
* Never trust client-provided tripcodes
* Server assigns session identity after auth
* Keep protocol boring and explicit

---

## 6. Database Sketch

SQLite tables:

```sql
boards (
  id INTEGER PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  description TEXT
)

threads (
  id INTEGER PRIMARY KEY,
  board_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  author_name TEXT NOT NULL,
  author_tripcode TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  is_locked INTEGER DEFAULT 0
)

posts (
  id INTEGER PRIMARY KEY,
  thread_id INTEGER NOT NULL,
  author_name TEXT NOT NULL,
  author_tripcode TEXT NOT NULL,
  body TEXT NOT NULL,
  created_at TEXT NOT NULL,
  edited_at TEXT,
  deleted_at TEXT
)

files (
  id INTEGER PRIMARY KEY,
  path TEXT NOT NULL,
  display_name TEXT NOT NULL,
  size_bytes INTEGER NOT NULL,
  mime_type TEXT,
  added_at TEXT NOT NULL
)
```

Possible future tables:

```sql
invite_codes
moderation_actions
plugin_state
server_events
```

---

## 7. Security / Privacy Principles

### Required

* Encrypted transport
* No plaintext deployment mode except local dev
* Password hash, not plaintext server password
* HMAC-based tripcodes using server secret
* No user account DB for MVP
* No persistent live chat logs by default
* Strict file path sandboxing
* Input validation on every protocol message
* Rate limits for chat/posting/login attempts
* Clear sysop config for retention policies

### Avoid

* Rolling your own crypto protocol
* Using tripcodes as admin auth
* Letting users upload files in MVP
* Logging message bodies by accident
* Storing server passwords directly
* Trusting plugin code from random people
* Path traversal bugs in file downloads

### Logging policy

Default logs should avoid content.

Good logs:

```text
session connected
session disconnected
forum post created: id=123 board=general
file downloaded: id=44
```

Risky logs:

```text
chat body: hello here is private stuff
server password attempt: hunter2
trip secret: whatever
```

---

## 8. Deployment Model

### MVP local/private deployment

* One Python server process
* SQLite DB
* Local file library directory
* Reverse proxy provides HTTPS/WSS
* Config file controls server password, theme, files, boards

Example:

```text
Caddy/nginx
   |
   v
FastAPI/Uvicorn app
   |
   |-- SQLite
   |-- ./library
   |-- ./themes
   |-- ./plugins
```

### Recommended production-ish setup

Use Caddy for TLS because it is simple.

```text
bbs.example.net {
  reverse_proxy localhost:8000
}
```

---

## 9. MVP Proposal

### MVP 0: Local toy

Goal: prove the loop.

Features:

* Python server
* Python terminal client
* WebSocket connection
* Shared server password
* Name + trip secret login
* `/who`
* `/chat`
* Ephemeral live chat
* ANSI login banner

### MVP 1: Real private BBS

Add:

* SQLite forums
* Boards, threads, replies
* File library browsing
* Download endpoint
* Config file
* Theme directory
* Basic sysop commands

### MVP 2: Weird BBS platform

Add:

* Plugin/door API
* More ANSI theming
* Invite codes
* Moderation commands
* Search
* Better TUI client
* Optional SSH gateway

---

## 10. Recommended Weekend Build Plan

### Day 1: Server + live chat

Build:

* FastAPI WebSocket endpoint
* Config loading
* Password gate
* Tripcode generation
* Session manager
* Presence manager
* Ephemeral chat broker
* Minimal terminal client

Success criteria:

* Two terminals can connect
* Both authenticate with server password
* Users get display tripcodes
* `/who` shows online users
* `/chat hello` broadcasts to online users

### Day 2: Boards + ANSI + files skeleton

Build:

* SQLite setup
* Boards table
* Threads/replies table
* `/boards`
* `/thread create`
* `/reply`
* ANSI login banner
* File listing from configured directory

Success criteria:

* Users can post persistent threads
* Users can browse files
* Login screen looks cool
* The whole thing feels like the seed of a real BBS

---

## 11. Key Open Questions

### Transport

* Are we committing to WebSocket-first?
* Do we want SSH support later?
* Should the protocol be client-rendered or server-rendered?

### Identity

* Should trip secrets be entered every session?
* Should the client locally remember name/trip secret?
* Should there be stronger identity later via keypairs?

### Privacy

* Should live chat have zero scrollback or in-memory scrollback?
* Should sysops be able to enable persistent chat logs?
* What should the default logging policy be?

### Forums

* Are forums global boards, Discord-style channels, or both?
* Can threads be locked/deleted?
* Are edits allowed?
* Is Markdown allowed?
* Is ANSI allowed in posts?

### Files

* Read-only sysop library only for MVP?
* How are downloads handled in terminal?
* Do we index metadata?
* Do we support search?

### Plugins

* Trusted Python modules only at first?
* Should plugins get their own state storage?
* Should plugins be able to send chat messages?
* Should plugins be allowed to access files?

### Moderation

* How does a sysop kick/ban without user accounts?
* Ban by IP? Tripcode? Invite code? Session?
* Do we want moderation logs?

---

## 12. Recommended Initial Decisions

| Area             | Recommendation                                         |
| ---------------- | ------------------------------------------------------ |
| Transport        | WebSocket over HTTPS                                   |
| Server framework | FastAPI                                                |
| Client           | Python terminal client, line-oriented first            |
| DB               | SQLite                                                 |
| Identity         | Name + HMAC tripcode                                   |
| Access           | Shared server password                                 |
| Chat             | Ephemeral broadcast with optional in-memory scrollback |
| Forums           | Persistent SQLite boards/threads/replies               |
| Files            | Read-only sysop-managed library                        |
| Art              | `.ans` theme directory                                 |
| Plugins          | Trusted Python plugins first                           |
| Deployment       | Caddy/nginx TLS reverse proxy                          |

---

## 13. Philosophy / Non-Goals

### This is not Discord

It should not become a full surveillance-style account platform.

### This is not a SaaS app first

It should feel personal, local, sysop-owned, and weird.

### This is not crypto-auth cosplay

Use boring, known security primitives. The weirdness belongs in the art and community, not in the transport security.

### This is not only nostalgia

The goal is not to recreate BBSes exactly. The goal is to recover the feeling of local digital place, then modernize the parts that need modernizing.

---

## 14. Decision Checklist, in Plain English

This section is the practical choice menu. The goal is not to decide everything forever. The goal is to choose enough defaults that the first version can be built without constantly stopping.

---

## Decision 1: How do users connect to the server?

This is the **transport** decision.

“Transport” means the pipe between the user’s computer and the BBS server.

The big question:

> When someone wants to connect to the BBS, what command or app do they use?

### Option A: SSH-first

Users connect with normal SSH:

```bash
ssh bbs.example.net
```

SSH is the same tool people use to log into remote servers.

#### What this means

The BBS behaves like a remote terminal. The server sends text/ANSI screens directly to the user’s terminal.

#### Pros

* Very terminal-native
* Feels old-school and hackerish
* Encryption is built in
* Users do not need a custom client
* Works nicely with tmux/screen

#### Cons

* Harder to also make a browser client later
* Harder to make a clean app-style protocol
* SSH authentication may clash with the “no accounts, tripcode identity” idea
* More awkward if we want mobile/web clients later

#### Pick this if

You want the purest terminal BBS feeling.

---

### Option B: WebSocket-first

Users run a small BBS client program:

```bash
sigil-node connect bbs.example.net
```

That client connects to the server over a secure WebSocket.

A WebSocket is a long-lived network connection commonly used for live chat, multiplayer games, browser apps, and anything where both sides need to send messages in real time.

#### What this means

The terminal program is the client. The server sends structured messages to the client. The client decides how to show them in the terminal.

#### Pros

* Great for live chat
* Great for presence / “who is online”
* Easy to build in Python with FastAPI
* Easy to test
* Easy to later add a web client
* Clean separation between server and client
* Normal HTTPS/TLS handles encryption

#### Cons

* Users need your custom client
* Less “just SSH into it”
* You have to build the terminal client yourself

#### Pick this if

You want the best long-term architecture while still being terminal-first.

### Recommended choice

**WebSocket-first.**

Reason:

It gives you live chat, terminal clients, future web clients, and a clean protocol without inventing a weird custom network system.

---

## Decision 2: Who draws the terminal UI?

This is the **rendering model** decision.

The question:

> Does the server send already-formatted terminal screens, or does the client render the interface locally?

### Option A: Server-rendered UI

The server sends raw terminal text and ANSI codes.

The client is basically dumb. It just displays whatever the server sends.

#### Pros

* Very BBS-like
* Easier if using SSH
* Sysop can control the full vibe
* Less client logic

#### Cons

* Harder to make multiple clients
* Harder to test
* Harder to build a web client later
* The server has to care about terminal quirks

---

### Option B: Client-rendered UI

The server sends structured events like:

```json
{ "type": "chat.message", "from": "Kassie", "body": "hi" }
```

The client decides how to display it.

#### Pros

* Cleaner architecture
* Easier to test
* Easier to make different clients
* Browser client possible later
* Server stays simpler

#### Cons

* More client code
* Sysop has slightly less total control over presentation
* ANSI art needs to be sent as content rather than being the whole UI

### Recommended choice

**Client-rendered, but with server-provided ANSI art.**

Meaning:

* Server sends messages/data
* Client renders menus/chat/forums
* Server can still send banners, MOTDs, themes, and ANSI art

This is a good compromise.

---

## Decision 3: What kind of terminal client first?

The question:

> Should the first client be a simple command shell or a fancy full-screen terminal app?

### Option A: Line-oriented client

This looks like IRC, MUDs, or a shell.

Example:

```text
/sigil> /who
/sigil> /chat hello everyone
/sigil> /boards
/sigil> /thread 12
```

#### Pros

* Much easier to build
* Great for tmux
* Easy to keep open in the background
* Easy to debug
* Users can copy/paste commands
* Better weekend project scope

#### Cons

* Less visually impressive at first
* Not as cozy as a full-screen app

---

### Option B: Full-screen TUI

A TUI is a “terminal user interface.”

It is still in the terminal, but looks more like an app with panels, boxes, menus, scroll regions, and hotkeys.

Example vibes:

* Midnight Commander
* htop
* lazygit
* old BBS menu screens
* Textual apps

#### Pros

* Looks awesome
* More polished
* Better browsing experience for forums/files

#### Cons

* More complexity
* More terminal compatibility issues
* Harder to build quickly
* Easy to get stuck fiddling with UI instead of making the BBS work

### Recommended choice

**Line-oriented first. Full TUI later.**

Build the real system first. Make it gorgeous after the bones work.

---

## Decision 4: How much live chat history exists?

The question:

> When someone joins the live chat, can they see recent messages from before they joined?

### Option A: Zero scrollback

“Scrollback” means recent chat history.

Zero scrollback means if you were not online when a message happened, you never see it.

#### Pros

* Most private
* Very simple
* Feels like real-time radio/IRC without logs

#### Cons

* Joining chat can feel confusing
* If your client disconnects, messages are gone
* People may constantly ask “what did I miss?”

---

### Option B: In-memory scrollback

The server remembers the last N messages in RAM only.

Example:

```toml
scrollback_messages = 50
```

If the server restarts, they disappear.

#### Pros

* Better user experience
* Still not stored permanently
* New joiners get context
* Good compromise

#### Cons

* Not literally zero-retention
* Need to clearly say it exists

---

### Option C: Saved chat logs

The server stores live chat in the database.

#### Pros

* Searchable
* Persistent
* Discord-like

#### Cons

* Worst privacy tradeoff
* More moderation burden
* Conflicts with the “live room” feeling

### Recommended choice

**In-memory scrollback, default 50 messages, no disk persistence.**

That gives the best vibe/privacy balance.

---

## Decision 5: What is persistent and what is ephemeral?

“Persistent” means stored on disk and available later.

“Ephemeral” means temporary and gone after it is sent or after the server restarts.

### Recommended split

| Feature                |   Persistent? | Why                                                     |
| ---------------------- | ------------: | ------------------------------------------------------- |
| Live chat              |            No | It is the hangout room. Keep it lightweight/private.    |
| Forum threads          |           Yes | Forums are meant to be read later.                      |
| Forum replies          |           Yes | Same reason.                                            |
| Files                  |           Yes | Server library needs to exist on disk.                  |
| ANSI art/themes        |           Yes | Sysop customization.                                    |
| Presence/who is online |            No | Only matters right now.                                 |
| Login attempts         | Maybe minimal | Security needs rate limiting, but avoid sensitive logs. |

### Recommended choice

**Ephemeral chat, persistent forums/files/themes.**

---

## Decision 6: How do identities work?

The question:

> If there are no accounts, how do people have recognizable names?

### Term: tripcode

A tripcode is an old imageboard/BBS-ish identity trick.

User types:

```text
Kassie#secretphrase
```

The server shows something like:

```text
Kassie !A8F92ZQ
```

The visible tripcode proves, sort of, that this is the same person using the same secret.

It is not a full account. It is more like a pseudonymous signature.

---

### Option A: Classic tripcode

Hash the secret directly.

#### Pros

* Easy
* Nostalgic

#### Cons

* Weak against guessing
* Not good security

---

### Option B: Server-secret HMAC tripcode

The server uses its own secret key when creating the tripcode.

In plain English:

> The user has a secret, the server has a secret, and the public tripcode is made from both.

#### Pros

* Better than classic tripcodes
* Still no user account database
* Prevents easy precomputed attacks

#### Cons

* If the server secret changes, tripcodes change
* Still not strong enough for admin powers

### Recommended choice

**Server-secret HMAC tripcodes.**

But important:

Tripcodes are for identity display, not admin security.

---

## Decision 7: How do sysops/admins authenticate?

The question:

> If regular users have no accounts, how does the server know who is allowed to do admin things?

Do **not** use tripcodes alone for admin powers.

### Option A: Admin token in config

Sysop has a separate admin password/token.

#### Pros

* Simple
* No account DB needed
* Good MVP choice

#### Cons

* Anyone with the token is admin
* Token rotation is manual

---

### Option B: Admin public keys

Sysops have cryptographic keypairs. The server trusts listed public keys.

#### Pros

* Stronger
* No password sharing
* Fits hacker aesthetic

#### Cons

* More complex UX
* Not needed immediately

### Recommended choice

**Admin token for MVP. Admin public keys later.**

---

## Decision 8: How does the server password work?

The question:

> How private is the server, and how do people get in?

### Option A: One shared server password

Everyone uses the same password to enter.

#### Pros

* Very simple
* No accounts
* Easy private-club vibe

#### Cons

* If one person leaks it, you rotate it for everyone
* Cannot revoke one person cleanly

---

### Option B: Invite codes

Each user gets an invite/access code.

#### Pros

* Can revoke one code
* Better abuse handling
* Still not exactly accounts

#### Cons

* More implementation
* More state to manage

### Recommended choice

**Shared server password first. Invite codes later.**

---

## Decision 9: Can users upload files?

The question:

> Is the file library just sysop-curated, or can users add files too?

### Option A: Sysop-only file library

Only the server owner adds files.

#### Pros

* Much safer
* Easier to moderate
* Easier to build
* Good for ebook/zine archive use case

#### Cons

* Less community participation

---

### Option B: User uploads

Users can upload files.

#### Pros

* More classic BBS feel
* Community file drops are fun

#### Cons

* Malware risk
* Storage abuse
* Copyright/liability issues
* Need moderation tools
* Need quotas
* Need file scanning or at least careful handling

### Recommended choice

**Sysop-only files for MVP.**

Add uploads only after moderation, quotas, and permissions exist.

---

## Decision 10: How are files downloaded?

The question:

> When a user chooses a file in the terminal client, how does the actual file transfer happen?

### Option A: Download over HTTPS link

The BBS client asks for a file, and the server gives a temporary secure download URL.

#### Pros

* Simple
* Good for large files
* Uses normal web download behavior
* Easier than inventing file transfer

#### Cons

* Slightly less pure terminal vibe
* Need temporary signed links/tokens

---

### Option B: Download through the BBS protocol

The file bytes are streamed through the same WebSocket connection.

#### Pros

* Very integrated
* No separate URL flow

#### Cons

* More complicated
* Bad for large files
* Easy to make janky

### Recommended choice

**HTTPS download links for MVP.**

The terminal client can still make it feel seamless.

---

## Decision 11: Are forum posts Markdown, plain text, or ANSI?

The question:

> What formatting is allowed in persistent posts?

### Option A: Plain text only

#### Pros

* Safest
* Simplest
* Terminal-friendly

#### Cons

* Less expressive

---

### Option B: Markdown-ish text

Allow simple Markdown:

```text
**bold**
`code`
> quote
```

#### Pros

* Familiar
* Good for technical discussion
* Easy to render in terminal and maybe web later

#### Cons

* Need parser/rendering rules

---

### Option C: ANSI allowed in posts

Users can put color/control codes in posts.

#### Pros

* Maximum chaos art
* Very BBS

#### Cons

* Can be abused
* Can mess up terminals
* Needs sanitization

### Recommended choice

**Plain text or limited Markdown for posts. ANSI reserved for sysop-controlled art at first.**

---

## Decision 12: How customizable are themes?

The question:

> How much can the sysop change the look and feel without editing code?

### Recommended MVP theme system

Use a theme folder:

```text
themes/default/
  login.ans
  motd.ans
  main_menu.ans
  boards.ans
  files.ans
```

Allow simple variables:

```text
Welcome to {server_name}
Users online: {online_count}
```

### Recommended choice

**Theme folder with `.ans` files and a small safe variable system.**

---

## Decision 13: How do plugins/doors work?

The question:

> How can sysops add games and weird modules?

### Term: door

A “door” is old BBS language for an external game or program launched from the BBS.

Examples:

* Trivia game
* Tiny roguelike
* Fortune teller
* Zine browser
* MUD-like room
* High-score game

---

### Option A: Trusted Python plugins

Plugins are Python files loaded by the server.

#### Pros

* Easy to build
* Great for weekend hacking
* Flexible

#### Cons

* Not safe for untrusted plugins
* Plugin bugs can crash things
* Plugin code can access too much unless carefully designed

---

### Option B: Subprocess doors

The server launches separate programs.

#### Pros

* More like classic BBS doors
* Can use any language
* Better isolation boundary

#### Cons

* More complicated input/output handling
* Need timeouts and resource controls

### Recommended choice

**Trusted Python plugins for v1. Subprocess doors later.**

---

## Decision 14: What database?

The question:

> Where do persistent forum posts, file metadata, and settings live?

### Option A: SQLite

SQLite is a small database stored in one file.

#### Pros

* Perfect for small servers
* Very easy to run
* No separate database server
* Great for a weekend project

#### Cons

* Not ideal for huge deployments
* Need some care with concurrent writes

---

### Option B: Postgres

Postgres is a full database server.

#### Pros

* More powerful
* Better for larger systems
* Better concurrency

#### Cons

* More setup
* Overkill for MVP

### Recommended choice

**SQLite.**

---

## Decision 15: What does moderation mean without accounts?

The question:

> If someone is being annoying, how does the sysop stop them?

This is tricky because no accounts means no clean per-user identity.

Possible moderation handles:

| Handle          | Meaning                  | Weakness                                   |
| --------------- | ------------------------ | ------------------------------------------ |
| Session         | Kick current connection  | They can reconnect                         |
| Tripcode        | Ban a displayed tripcode | They can change secret                     |
| IP address      | Ban network address      | Can be shared or changed                   |
| Invite code     | Revoke access code       | Requires invite-code system                |
| Server password | Rotate password          | Kicks everyone until they get new password |

### Recommended MVP

* Kick session
* Ban tripcode temporarily
* Ban IP temporarily if needed
* Rotate server password manually for serious problems

### Recommended v2

* Invite codes
* Revoke invite code
* Optional stronger identities

---

## Decision 16: What should be logged?

The question:

> What does the server record for debugging/security?

### Recommended default

Log events, not private content.

Good:

```text
user connected
user disconnected
forum post created id=123
file downloaded id=44
bad password attempt from ip hash
```

Avoid:

```text
chat message body
trip secret
server password
private message body
full IP forever
```

### Recommended choice

**Minimal structured logs, no chat bodies, no secrets.**

---

## Decision 17: What is the first actual build target?

The question:

> What should exist first so the project feels real?

### Recommended first milestone

Build a server and terminal client where two people can:

1. Connect securely
2. Enter server password
3. Choose name + trip secret
4. See ANSI welcome banner
5. Run `/who`
6. Send live chat messages
7. Disconnect/reconnect

That is the “it lives” moment.

### Recommended second milestone

Add:

1. Boards
2. Threads
3. Replies
4. File listing
5. Download links
6. Theme folder

---

## 15. Recommended Answers, No Debate Mode

If we just want to pick sane defaults and start building:

| Decision          | Pick                                                            |
| ----------------- | --------------------------------------------------------------- |
| Connection method | WebSocket-first                                                 |
| UI rendering      | Client-rendered with server-provided ANSI art                   |
| First client      | Line-oriented terminal client                                   |
| Chat history      | 50-message in-memory scrollback                                 |
| Persistent data   | Forums, files, themes                                           |
| Ephemeral data    | Live chat, presence                                             |
| Identity          | Name + server-secret HMAC tripcode                              |
| Admin auth        | Separate admin token                                            |
| Server access     | Shared password                                                 |
| File uploads      | No user uploads yet                                             |
| File downloads    | HTTPS download links                                            |
| Forum formatting  | Plain text or limited Markdown                                  |
| Themes            | `.ans` files in theme directory                                 |
| Plugins           | Trusted Python plugins                                          |
| Database          | SQLite                                                          |
| Moderation        | Kick session, temporary trip/IP bans, rotate password if needed |
| Logging           | Minimal event logs, no chat bodies/secrets                      |

## 16. The Short Version for Autumn

We are building a private terminal BBS.

Users run a terminal client that connects securely to a Python server. They enter the server password, choose a name, and use a secret phrase to generate a tripcode identity. Live chat is temporary and mostly private. Forum posts are saved. Files are hosted by the sysop. The server can show ANSI art and eventually run plugin games called doors.

For the first version, we should build the boring solid path:

* Python
* FastAPI
* WebSockets
* SQLite
* Terminal client
* Shared server password
* Tripcodes
* Ephemeral chat
* Persistent forums
* Read-only files
* ANSI themes

Then once it works, we make it cursed and beautiful.
