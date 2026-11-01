# MCP Protocol Studio

Enterprise-grade MCP (Model Context Protocol) Registry & Management Studio.
Built with Vue 3, Vite, PrimeVue, and Tailwind CSS. Backed by FastAPI MCP Server.

## Features

- **MCP Private Registry**: Explore, search, and manage in-house, custom, and Git-sourced MCP servers.
- **Git & Package Import**: Direct import from GitHub/GitLab repositories or `.zip`/`.tar.gz` packages.
- **Live MCP Tool Testing**: Interactive schema inspector and live tool runner with dynamic JSON argument generation.
- **Client Integration Snippets**: Ready-to-copy configurations for Claude Desktop (`claude_desktop_config.json`), Cursor, Windsurf, and custom AI clients.
- **Desktop Shell**: High-performance WinForms/WebView2 container with system tray, autostart, and single-instance coordination.

## Development

```bash
# Install dependencies
npm install

# Run Vite dev server
npm run dev

# Run unit tests
npm test

# Production build
npm run build
```

## Architecture

- **Frontend**: Vite + Vue 3 (Composition API) + Pinia + PrimeVue (`src/`)
- **Backend**: FastAPI MCP Server + Dynamic Tool Registry (`../app.py`)
- **Desktop Shell**: Python Win32/WinForms WebView2 container (`desktop/`)
