# Drawer
_updated: 2026-07-15 | relates: [[wikilink-navigation]], [[settings-in-drawer]]_

**File(s):** `frontend/src/lib/components/drawer/Drawer.svelte`, `frontend/src/lib/components/drawer/Breadcrumb.svelte`, `frontend/src/lib/components/drawer/SettingsPanel.svelte`, `frontend/src/lib/stores/drawer.svelte.ts`
**Role:** Slide-in right panel (~480px) that renders either a record (`PageView`) or the settings panel (`SettingsPanel`), controlled by `drawerStore`.

**Non-obvious:**
- **Two modes:** `drawerStore.mode` is `'record' | 'settings'`. Record mode shows `PageView` + breadcrumb nav; settings mode shows `SettingsPanel` + a static "Settings" label. Switching modes clears the active record and breadcrumb stack.
- **`<Drawer />` is mounted outside `.app-shell`** in `+layout.svelte` (after the closing `</div>`). CSS properties set on `.app-shell` — including `font-family` — do not cascade into the drawer. Any inherited styles needed in the drawer must be set explicitly on `.drawer` itself.
- **Backdrop + Escape:** Clicking the backdrop or pressing Escape calls `drawerStore.close()`, which resets both mode and record.
- **Live record sync:** In record mode the drawer derives `liveRecord` from `recordsStore` (same vault+folder) rather than the snapshot stored in `drawerStore`. This means SSE-triggered record updates appear in the open drawer without a re-open.
- **Schema lazy-load:** Folder schema is fetched once per folder path and cached in `loadedFolder`. A folder change triggers a fresh `getFolderSchema()` call.
- **Settings button toggle:** The header Settings `<button>` calls `drawerStore.openSettings()` on first click; if the settings drawer is already open, it calls `drawerStore.close()` instead, acting as a toggle.
