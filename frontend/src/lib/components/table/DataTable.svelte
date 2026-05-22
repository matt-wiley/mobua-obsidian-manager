<script lang="ts">
	import type { VaultRecord, RecordUpdate } from '$lib/api/records';
	import type { SchemaField } from '$lib/api/folders';
	import { setColWidth } from '$lib/api/folders';
	import { recordsStore } from '$lib/stores/records.svelte';
	import TableCell from './TableCell.svelte';
	import ColumnHeader from './ColumnHeader.svelte';

	let {
		records,
		schema,
		folder,
		colWidths = {}
	}: {
		records: VaultRecord[];
		schema: SchemaField[];
		folder: string;
		colWidths?: Record<string, number>;
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
				setColWidth(folder, field, width);
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
		dragId = null;
		dropTargetId = null;
	}

	function onDragEnd() {
		dragId = null;
		dropTargetId = null;
	}

	const fieldMap = $derived(Object.fromEntries(schema.map((f) => [f.field_name, f])));

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
			? records
			: [...records].sort((a, b) => {
				for (const { id, dir } of sortCriteria) {
					const av = getSortValue(a, id);
					const bv = getSortValue(b, id);
					const cmp = av < bv ? -1 : av > bv ? 1 : 0;
					if (cmp !== 0) return dir === 'asc' ? cmp : -cmp;
				}
				return 0;
			})
	);

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
			patch = { sections: { ...record.sections, [colId]: value } };
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

{#if saveError}
	<div class="save-error" role="alert">{saveError}</div>
{/if}

{#if isReordered}
	<div class="toolbar">
		<button class="reset-btn" onclick={resetOrder}>Reset column order</button>
	</div>
{/if}

{#if records.length === 0}
	<p class="empty">No records in this folder yet.</p>
{:else}
	<div class="table-wrap">
		<table>
			<thead>
				<tr>
					{#each allCols as col (col.id)}
						{@const sortIdx = sortCriteria.findIndex((s) => s.id === col.id)}
						<th
							style="width: {colW(col.id, col.defaultW)}px"
							draggable="true"
							class:drag-over-left={dropTargetId === col.id && dropSide === 'left'}
							class:drag-over-right={dropTargetId === col.id && dropSide === 'right'}
							class:dragging={dragId === col.id}
							onclick={() => handleSortClick(col.id)}
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
							/>
						</th>
					{/each}
				</tr>
			</thead>
			<tbody>
				{#each sortedRecords as record (record.id)}
					<tr>
						{#each allCols as col (col.id)}
							<td style="width: {colW(col.id, col.defaultW)}px">
								{#if col.isFilename}
									<div class="cell-inner">
										<a href="/{folder}/{encodeURIComponent(record.filename)}" class="record-link">
											{record.filename}
										</a>
									</div>
								{:else}
									{@const field = fieldMap[col.id]}
									{#if field}
										<div class="cell-inner">
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

<style>
	.table-wrap {
		overflow-x: auto;
	}
	table {
		border-collapse: collapse;
		table-layout: fixed;
		width: max-content;
		min-width: 100%;
		font-size: 0.9rem;
	}
	thead {
		background: #f9fafb;
		border-bottom: 2px solid #e5e7eb;
	}
	th {
		position: relative;
		padding: 8px 12px;
		text-align: left;
		font-weight: 600;
		color: #374151;
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
		padding: 4px 0;
		border-bottom: 1px solid #f3f4f6;
		vertical-align: top;
		overflow: hidden;
		max-width: 0; /* with table-layout:fixed this makes overflow:hidden clip inner content */
	}
	.cell-inner {
		min-width: 80px;
		overflow: hidden;
	}
	tr:hover td {
		background: #fafafa;
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
</style>
