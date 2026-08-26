# Web Refactoring Status

The web application is integrated with the public `agent.Orchestrator` API.
Reusable chat models, formatters, templates, and streaming logging utilities
are separated from the HTTP server. `web/server.py` is 591 lines, down from the
original 1,395-line implementation.

The server supports regular JSON responses and Server-Sent Events, passes
progress callbacks into the orchestrator, and obtains host and port defaults
from centralized settings.

The remaining HTTP request methods are intentionally kept together in
`StockChatHandler`; splitting them further is optional and is not required for
the agent architecture migration.

Last updated: 2026-08-25
