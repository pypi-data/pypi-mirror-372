# Aiden Mail MCP

![PyPI - Version](https://img.shields.io/pypi/v/aiden-mail)

Aiden Mail MCP is a simple and powerful email MCP server based on IMAP and SMTP protocols. It provides a unified interface for managing your emails across multiple providers.

## Features

- ✅ **Email Listing**: View emails in your inbox and other folders
- ✅ **Email Search**: Search emails by keyword, sender, recipient, or subject
- ✅ **Email Deletion**: Delete specific emails
- ✅ **Email Sending**: Send emails easily
- ✅ **Email Management**: Move emails between folders, mark as read/unread
- ✅ **Multi-Provider Support**: Currently supports Gmail, iCloud, QQ and 163 Mail

## Installation

This MCP server is designed for use with [AidenChat](https://aidenai.io/).

```json
"aiden-mail": {
    "command": "uvx",
    "args": [
        "aiden-mail"
    ],
    "transport": "stdio",
    "aiden_credential": {
        "type": "password",
        "providers": ["Gmail", "iCloud", "QQ", "163"]
    }
}
```
