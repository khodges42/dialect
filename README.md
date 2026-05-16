# SIGIL//NODE

A free, GPLv3, terminal-first BBS for artistic weirdos, hackers, and people who think the internet got worse when everything became five websites in a trenchcoat.

SIGIL//NODE is a modern BBS system with old-school soul: live chat, forum threads, ANSI art, file libraries, and modular doors/games, built for small communities that want their own weird little digital place.

## Goals

* Terminal-first social space
* Encrypted traffic by default
* Passworded private servers
* Tripcode-style pseudonymous users
* Ephemeral live chat
* Persistent forum threads and replies
* Sysop-hosted file libraries
* ANSI art and custom themes
* Modular doors, games, and weird extensions
* Simple enough to self-host
* Free software, forever

## What It Is

SIGIL//NODE is not trying to be Discord, Slack, Reddit, or a SaaS platform.

It is a small, self-hosted community node where people can hang out from a terminal, post threads, share files, run weird little programs, and decorate the place like it is a scene hangout from 1996.

## Planned Stack

Initial prototype:

* Python
* FastAPI
* WebSockets
* SQLite
* Terminal client
* ANSI theme files
* Trusted Python plugins

Possible future:

* Rust core
* Python extension layer
* SSH gateway
* Subprocess-style BBS doors
* Stronger key-based identities

## Core Features

### Live Chat

A real-time hangout room for whoever is online right now. Chat is ephemeral by default, with optional in-memory scrollback.

### Forums

Persistent boards, threads, and replies for slower conversations, project logs, zines, arguments, manifestos, and lore dumps.

### File Library

Sysop-managed file hosting for ebooks, zines, ANSI packs, music, game files, documents, and other curated treasures.

### ANSI Art

Servers can define their own login screens, menus, banners, error pages, and general visual identity using ANSI art.

### Doors and Modules

Sysops can add games, tools, bots, rituals, fortune tellers, tiny roguelikes, or whatever cursed thing belongs on their node.

## Identity Model

Users do not need traditional accounts.

Instead, users choose a display name and secret phrase. The server uses that secret to generate a tripcode-style identity marker.

Example:

```text
Kassie !A8F92ZQ
```

Tripcodes are for recognizable pseudonymous identity, not high-security authentication.

## Privacy Direction

SIGIL//NODE should store as little as possible by default.

* Live chat is not permanently logged by default
* Forum posts are intentionally persistent
* File libraries are intentionally persistent
* Secrets should never be logged
* Server passwords should be stored hashed
* Admin powers should not rely on tripcodes alone

## License

SIGIL//NODE is free software licensed under the GNU General Public License v3.0 or later.

You are free to run it, study it, modify it, and share it under the terms of the GPLv3.

## Project Vibe

Personal computing should feel personal again.

Bring back weird servers.
Bring back sysops.
Bring back ANSI art.
Bring back small communities.

This lambda ain’t nothing to me, man.
