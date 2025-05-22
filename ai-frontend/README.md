# AI Frontend

This folder contains a simple React + Tailwind application scaffolded to match provided UI mockups.

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

Tailwind is configured via `tailwind.config.js` and `postcss.config.js`. Styles are imported in `src/input.css` and compiled to `dist/output.css`.

The main React entry is `src/main.jsx`. Components reside in `src/components`:
- `Chat.jsx` – main chat window
- `Documents.jsx` – file uploads and listing
- `Settings.jsx` – configuration form
- `Sidebar.jsx` – navigation between sections

The layout and styling should be adjusted to match the provided JPEG mockups.
\n## Backend Integration\n\nThe chat messages should be sent to your backend API for processing (e.g., Python service with Pinecone indexing). Use `fetch` or Axios in the React components to communicate with endpoints for chat, file upload, and settings storage.
