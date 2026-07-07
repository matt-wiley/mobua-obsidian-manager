<script lang="ts">
	import type { VaultRecord, RecordUpdate } from '$lib/api/records';
	import type { SchemaField, View } from '$lib/api/folders';
	import { setColWidth, getViews, createView, deleteView } from '$lib/api/folders';
	import { recordsStore } from '$lib/stores/records.svelte';
	import TableCell from './TableCell.svelte';
	import ColumnHeader from './ColumnHeader.svelte';

	let {
		records,
		schema,
		vault,
		folder,
		colWidths = {},
		quickSearch = ''
	}: {
		records: VaultRecord[];
		schema: SchemaField[];
		vault: string;
		folder: string;
		colWidths?: Record<string, number>;
		quickSearch?: string;
	} = $props();

	// --- Column sizing -------------------------------------------------------

	let sizing = $state<Record<string, number>>({ ...colWidths });

	function colW(id: string, def: number): number {
		return sizing[id] ?? def;
	}

	let saveTimer: ReturnType<typeof setTimeout> | null = null;
	function scheduleSave() {
		if (saveTimer) clearTimeout(saveTimer);
		saveTimer = setTimeout(() => {
			for (const [field, width] of Object.entries(sizing)) {
				setColWidth(vault, folder, field, width);
			}
		}, 500);
	}

	function resizeHandler(colId: string, defaultW: number) {
		return (e: MouseEvent | TouchEvent) => {
			e.preventDefault();
			const startX = e instanceof MouseEvent ? e.clientX : e.touches[0].clientX;
			const startW = sizing[colId] ?? defaultW;

			function onMove(ev: MouseEvent) {
				sizing[colId] = Math.max(20, startW + (ev.clientX - startX));
			}

			function onUp() {
				document.removeEventListener('mousemove', onMove);
				document.removeEventListener('mouseup', onUp);
				scheduleSave();
			}
			document.addEventListener('mousemove', onMove);
			document.addEventListener('mouseup', onUp);
		};
	}

	// --- Column list ---------------------------------------------------------

	type Col = { id: string; label: string; defaultW: number; isFilename: boolean };

	const baseCols = $derived<Col[]>([
		{ id: 'filename', label: 'Name', defaultW: 220, isFilename: true },
		...schema.map((f) => ({
			id: f.field_name,
			label: f.field_name,
			defaultW: 160,
			isFilename: false
		}))
	]);

	// --- Column ordering (persisted in localStorage) -------------------------

	const orderKey = `col-order:${folder}`;

	function loadOrder(cols: Col[]): string[] {
		try {
			const stored = localStorage.getItem(orderKey);
			if (stored) {
				const parsed: string[] = JSON.parse(stored);
				// Keep only IDs that still exist, then append any new ones
				const valid = parsed.filter((id) => cols.some((c) => c.id === id));
				const added = cols.filter((c) => !valid.includes(c.id)).map((c) => c.id);
				return [...valid, ...added];
			}
		} catch {
			// ignore
		}
		return cols.map((c) => c.id);
	}

	let colOrder = $state<string[]>([]);

	$effect(() => {
		colOrder = loadOrder(baseCols);
	});

	const allCols = $derived<Col[]>(
		colOrder
			.map((id) => baseCols.find((c) => c.id === id))
			.filter((c): c is Col => c !== undefined)
	);

	function saveOrder() {
		localStorage.setItem(orderKey, JSON.stringify(colOrder));
	}

	function resetOrder() {
		localStorage.removeItem(orderKey);
		colOrder = baseCols.map((c) => c.id);
		activeViewId = null;
	}

	const isReordered = $derived(
		colOrder.some((id, i) => baseCols[i]?.id !== id)
	);

	// --- Drag-to-reorder -----------------------------------------------------

	let dragId = $state<string | null>(null);
	let dropTargetId = $state<string | null>(null);
	let dropSide = $state<'left' | 'right'>('right');

	function onDragStart(e: DragEvent, colId: string) {
		dragId = colId;
		e.dataTransfer!.effectAllowed = 'move';
		e.dataTransfer!.setData('text/plain', colId);
	}

	function onDragOver(e: DragEvent, colId: string) {
		if (!dragId || dragId === colId) return;
		e.preventDefault();
		e.dataTransfer!.dropEffect = 'move';
		const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
		dropSide = e.clientX < rect.left + rect.width / 2 ? 'left' : 'right';
		dropTargetId = colId;
	}

	function onDragLeave(e: DragEvent) {
		// Only clear if leaving the th entirely (not moving to a child)
		if (!(e.currentTarget as HTMLElement).contains(e.relatedTarget as Node)) {
			dropTargetId = null;
		}
	}

	function onDrop(e: DragEvent, targetId: string) {
		e.preventDefault();
		if (!dragId || dragId === targetId) { dropTargetId = null; return; }

		const order = [...colOrder];
		const fromIdx = order.indexOf(dragId);
		const toIdx = order.indexOf(targetId);
		if (fromIdx === -1 || toIdx === -1) { dropTargetId = null; return; }

		order.splice(fromIdx, 1);
		const insertAt = dropSide === 'left' ? order.indexOf(targetId) : order.indexOf(targetId) + 1;
		order.splice(insertAt, 0, dragId);

		colOrder = order;
		saveOrder();
		activeViewId = null;
		dragId = null;
		dropTargetId = null;
	}

	function onDragEnd() {
		dragId = null;
		dropTargetId = null;
	}

	const fieldMap = $derived(Object.fromEntries(schema.map((f) => [f.field_name, f])));

	// --- Column visibility (persisted in localStorage) ----------------------

	const hiddenKey = `col-hidden:${folder}`;

	function loadHidden(): Set<string> {
		try {
			const stored = localStorage.getItem(hiddenKey);
			if (stored) return new Set(JSON.parse(stored));
		} catch { /* ignore */ }
		return new Set();
	}

	let hiddenCols = $state<Set<string>>(loadHidden());

	function saveHidden() {
		localStorage.setItem(hiddenKey, JSON.stringify([...hiddenCols]));
	}

	function toggleColumn(colId: string) {
		const next = new Set(hiddenCols);
		if (next.has(colId)) {
			next.delete(colId);
		} else {
			next.add(colId);
			sortCriteria = sortCriteria.filter((s) => s.id !== colId);
			saveSortCriteria();
		}
		hiddenCols = next;
		saveHidden();
		activeViewId = null;
	}

	const visibleCols = $derived(allCols.filter((c) => !hiddenCols.has(c.id)));

	let showColPanel = $state(false);

	// --- Row filtering (persisted in localStorage) --------------------------

	type FilterOp =
		| 'contains' | 'not_contains'
		| 'is_empty' | 'is_not_empty'
		| 'eq' | 'lt' | 'lte' | 'gt' | 'gte'
		| 'on' | 'before' | 'after';

	type FilterCriterion = { field: string; op: FilterOp; value: string };

	const TEXT_OPS: { value: FilterOp; label: string }[] = [
		{ value: 'contains',     label: 'contains' },
		{ value: 'not_contains', label: 'does not contain' },
		{ value: 'is_empty',     label: 'is empty' },
		{ value: 'is_not_empty', label: 'is not empty' },
	];
	const NUMBER_OPS: { value: FilterOp; label: string }[] = [
		{ value: 'eq',           label: '=' },
		{ value: 'lt',           label: '<' },
		{ value: 'lte',          label: '≤' },
		{ value: 'gt',           label: '>' },
		{ value: 'gte',          label: '≥' },
		{ value: 'is_empty',     label: 'is empty' },
		{ value: 'is_not_empty', label: 'is not empty' },
	];
	const DATE_OPS: { value: FilterOp; label: string }[] = [
		{ value: 'on',           label: 'is' },
		{ value: 'before',       label: 'before' },
		{ value: 'after',        label: 'after' },
		{ value: 'is_empty',     label: 'is empty' },
		{ value: 'is_not_empty', label: 'is not empty' },
	];

	const filterKey = `col-filter:${folder}`;

	function loadFilters(): FilterCriterion[] {
		try {
			const stored = localStorage.getItem(filterKey);
			if (stored) return JSON.parse(stored);
		} catch { /* ignore */ }
		return [];
	}

	let filters = $state<FilterCriterion[]>(loadFilters());
	let showFilterPanel = $state(false);

	function saveFilters() {
		localStorage.setItem(filterKey, JSON.stringify(filters));
	}

	function getFieldType(field: string): string {
		if (field === 'filename') return 'text';
		return fieldMap[field]?.field_type ?? 'text';
	}

	function getOpsForType(type: string): { value: FilterOp; label: string }[] {
		if (type === 'number') return NUMBER_OPS;
		if (type === 'date') return DATE_OPS;
		return TEXT_OPS;
	}

	function defaultOpForType(type: string): FilterOp {
		if (type === 'number') return 'eq';
		if (type === 'date') return 'on';
		return 'contains';
	}

	function addFilter() {
		const field = baseCols[0]?.id ?? 'filename';
		const type = getFieldType(field);
		filters = [...filters, { field, op: defaultOpForType(type), value: '' }];
		saveFilters();
		activeViewId = null;
	}

	function removeFilter(idx: number) {
		filters = filters.filter((_, i) => i !== idx);
		saveFilters();
		activeViewId = null;
	}

	function updateFilterField(idx: number, field: string) {
		const type = getFieldType(field);
		filters = filters.map((f, i) =>
			i === idx ? { field, op: defaultOpForType(type), value: '' } : f
		);
		saveFilters();
		activeViewId = null;
	}

	function updateFilterOp(idx: number, op: FilterOp) {
		filters = filters.map((f, i) => i === idx ? { ...f, op } : f);
		saveFilters();
		activeViewId = null;
	}

	function updateFilterValue(idx: number, value: string) {
		filters = filters.map((f, i) => i === idx ? { ...f, value } : f);
		saveFilters();
		activeViewId = null;
	}

	const needsValue = (op: FilterOp) => op !== 'is_empty' && op !== 'is_not_empty';

	function getFilterRaw(record: VaultRecord, field: string): string {
		if (field === 'filename') return record.filename;
		const f = fieldMap[field];
		if (!f) return '';
		const raw = f.source === 'frontmatter' ? record.frontmatter[field] : record.sections[field];
		if (raw === null || raw === undefined) return '';
		return String(raw);
	}

	function matchesCriterion(record: VaultRecord, criterion: FilterCriterion): boolean {
		const { field, op, value } = criterion;
		const raw = getFilterRaw(record, field);

		if (op === 'is_empty')     return raw === '';
		if (op === 'is_not_empty') return raw !== '';

		const type = getFieldType(field);

		if (type === 'number') {
			const numRaw = parseFloat(raw);
			const numVal = parseFloat(value);
			if (isNaN(numRaw)) return false;
			if (!value || isNaN(numVal)) return true; // incomplete filter → pass-through
			if (op === 'eq')  return numRaw === numVal;
			if (op === 'lt')  return numRaw < numVal;
			if (op === 'lte') return numRaw <= numVal;
			if (op === 'gt')  return numRaw > numVal;
			if (op === 'gte') return numRaw >= numVal;
		}

		if (type === 'date') {
			if (!value) return true; // incomplete filter → pass-through
			if (op === 'on')     return raw === value;
			if (op === 'before') return raw !== '' && raw < value;
			if (op === 'after')  return raw !== '' && raw > value;
		}

		// text / url / relation / markdown
		if (!value) return true; // incomplete filter → pass-through
		const lRaw = raw.toLowerCase();
		const lVal = value.toLowerCase();
		if (op === 'contains')     return lRaw.includes(lVal);
		if (op === 'not_contains') return !lRaw.includes(lVal);

		return true;
	}

	function matchesQuickSearch(record: VaultRecord, query: string): boolean {
		const q = query.trim().toLowerCase();
		if (!q) return true;
		return ['filename', ...Object.keys(fieldMap)].some((field) =>
			getFilterRaw(record, field).toLowerCase().includes(q)
		);
	}

	const filteredRecords = $derived(
		records.filter(
			(r) => filters.every((f) => matchesCriterion(r, f)) && matchesQuickSearch(r, quickSearch)
		)
	);

	// --- Multi-field sort (persisted in localStorage) ------------------------

	type SortCriterion = { id: string; dir: 'asc' | 'desc' };

	const sortKey = `col-sort:${folder}`;

	function loadSort(): SortCriterion[] {
		try {
			const stored = localStorage.getItem(sortKey);
			if (stored) return JSON.parse(stored);
		} catch { /* ignore */ }
		return [];
	}

	let sortCriteria = $state<SortCriterion[]>(loadSort());

	function saveSortCriteria() {
		localStorage.setItem(sortKey, JSON.stringify(sortCriteria));
	}

	function handleSortClick(colId: string) {
		const idx = sortCriteria.findIndex((s) => s.id === colId);
		if (idx === -1) {
			sortCriteria = [...sortCriteria, { id: colId, dir: 'asc' }];
		} else if (sortCriteria[idx].dir === 'asc') {
			sortCriteria = sortCriteria.map((s, i) => i === idx ? { ...s, dir: 'desc' } : s);
		} else {
			sortCriteria = sortCriteria.filter((_, i) => i !== idx);
		}
		saveSortCriteria();
		activeViewId = null;
	}

	function getSortValue(record: VaultRecord, colId: string): string | number {
		if (colId === 'filename') return record.filename.toLowerCase();
		const field = fieldMap[colId];
		if (!field) return '';
		const val = field.source === 'frontmatter'
			? record.frontmatter[colId]
			: record.sections[colId];
		if (val === null || val === undefined) return '';
		if (typeof val === 'number') return val;
		return String(val).toLowerCase();
	}

	const sortedRecords = $derived(
		sortCriteria.length === 0
			? filteredRecords
			: [...filteredRecords].sort((a, b) => {
				for (const { id, dir } of sortCriteria) {
					const av = getSortValue(a, id);
					const bv = getSortValue(b, id);
					const cmp = av < bv ? -1 : av > bv ? 1 : 0;
					if (cmp !== 0) return dir === 'asc' ? cmp : -cmp;
				}
				return 0;
			})
	);

	// --- Views (persisted in DB via API) ------------------------------------

	let views = $state<View[]>([]);
	let showViewPanel = $state(false);
	let savingView = $state(false);
	let newViewName = $state('');
	let showSaveForm = $state(false);
	let activeViewId = $state<string | null>(null);

	const defaultViewKey = `col-default-view:${folder}`;
	let defaultViewId = $state<string | null>(localStorage.getItem(defaultViewKey));

	$effect(() => {
		const v = vault, f = folder;
		getViews(v, f).then((result) => {
			views = result;
			const defId = localStorage.getItem(`col-default-view:${f}`);
			if (defId) {
				const def = result.find((view) => view.id === defId);
				if (def) applyView(def);
			}
		});
	});

	function applyView(view: View) {
		colOrder = view.col_order.length ? view.col_order : baseCols.map((c) => c.id);
		hiddenCols = new Set(view.hidden_cols);
		filters = view.filters as FilterCriterion[];
		sortCriteria = view.sort as SortCriterion[];
		saveOrder();
		saveHidden();
		saveFilters();
		saveSortCriteria();
		activeViewId = view.id;
		showViewPanel = false;
	}

	function toggleDefaultView(viewId: string) {
		if (defaultViewId === viewId) {
			localStorage.removeItem(defaultViewKey);
			defaultViewId = null;
		} else {
			localStorage.setItem(defaultViewKey, viewId);
			defaultViewId = viewId;
		}
	}

	async function handleSaveView() {
		const name = newViewName.trim();
		if (!name) return;
		savingView = true;
		try {
			const created = await createView(vault, folder, {
				name,
				filters,
				sort: sortCriteria,
				col_order: colOrder,
				hidden_cols: [...hiddenCols],
			});
			views = [...views, created];
			newViewName = '';
			showSaveForm = false;
		} finally {
			savingView = false;
		}
	}

	async function handleDeleteView(id: string) {
		await deleteView(vault, folder, id);
		views = views.filter((v) => v.id !== id);
		if (activeViewId === id) activeViewId = null;
		if (defaultViewId === id) {
			localStorage.removeItem(defaultViewKey);
			defaultViewId = null;
		}
	}

	// --- Save handler with error feedback -----------------------------------

	let saveError = $state<string | null>(null);
	let errorTimer: ReturnType<typeof setTimeout> | null = null;

	async function handleSave(record: VaultRecord, colId: string, value: string) {
		const field = fieldMap[colId];
		if (!field) return;
		let patch: RecordUpdate;
		if (field.source === 'frontmatter') {
			patch = { frontmatter: { ...record.frontmatter, [colId]: value } };
		} else {
			patch = { section: { heading: colId, body: value } };
		}
		try {
			await recordsStore.update(record.id, patch);
		} catch (e) {
			saveError = e instanceof Error ? e.message : 'Save failed';
			if (errorTimer) clearTimeout(errorTimer);
			errorTimer = setTimeout(() => { saveError = null; }, 4000);
		}
	}
