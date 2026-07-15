# Settings in Drawer (not a page route)
_updated: 2026-07-15 | relates: [[drawer]]_

**Decision:** Settings live in the shared drawer panel, not at a dedicated `/settings` route.
**Why:** A drawer opens over the current view — the user stays in context (table, record, etc.) while adjusting preferences. A separate route would navigate away, clearing the active table selection and losing scroll position. The drawer is already the pattern for contextual side-panels (record view); Settings follows the same shell.
**Consequence:** The `drawerStore` must support multiple modes (`'record' | 'settings'`). The `<Drawer />` component conditionally renders `PageView` or `SettingsPanel` based on `drawerStore.mode`. There is no `/settings` URL — deep-linking to settings is not supported. The header Settings element is a `<button>` (not `<a>`) that toggles the drawer.
