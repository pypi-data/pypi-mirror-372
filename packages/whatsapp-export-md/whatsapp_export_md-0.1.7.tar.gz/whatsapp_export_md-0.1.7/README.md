# whatsapp-export-md

Convert exported WhatsApp chats (Android/iOS) into **Markdown** or **HTML**, with proper handling of **media**:
- Recognizes `<attached: FILENAME>` and bare filenames
- Links media with **relative paths** or **embeds** via Base64 (`--embed`)
- Supports images, audio (incl. `.opus`), video, and PDFs
- Robust parsing of timestamps and multi‑line messages
- Optional JSON dump of parsed messages for further analysis

> Privacy-friendly: runs **completely locally** on your machine.

## Install

```bash
pip install whatsapp-export-md
```

> Requires Python 3.9+

## Quick start

```bash
# HTML with embedded media (up to 8 MB each)
whatsapp-export-md   --input "/Exports/Family Chat.txt"   --media-dir "/Exports/Family Chat"   --out "/Exports/family_chat.html"   --format html --embed --embed-max-mb 8

# Markdown without media embedding
whatsapp-export-md   --input "/Exports/Project Team.txt"   --out "project_team.md"   --format md --title "Project Team"
```

Recommended folder layout:
```
/Exports/
  Chat.txt
  Chat/                 # WhatsApp-created media folder for that chat
    IMG-....jpg
    VID-....mp4
    00001234-AUDIO....opus
  chat.html             # save your output here
```

## Features

- Android/iOS export formats, system messages
- Per‑day grouping and clean HTML layout
- Linkify plain `http(s)://` URLs
- Smart filename resolution:
  - case‑insensitive
  - ignores brackets `(1)` and spacing/underscore/dash differences
- Correct MIME mapping for `.opus`, `.m4a`, `.pdf`

## CLI

```
usage: whatsapp-export-md --input INPUT --out OUT [--format {md,html}] [--media-dir DIR]
                          [--embed] [--embed-max-mb N] [--tz ZONE] [--title TITLE] [--json PATH]

Options:
  --input PATH          Exported WhatsApp .txt file
  --out PATH            Output file (.md or .html)
  --format md|html      Output format (default: md)
  --media-dir DIR       Path to the exported media folder (optional)
  --embed               Inline media as Base64 data URIs (HTML only)
  --embed-max-mb N      Max per-file embed size in MB (default: 8)
  --tz ZONE             Display timezone (default: Asia/Kolkata)
  --title TITLE         Document title
  --json PATH           Also dump parsed JSON
```

## Tips

- For large videos, consider not embedding (`--embed` off) to keep HTML size small.
- PDFs are shown via `<embed>` when embedded, otherwise linked.
- If you see a note like “Could not resolve these media tokens”, confirm that the files exist in `--media-dir`.
  The resolver handles common renames (e.g., `file.pdf` vs `file (1).pdf`).

## Development

```bash
git clone https://github.com/mshammas/whatsapp-export-md
cd whatsapp-export-md
pip install -e ".[test]"
```

## License

MIT © Mohammed Shammas
