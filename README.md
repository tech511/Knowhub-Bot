# KnowHub Bot

A lightweight Telegram knowledge library for communities, built with Python, Aiogram 3, MongoDB Atlas, and Render background workers.

## Features in this starter release

- Personal saved entries and group-scoped shared entries
- Save text and URLs
- Search titles, content, and tags
- Categories and paginated results
- Edit/delete your own entries
- Group administrator moderation and category listing
- Basic statistics and access checks
- MongoDB persistence and indexes

## Important behavior

- In private chat, entries belong to the user.
- In a group, `/save` creates a shared entry for that group.
- Group members can search and view group entries.
- Only the creator or a Telegram group admin can edit/delete a shared entry.
- `/approve` and `/reject` are group-admin-only moderation commands for pending entries.
- `/settings` shows the current group library mode; this starter uses admin approval for group submissions.
- This bot does not download or host media.

## Setup locally

1. Install Python 3.11+.
2. Create a virtual environment.
3. Run `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and fill in your values.
5. Export the variables in your shell, or use a local dotenv runner. The bot does not automatically load `.env` so production secrets remain explicit; to load it locally, add `from dotenv import load_dotenv; load_dotenv()` at the top of `bot.py`.
6. Run `python bot.py`.

## MongoDB Atlas

Create a database user, allow your host in Network Access (for Render, configure an appropriate access rule), and copy the driver connection string into `DATABASE_URL`. Keep the password URL-encoded if it contains special characters.

## Deploy to Render

Push this folder to GitHub, create a Background Worker, set the start command to `python bot.py`, and add `BOT_TOKEN`, `DATABASE_URL`, `DATABASE_NAME`, and `OWNER_ID` in Render environment variables. `render.yaml` is included as a starting blueprint.

## Commands

- `/start`, `/help`
- `/save` — guided save flow; in groups it creates a pending entry
- `/search <keyword>`
- `/categories`
- `/myentries`
- `/edit <entry_id>` — then send updated title and content on separate lines
- `/delete <entry_id>`
- `/stats`
- `/settings`
- `/approve <entry_id>` and `/reject <entry_id>` — group admins only

## Notes

- Telegram privacy mode can affect which ordinary group messages the bot receives. Commands and explicit bot interactions are the safest workflow.
- Add the bot to a group and grant administrator status if you want it to verify admin privileges reliably.
- This is a functional starter project, not a security audit. Test with a private test group before public release.
