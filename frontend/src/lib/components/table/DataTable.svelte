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
				sizing[colId] = Math.max(60, startW + (ev.clientX - startX));
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

	const allCols = $derived<Col[]>([
		{ id: 'filename', label: 'Name', defaultW: 220, isFilename: true },
		...schema.map((f) => ({
			id: f.field_name,
			label: f.field_name,
			defaultW: 160,
			isFilename: false
		}))
	]);

	const fieldMap = $derived(Object.fromEntries(schema.map((f) => [f.field_name, f])));

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

{#if records.length === 0}
	<p class="empty">No records in this folder yet.</p>
{:else}
	<div class="table-wrap">
		<table>
			<thead>
				<tr>
					{#each allCols as col (col.id)}
						<th style="width: {colW(col.id, col.defaultW)}px">
							<ColumnHeader
								label={col.label}
								canResize={true}
								onResizeStart={resizeHandler(col.id, col.defaultW)}
							/>
						</th>
					{/each}
				</tr>
			</thead>
			<tbody>
				{#each records as record (record.id)}
					<tr>
						{#each allCols as col (col.id)}
							<td style="width: {colW(col.id, col.defaultW)}px">
								{#if col.isFilename}
									<a href="/{folder}/{encodeURIComponent(record.filename)}" class="record-link">
										{record.filename}
									</a>
								{:else}
									{@const field = fieldMap[col.id]}
									{#if field}
										<TableCell
											{record}
											{field}
											onSave={(v) => handleSave(record, col.id, v)}
										/>
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
	}
	td {
		padding: 4px 0;
		border-bottom: 1px solid #f3f4f6;
		vertical-align: top;
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
</style>
