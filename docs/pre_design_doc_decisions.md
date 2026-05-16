## 4.1 Transport / Protocol

### Option B: WebSocket API over HTTPS
    fine with file downloads being https, use server invite as access cookie

## 4.2 Identity Model
### Option B: Server-secret HMAC tripcode

    admins have a pub/private key and accounts work like that too.
    maybe users can have pub/private too if they want? that way users can be anonymous or set up permanent access

## 4.3
### Option B: Multiple invite codes
    Discord style
    Can be used to access endpoints
    Once user connects, stores this in their .dialect file for future access along with their username and such.

## 4.4 Live Chat
### Option A
    Show users online, thats it. No old chat.


## 4.5 Forum / Threads
#### Option A: SQLite

## 4.6 File Hosting
### Option A: Read-only sysop file library
* Sysop-managed read-only file library
* Files live under a configured root directory
* Server prevents path traversal
* Metadata index stored in SQLite
* Downloads happen over HTTPS endpoint using expiring signed download tokens, or directly through client protocol for small files


## 4.7 ANSI Art / Sysop Customization
#### Option B: Template-driven ANSI screens



## 4.8 Doors / Modules / Games
#### Option A: Python module plugins in-process
    * Low tech and risky but probably fine for this for now.

## 4.9 Terminal Client UX
#### Mode C: Hybrid


## 4.10 Server Architecture
* FastAPI for HTTP/WebSocket server
* Uvicorn for local/dev serving
* SQLite via SQLAlchemy or plain `sqlite3`/`aiosqlite`
* Pydantic for protocol schemas
* Rich/Textual/prompt_toolkit for terminal client later if desired
* Typer for CLI utilities



