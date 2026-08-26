# Web Refactoring Complete

The original 1,395-line web server has been reduced to a 591-line HTTP and SSE
integration layer. Chat models, NLP processing, response formatters, the HTML
template, and streaming logging live in focused modules under `web/`.

The server now constructs `agent.Orchestrator.from_settings()` and calls its
provider-neutral `run()` API for both regular and streaming requests.

See [web/REFACTORING_PROGRESS.md](web/REFACTORING_PROGRESS.md) for the current
structure and maintenance notes.

Last updated: 2026-08-25
