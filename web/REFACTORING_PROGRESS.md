# Web Refactoring Status

The web application is integrated with the public `agent.Orchestrator` API.
Reusable chat models, formatters, templates, and streaming logging utilities
are separated from the HTTP server. Ordinary and streaming chat share one message-processing method, and unused
parallel analysis handlers have been removed.

The server supports regular JSON responses and Server-Sent Events, passes
progress callbacks into the orchestrator, and obtains host and port defaults
from centralized settings.

The remaining HTTP request methods are intentionally kept together in
`StockChatHandler`; splitting them further is optional and is not required for
the agent architecture migration.

Last updated: 2026-09-13
