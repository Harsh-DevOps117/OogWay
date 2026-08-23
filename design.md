# Design Principles - The Lenny Growth Assistant

While this engagement focuses primarily on the backend systems, the following design principles should guide the frontend team constructing the Artifact Viewer and Chat Interface.

## 1. UI/UX Principles
- **Minimalist & Focused**: The chat interface should mirror the simplicity of modern LLM interfaces (like Claude or ChatGPT), keeping the focus entirely on the content.
- **Side-by-Side Artifacts**: When the backend returns an `<artifact>` block, the UI should immediately split into a two-pane layout. The chat remains on the left, and the rendered artifact (Markdown or HTML) appears on the right.
- **Explicit Citations**: The backend provides citation metadata. The UI must render these citations visibly so users trust the grounded response.

## 2. Information Architecture
- **Sidebar**: List of previous chat sessions organized by date.
- **Main View**: 
  - If no artifact is present: Centered, single-column chat.
  - If artifact is present: 40/60 split (Chat on left, Viewer on right).

## 3. Interaction States
- **Loading**: Crucial for Local LLM (Ollama) testing. The UI must show a clear, animated loading state since inference may take up to 15 seconds.
- **Error Handling**: Display clear, human-readable error messages if the API returns a 500 or if the database connection fails.

## 4. Security & Artifact Rendering
- **Sanitization**: Any HTML returned in the `artifacts` field of the API MUST be sanitized using a robust library (e.g., DOMPurify) before being rendered. `<iframe>` sandboxing is recommended for raw HTML/CSS output to prevent XSS attacks against the internal network.