</script>

<div class="datatable">

{#if saveError}
	<div class="save-error" role="alert">{saveError}</div>
{/if}

<div class="toolbar">
	{#if isReordered}
		<button class="reset-btn" onclick={resetOrder}>Reset column order</button>
	{/if}
	<div class="view-panel-anchor">
		<button
			class="view-btn"
			class:view-active={activeViewId !== null}
			onclick={() => { showViewPanel = !showViewPanel; showSaveForm = false; }}
		>
			{#if activeViewId !== null}
				{views.find((v) => v.id === activeViewId)?.name ?? 'View'}
			{:else}
				Views{views.length > 0 ? ` (${views.length})` : ''}
			{/if}
		</button>
		{#if showViewPanel}
			<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
			<div class="view-panel" role="dialog" aria-label="Saved views" onmouseleave={() => { if (!showSaveForm) showViewPanel = false; }}>
				{#if views.length === 0 && !showSaveForm}
					<p class="view-empty-hint">No saved views.</p>
				{:else}
					<ul class="view-list">
						{#each views as view (view.id)}
							<li class="view-row" class:view-row-active={view.id === activeViewId}>
								<button
									class="view-default-btn"
									class:view-default-set={defaultViewId === view.id}
									onclick={() => toggleDefaultView(view.id)}
									title={defaultViewId === view.id ? 'Remove default' : 'Set as default'}
									aria-label={defaultViewId === view.id ? 'Remove default' : 'Set as default'}
								>{defaultViewId === view.id ? '★' : '☆'}</button>
								<button class="view-apply-btn" onclick={() => applyView(view)}>{view.name}</button>
								<button class="view-delete-btn" onclick={() => handleDeleteView(view.id)} aria-label="Delete view">✕</button>
							</li>
						{/each}
					</ul>
				{/if}
				<div class="view-panel-footer">
					{#if showSaveForm}
						<div class="view-save-form">
							<!-- svelte-ignore a11y_autofocus -->
							<input
								autofocus
								class="view-name-input"
								placeholder="View name"
								bind:value={newViewName}
								onkeydown={(e) => { if (e.key === 'Enter') handleSaveView(); if (e.key === 'Escape') { showSaveForm = false; newViewName = ''; } }}
							/>
							<button class="view-save-confirm-btn" onclick={handleSaveView} disabled={savingView || !newViewName.trim()}>
								{savingView ? '…' : 'Save'}
							</button>
							<button class="view-save-cancel-btn" onclick={() => { showSaveForm = false; newViewName = ''; }}>Cancel</button>
						</div>
					{:else}
						<button class="view-save-btn" onclick={() => { showSaveForm = true; }}>+ Save current view</button>
					{/if}
				</div>
			</div>
		{/if}
	</div>
	<div class="filter-panel-anchor">
		<button
			class="filter-btn"
			class:filter-active={filters.length > 0}
			onclick={() => (showFilterPanel = !showFilterPanel)}
		>
			Filter{filters.length > 0 ? ` (${filters.length})` : ''}
		</button>
		{#if showFilterPanel}
			<div class="filter-panel" role="dialog" aria-label="Row filters">
				{#if filters.length === 0}
					<p class="filter-empty-hint">No filters applied.</p>
				{:else}
					<ul class="filter-list">
						{#each filters as criterion, idx (idx)}
							{@const type = getFieldType(criterion.field)}
							{@const ops = getOpsForType(type)}
							<li class="filter-row">
								<select
									class="filter-select filter-field-select"
									value={criterion.field}
									onchange={(e) => updateFilterField(idx, (e.currentTarget as HTMLSelectElement).value)}
								>
									{#each baseCols as col (col.id)}
										<option value={col.id}>{col.label}</option>
									{/each}
								</select>
								<select
									class="filter-select filter-op-select"
									value={criterion.op}
									onchange={(e) => updateFilterOp(idx, (e.currentTarget as HTMLSelectElement).value as FilterOp)}
								>
									{#each ops as op (op.value)}
										<option value={op.value}>{op.label}</option>
									{/each}
								</select>
								{#if needsValue(criterion.op)}
									{#if type === 'date'}
										<input
											type="date"
											class="filter-value-input"
											value={criterion.value}
											oninput={(e) => updateFilterValue(idx, (e.currentTarget as HTMLInputElement).value)}
										/>
									{:else if type === 'number'}
										<input
											type="number"
											class="filter-value-input"
											placeholder="value"
											value={criterion.value}
											oninput={(e) => updateFilterValue(idx, (e.currentTarget as HTMLInputElement).value)}
										/>
									{:else}
										<input
											type="text"
											class="filter-value-input"
											placeholder="value"
											value={criterion.value}
											oninput={(e) => updateFilterValue(idx, (e.currentTarget as HTMLInputElement).value)}
										/>
									{/if}
								{:else}
									<span class="filter-value-spacer"></span>
								{/if}
								<button class="filter-remove-btn" onclick={() => removeFilter(idx)} aria-label="Remove filter">✕</button>
							</li>
						{/each}
					</ul>
				{/if}
				<div class="filter-panel-footer">
					<button class="filter-add-btn" onclick={addFilter}>+ Add filter</button>
					{#if filters.length > 0}
						<button class="filter-clear-btn" onclick={() => { filters = []; saveFilters(); }}>Clear all</button>
					{/if}
				</div>
			</div>
		{/if}
	</div>
	<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
	<div class="col-panel-anchor" onmouseleave={() => (showColPanel = false)}>
		<button class="col-toggle-btn" onclick={() => (showColPanel = !showColPanel)}>
			Columns{hiddenCols.size > 0 ? ` (${hiddenCols.size} hidden)` : ''}
		</button>
		{#if showColPanel}
			<div class="col-panel" role="menu">
				{#each baseCols as col (col.id)}
					<label class="col-panel-row">
						<input
							type="checkbox"
							checked={!hiddenCols.has(col.id)}
							onchange={() => toggleColumn(col.id)}
							disabled={col.id === 'filename'}
						/>
						{col.label}
					</label>
				{/each}
				<div class="col-panel-footer">
					<button
						class="show-all-btn"
						disabled={hiddenCols.size === 0}
						onclick={() => { hiddenCols = new Set(); saveHidden(); }}
					>
						Show all
					</button>
				</div>
			</div>
		{/if}
	</div>
</div>

{#if records.length === 0}
	<p class="empty">No records in this folder yet.</p>
{:else if filteredRecords.length === 0}
	<p class="empty">No records match the active filters.</p>
{:else}
	<div class="table-wrap">
		<table>
			<thead>
				<tr>
					{#each visibleCols as col (col.id)}
						{@const sortIdx = sortCriteria.findIndex((s) => s.id === col.id)}
						<th
							style="width: {colW(col.id, col.defaultW)}px"
							draggable="true"
							class:drag-over-left={dropTargetId === col.id && dropSide === 'left'}
							class:drag-over-right={dropTargetId === col.id && dropSide === 'right'}
							class:dragging={dragId === col.id}
							ondragstart={(e) => onDragStart(e, col.id)}
							ondragover={(e) => onDragOver(e, col.id)}
							ondragleave={onDragLeave}
							ondrop={(e) => onDrop(e, col.id)}
							ondragend={onDragEnd}
						>
							<ColumnHeader
								label={col.label}
								canResize={true}
								onResizeStart={resizeHandler(col.id, col.defaultW)}
								sortDir={sortIdx !== -1 ? sortCriteria[sortIdx].dir : null}
								sortPriority={sortCriteria.length > 1 ? sortIdx + 1 : null}
								onSortClick={() => handleSortClick(col.id)}
							/>
						</th>
					{/each}
				</tr>
			</thead>
			<tbody>
				{#each sortedRecords as record (record.id)}
					<tr>
						{#each visibleCols as col (col.id)}
							<td style="width: {colW(col.id, col.defaultW)}px">
								{#if col.isFilename}
									<div class="cell-inner" onscroll={(e) => { const el = e.currentTarget as HTMLElement; el.style.setProperty('--shadow-opacity', el.scrollTop > 0 ? '1' : '0'); }}>
										<a href="/{encodeURIComponent(vault)}/{encodeURIComponent(folder)}/{encodeURIComponent(record.filename)}" class="record-link">
											{record.filename}
										</a>
									</div>
								{:else}
									{@const field = fieldMap[col.id]}
									{#if field}
										<div class="cell-inner" onscroll={(e) => { const el = e.currentTarget as HTMLElement; el.style.setProperty('--shadow-opacity', el.scrollTop > 0 ? '1' : '0'); }}>
											<TableCell
												{record}
												{field}
												onSave={(v) => handleSave(record, col.id, v)}
											/>
										</div>
									{/if}
								{/if}
							</td>
						{/each}
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

</div>

<style>
	.datatable {
		display: flex;
		flex-direction: column;
		height: 100%;
		min-height: 0;
	}
	.table-wrap {
		flex: 1;
		overflow: auto;
		min-height: 0;
	}
	table {
		border-collapse: collapse;
		table-layout: fixed;
		width: max-content;
		font-size: 0.9rem;
	}
	thead {
		position: sticky;
		top: 0;
		z-index: 5;
		background: #f3f4f6;
		border-bottom: 2px solid #d1d5db;
	}
	th {
		position: relative;
		padding: 8px 12px;
		text-align: left;
		font-weight: 700;
		font-size: 0.75rem;
		letter-spacing: 0.05em;
		text-transform: uppercase;
		color: #111827;
		white-space: nowrap;
		overflow: hidden;
		vertical-align: middle;
		cursor: grab;
		user-select: none;
	}
	th.dragging {
		opacity: 0.4;
	}
	th.drag-over-left {
		box-shadow: inset 2px 0 0 #6366f1;
	}
	th.drag-over-right {
		box-shadow: inset -2px 0 0 #6366f1;
	}
	td {
		padding: 10px 0;
		border-bottom: 1px solid #e5e7eb;
		vertical-align: top;
		overflow: hidden;
		max-width: 0; /* with table-layout:fixed this makes overflow:hidden clip inner content */
	}
	.cell-inner {
		min-width: 80px;
		padding: 0 10px;
		overflow-x: hidden;
		overflow-y: auto;
		max-height: 400px;
		--shadow-opacity: 0;
	}
	.cell-inner::before {
		content: '';
		display: block;
		position: sticky;
		top: 0;
		height: 24px;
		margin: 0 -10px -24px;
		background: linear-gradient(to bottom, rgba(0, 0, 0, 0.18), transparent);
		pointer-events: none;
		z-index: 1;
		opacity: var(--shadow-opacity);
		transition: opacity 0.15s ease;
	}
	tr:hover td {
		background: #f5f5f5;
	}
	.record-link {
		display: block;
		padding: 2px 4px;
		color: #111;
		text-decoration: none;
		font-weight: 500;
	}
	.record-link:hover {
		text-decoration: underline;
	}
	.save-error {
		background: #fee2e2;
		color: #991b1b;
		border: 1px solid #fca5a5;
		border-radius: 6px;
		padding: 8px 12px;
		font-size: 0.875rem;
		margin-bottom: 8px;
	}
	.empty {
		color: #9ca3af;
		padding: 40px 0;
		text-align: center;
	}
	.toolbar {
		display: flex;
		justify-content: flex-end;
		align-items: center;
		gap: 8px;
		margin-bottom: 6px;
	}
	.reset-btn {
		background: none;
		border: none;
		cursor: pointer;
		font-size: 0.75rem;
		color: #9ca3af;
		padding: 2px 6px;
		border-radius: 4px;
	}
	.reset-btn:hover {
		color: #6b7280;
		background: #f3f4f6;
	}
	.col-panel-anchor {
		position: relative;
	}
	.col-toggle-btn {
		background: none;
		border: 1px solid #e5e7eb;
		cursor: pointer;
		font-size: 0.75rem;
		color: #6b7280;
		padding: 2px 8px;
		border-radius: 4px;
	}
	.col-toggle-btn:hover {
		background: #f3f4f6;
		color: #374151;
	}
	.col-panel {
		position: absolute;
		right: 0;
		top: calc(100% + 4px);
		z-index: 50;
		background: #fff;
		border: 1px solid #e5e7eb;
		border-radius: 6px;
		box-shadow: 0 4px 12px rgba(0,0,0,0.1);
		padding: 6px 0;
		min-width: 160px;
	}
	.col-panel-row {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 5px 12px;
		font-size: 0.8125rem;
		color: #374151;
		cursor: pointer;
		white-space: nowrap;
	}
	.col-panel-row:hover {
		background: #f9fafb;
	}
	.col-panel-row input {
		cursor: pointer;
	}
	.col-panel-row input:disabled {
		cursor: default;
		opacity: 0.4;
	}
	.col-panel-footer {
		border-top: 1px solid #f3f4f6;
		padding: 5px 8px 3px;
		margin-top: 2px;
	}
	.show-all-btn {
		background: none;
		border: none;
		cursor: pointer;
		font-size: 0.75rem;
		color: #6366f1;
		padding: 2px 4px;
		border-radius: 4px;
		width: 100%;
		text-align: left;
	}
	.show-all-btn:hover:not(:disabled) {
		background: #eef2ff;
	}
	.show-all-btn:disabled {
		color: #c7d2fe;
		cursor: default;
	}
	.filter-panel-anchor {
		position: relative;
	}
	.filter-btn {
		background: none;
		border: 1px solid #e5e7eb;
		cursor: pointer;
		font-size: 0.75rem;
		color: #6b7280;
		padding: 2px 8px;
		border-radius: 4px;
	}
	.filter-btn:hover {
		background: #f3f4f6;
		color: #374151;
	}
	.filter-btn.filter-active {
		border-color: #6366f1;
		color: #6366f1;
		background: #eef2ff;
	}
	.filter-panel {
		position: absolute;
		right: 0;
		top: calc(100% + 4px);
		z-index: 50;
		background: #fff;
		border: 1px solid #e5e7eb;
		border-radius: 6px;
		box-shadow: 0 4px 12px rgba(0,0,0,0.1);
		padding: 8px 0 4px;
		min-width: 480px;
	}
	.filter-empty-hint {
		color: #9ca3af;
		font-size: 0.8125rem;
		padding: 4px 12px 8px;
		margin: 0;
	}
	.filter-list {
		list-style: none;
		margin: 0;
		padding: 0;
	}
	.filter-row {
		display: flex;
		align-items: center;
		gap: 6px;
		padding: 4px 10px;
	}
	.filter-row:hover {
		background: #f9fafb;
	}
	.filter-select {
		border: 1px solid #e5e7eb;
		border-radius: 4px;
		font-size: 0.8125rem;
		color: #374151;
		background: #fff;
		padding: 2px 4px;
		cursor: pointer;
	}
	.filter-field-select {
		max-width: 140px;
	}
	.filter-op-select {
		max-width: 140px;
	}
	.filter-value-input {
		flex: 1;
		border: 1px solid #e5e7eb;
		border-radius: 4px;
		font-size: 0.8125rem;
		color: #374151;
		padding: 2px 6px;
		min-width: 0;
	}
	.filter-value-input:focus {
		outline: none;
		border-color: #6366f1;
		box-shadow: 0 0 0 2px #eef2ff;
	}
	.filter-value-spacer {
		flex: 1;
	}
	.filter-remove-btn {
		background: none;
		border: none;
		cursor: pointer;
		color: #9ca3af;
		font-size: 0.75rem;
		padding: 2px 4px;
		border-radius: 4px;
		line-height: 1;
	}
	.filter-remove-btn:hover {
		color: #ef4444;
		background: #fee2e2;
	}
	.filter-panel-footer {
		border-top: 1px solid #f3f4f6;
		padding: 6px 10px 4px;
		margin-top: 4px;
		display: flex;
		gap: 8px;
		align-items: center;
	}
	.filter-add-btn {
		background: none;
		border: none;
		cursor: pointer;
		font-size: 0.75rem;
		color: #6366f1;
		padding: 2px 4px;
		border-radius: 4px;
	}
	.filter-add-btn:hover {
		background: #eef2ff;
	}
	.filter-clear-btn {
		background: none;
		border: none;
		cursor: pointer;
		font-size: 0.75rem;
		color: #9ca3af;
		padding: 2px 4px;
		border-radius: 4px;
		margin-left: auto;
	}
	.filter-clear-btn:hover {
		color: #6b7280;
		background: #f3f4f6;
	}
	.view-panel-anchor {
		position: relative;
	}
	.view-btn {
		background: none;
		border: 1px solid #e5e7eb;
		cursor: pointer;
		font-size: 0.75rem;
		color: #6b7280;
		padding: 2px 8px;
		border-radius: 4px;
	}
	.view-btn:hover {
		background: #f3f4f6;
		color: #374151;
	}
	.view-btn.view-active {
		border-color: #6366f1;
		color: #6366f1;
		background: #eef2ff;
	}
	.view-panel {
		position: absolute;
		right: 0;
		top: calc(100% + 4px);
		z-index: 50;
		background: #fff;
		border: 1px solid #e5e7eb;
		border-radius: 6px;
		box-shadow: 0 4px 12px rgba(0,0,0,0.1);
		padding: 8px 0 4px;
		min-width: 200px;
	}
	.view-empty-hint {
		color: #9ca3af;
		font-size: 0.8125rem;
		padding: 4px 12px 8px;
		margin: 0;
	}
	.view-list {
		list-style: none;
		margin: 0;
		padding: 0;
	}
	.view-row {
		display: flex;
		align-items: center;
		gap: 4px;
		padding: 2px 8px 2px 4px;
	}
	.view-row:hover {
		background: #f9fafb;
	}
	.view-row-active {
		background: #eef2ff;
	}
	.view-row-active:hover {
		background: #e0e7ff;
	}
	.view-default-btn {
		background: none;
		border: none;
		cursor: pointer;
		color: #d1d5db;
		font-size: 0.85rem;
		padding: 2px 2px;
		border-radius: 4px;
		line-height: 1;
		flex-shrink: 0;
	}
	.view-default-btn:hover {
		color: #f59e0b;
	}
	.view-default-btn.view-default-set {
		color: #f59e0b;
	}
	.view-apply-btn {
		flex: 1;
		background: none;
		border: none;
		cursor: pointer;
		font-size: 0.8125rem;
		color: #374151;
		padding: 4px 8px;
		border-radius: 4px;
		text-align: left;
	}
	.view-apply-btn:hover {
		color: #6366f1;
	}
	.view-delete-btn {
		background: none;
		border: none;
		cursor: pointer;
		color: #9ca3af;
		font-size: 0.75rem;
		padding: 2px 4px;
		border-radius: 4px;
		line-height: 1;
		flex-shrink: 0;
	}
	.view-delete-btn:hover {
		color: #ef4444;
		background: #fee2e2;
	}
	.view-panel-footer {
		border-top: 1px solid #f3f4f6;
		padding: 6px 8px 4px;
		margin-top: 4px;
	}
	.view-save-btn {
		background: none;
		border: none;
		cursor: pointer;
		font-size: 0.75rem;
		color: #6366f1;
		padding: 2px 4px;
		border-radius: 4px;
		width: 100%;
		text-align: left;
	}
	.view-save-btn:hover {
		background: #eef2ff;
	}
	.view-save-form {
		display: flex;
		align-items: center;
		gap: 4px;
	}
	.view-name-input {
		flex: 1;
		border: 1px solid #e5e7eb;
		border-radius: 4px;
		font-size: 0.8125rem;
		color: #374151;
		padding: 3px 6px;
		min-width: 0;
	}
	.view-name-input:focus {
		outline: none;
		border-color: #6366f1;
		box-shadow: 0 0 0 2px #eef2ff;
	}
	.view-save-confirm-btn {
		background: #6366f1;
		color: #fff;
		border: none;
		cursor: pointer;
		font-size: 0.75rem;
		padding: 3px 8px;
		border-radius: 4px;
		white-space: nowrap;
	}
	.view-save-confirm-btn:hover:not(:disabled) {
		background: #4f46e5;
	}
	.view-save-confirm-btn:disabled {
		opacity: 0.5;
		cursor: default;
	}
	.view-save-cancel-btn {
		background: none;
		border: none;
		cursor: pointer;
		font-size: 0.75rem;
		color: #9ca3af;
		padding: 3px 4px;
		border-radius: 4px;
	}
	.view-save-cancel-btn:hover {
		color: #6b7280;
		background: #f3f4f6;
	}
</style>
