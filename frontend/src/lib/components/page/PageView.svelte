<script lang="ts">
	import type { VaultRecord, RecordUpdate } from '$lib/api/records';
	import type { SchemaField } from '$lib/api/folders';
	import { recordsStore } from '$lib/stores/records.svelte';
	import FieldBlock from './FieldBlock.svelte';
	import SectionBlock from './SectionBlock.svelte';

	let {
		record,
		schema
	}: {
		record: VaultRecord;
		schema: SchemaField[];
	} = $props();

	// --- Title editing -------------------------------------------------------

	let editingTitle = $state(false);
	let titleDraft = $state('');

	function startTitleEdit() {
		titleDraft = record.filename;
		editingTitle = true;
	}

	async function commitTitle() {
		editingTitle = false;
		if (titleDraft.trim() && titleDraft !== record.filename) {
			await save({ filename: titleDraft.trim() });
		}
	}

	function onTitleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') commitTitle();
		if (e.key === 'Escape') editingTitle = false;
	}

	// --- Field and section data ----------------------------------------------

	const schemaMap = $derived(
		Object.fromEntries(schema.map((f) => [f.field_name, f]))
	);

	const fmEntries = $derived(
		Object.keys(record.frontmatter).map((key) => ({
			key,
			value: record.frontmatter[key] != null ? String(record.frontmatter[key]) : '',
			type: schemaMap[key]?.field_type ?? 'text',
			options: schemaMap[key]?.options ?? []
		}))
	);

	const sectionEntries = $derived(Object.entries(record.sections));
	const detailsEntry = $derived(sectionEntries.find(([title]) => title === 'Details'));
	const otherSectionEntries = $derived(sectionEntries.filter(([title]) => title !== 'Details'));

	// --- Layout mode -----------------------------------------------------------

	type LayoutMode = 'single' | 'two-centered' | 'two-full';
	const LAYOUT_STORAGE_KEY = 'pageview-layout-mode';
	const storedLayoutMode = localStorage.getItem(LAYOUT_STORAGE_KEY);
	let layoutMode = $state<LayoutMode>(
		storedLayoutMode === 'single' || storedLayoutMode === 'two-centered' || storedLayoutMode === 'two-full'
			? storedLayoutMode
			: 'two-centered'
	);

	function setLayoutMode(mode: LayoutMode) {
		layoutMode = mode;
		localStorage.setItem(LAYOUT_STORAGE_KEY, mode);
	}

	// --- Left column width (resizable, with snap points) ------------------------

	const WIDTH_STORAGE_KEY = 'pageview-left-col-width';
	const MIN_WIDTH_PCT = 20;
	const MAX_WIDTH_PCT = 60;
	const DEFAULT_WIDTH_PCT = 32;
	const SNAP_POINTS = [25, 33.33, 50];
	const SNAP_THRESHOLD_PCT = 1.5;

	const storedWidthPct = Number(localStorage.getItem(WIDTH_STORAGE_KEY));
	let leftWidthPct = $state(
		Number.isFinite(storedWidthPct) && storedWidthPct >= MIN_WIDTH_PCT && storedWidthPct <= MAX_WIDTH_PCT
			? storedWidthPct
			: DEFAULT_WIDTH_PCT
	);

	let bodyEl = $state<HTMLDivElement | undefined>(undefined);
	let resizing = $state(false);

	function onResizerPointerDown(e: PointerEvent) {
		resizing = true;
		(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
	}

	function onResizerPointerMove(e: PointerEvent) {
		if (!resizing || !bodyEl) return;
		const rect = bodyEl.getBoundingClientRect();
		let pct = ((e.clientX - rect.left) / rect.width) * 100;
		pct = Math.min(MAX_WIDTH_PCT, Math.max(MIN_WIDTH_PCT, pct));
		for (const snap of SNAP_POINTS) {
			if (Math.abs(pct - snap) < SNAP_THRESHOLD_PCT) {
				pct = snap;
				break;
			}
		}
		leftWidthPct = pct;
	}

	function onResizerPointerUp() {
		if (!resizing) return;
		resizing = false;
		localStorage.setItem(WIDTH_STORAGE_KEY, String(leftWidthPct));
	}

	// --- Save with error handling --------------------------------------------

	let saveError = $state<string | null>(null);
	let errorTimer: ReturnType<typeof setTimeout> | null = null;

	async function save(patch: RecordUpdate) {
		try {
			await recordsStore.update(record.id, patch);
		} catch (e) {
			saveError = e instanceof Error ? e.message : 'Save failed';
			if (errorTimer) clearTimeout(errorTimer);
			errorTimer = setTimeout(() => { saveError = null; }, 4000);
		}
	}

	async function saveField(key: string, value: string) {
		await save({ frontmatter: { ...record.frontmatter, [key]: value } });
	}

	async function saveSection(sectionTitle: string, value: string) {
		await save({ sections: { ...record.sections, [sectionTitle]: value } });
	}

	async function renameSectionTitle(oldTitle: string, newTitle: string) {
		const newSections: Record<string, string> = {};
		for (const [k, v] of Object.entries(record.sections)) {
			newSections[k === oldTitle ? newTitle : k] = v as string;
		}
		await save({ sections: newSections });
	}
</script>

<div class="page-view mode-{layoutMode}">
	<div class="page-col">
		{#if saveError}
			<div class="save-error" role="alert">{saveError}</div>
		{/if}

		<!-- Title -->
		<div class="title-row">
			{#if editingTitle}
				<!-- svelte-ignore a11y_autofocus -->
				<input
					class="title-input"
					type="text"
					autofocus
					bind:value={titleDraft}
					onblur={commitTitle}
					onkeydown={onTitleKeydown}
				/>
			{:else}
				<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_noninteractive_element_interactions -->
				<h1 class="title" onclick={startTitleEdit}>{record.filename}</h1>
			{/if}

			<div class="layout-toggle" role="group" aria-label="Page layout">
				<button
					class:active={layoutMode === 'single'}
					onclick={() => setLayoutMode('single')}
					title="Single column"
				>1 col</button>
				<button
					class:active={layoutMode === 'two-centered'}
					onclick={() => setLayoutMode('two-centered')}
					title="Two columns, centered"
				>2 col</button>
				<button
					class:active={layoutMode === 'two-full'}
					onclick={() => setLayoutMode('two-full')}
					title="Two columns, full width"
				>2 col wide</button>
			</div>
		</div>

		<div
			class="body"
			class:resizing
			bind:this={bodyEl}
			style={layoutMode !== 'single' ? `grid-template-columns: ${leftWidthPct}% 8px 1fr` : undefined}
		>
			<div class="col-left">
				<!-- Frontmatter properties -->
				{#if fmEntries.length > 0}
					<div class="properties">
						{#each fmEntries as fm (fm.key)}
							<FieldBlock
								{record}
								label={fm.key}
								fieldType={fm.type}
								options={fm.options}
								value={fm.value}
								onSave={(v) => saveField(fm.key, v)}
							/>
						{/each}
					</div>
				{/if}

				{#if detailsEntry}
					{@const [title, content] = detailsEntry}
					<SectionBlock
						{title}
						{content}
						onSaveContent={(v) => saveSection(title, v)}
						onSaveTitle={(newTitle) => renameSectionTitle(title, newTitle)}
					/>
				{/if}
			</div>

			{#if layoutMode !== 'single'}
				<!-- svelte-ignore a11y_no_static_element_interactions -->
				<div
					class="col-resizer"
					role="separator"
					aria-orientation="vertical"
					aria-label="Resize columns"
					onpointerdown={onResizerPointerDown}
					onpointermove={onResizerPointerMove}
					onpointerup={onResizerPointerUp}
				></div>
			{/if}

			<div class="col-right">
				{#each otherSectionEntries as [title, content] (title)}
					<SectionBlock
						{title}
						{content}
						onSaveContent={(v) => saveSection(title, v)}
						onSaveTitle={(newTitle) => renameSectionTitle(title, newTitle)}
					/>
				{/each}
			</div>
		</div>
	</div>
</div>

<style>
	.page-view {
		container-type: inline-size;
		container-name: page-view;
		height: 100%;
		display: flex;
		flex-direction: column;
		min-height: 0;
	}
	.page-col {
		width: 100%;
		max-width: 760px;
		margin: 0 auto;
		height: 100%;
		display: flex;
		flex-direction: column;
		min-height: 0;
	}
	.save-error {
		background: #fee2e2;
		color: #991b1b;
		border: 1px solid #fca5a5;
		border-radius: 6px;
		padding: 8px 12px;
		font-size: 0.875rem;
		margin-bottom: 12px;
		flex-shrink: 0;
	}
	.title-row {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 12px;
		margin-bottom: 20px;
		flex-shrink: 0;
	}
	.layout-toggle {
		display: flex;
		flex-shrink: 0;
		border: 1px solid #e5e7eb;
		border-radius: 6px;
		overflow: hidden;
		margin-top: 4px;
	}
	.layout-toggle button {
		background: #fff;
		border: none;
		border-left: 1px solid #e5e7eb;
		color: #6b7280;
		font-size: 0.75rem;
		font-family: inherit;
		padding: 4px 8px;
		cursor: pointer;
		white-space: nowrap;
	}
	.layout-toggle button:first-child {
		border-left: none;
	}
	.layout-toggle button:hover {
		background: #f3f4f6;
		color: #111;
	}
	.layout-toggle button.active {
		background: #eef2ff;
		color: #4f46e5;
		font-weight: 600;
	}
	.body {
		flex: 1;
		min-height: 0;
		overflow-y: auto;
	}
	.col-left,
	.col-right {
		min-width: 0;
	}
	.col-resizer {
		display: none;
	}

	@container page-view (min-width: 760px) {
		.mode-two-centered .page-col {
			max-width: 1200px;
		}
		.mode-two-full .page-col {
			max-width: none;
		}
		.mode-two-centered .body,
		.mode-two-full .body {
			display: grid;
			grid-template-columns: minmax(280px, 360px) 1fr;
			overflow: hidden;
		}
		.mode-two-centered .col-left,
		.mode-two-centered .col-right,
		.mode-two-full .col-left,
		.mode-two-full .col-right {
			height: 100%;
			overflow-y: auto;
		}
		.mode-two-centered .col-left,
		.mode-two-full .col-left {
			padding-right: 12px;
		}
		.mode-two-centered .col-right,
		.mode-two-full .col-right {
			padding-left: 12px;
		}
		.mode-two-centered .col-resizer,
		.mode-two-full .col-resizer {
			display: flex;
			justify-content: center;
			height: 100%;
			cursor: col-resize;
			touch-action: none;
		}
		.mode-two-centered .col-resizer::after,
		.mode-two-full .col-resizer::after {
			content: '';
			width: 1px;
			height: 100%;
			background: #e5e7eb;
			transition: background 0.15s, width 0.15s;
		}
		.mode-two-centered .col-resizer:hover::after,
		.mode-two-full .col-resizer:hover::after,
		.body.resizing .col-resizer::after {
			width: 3px;
			background: #6366f1;
		}
		.body.resizing {
			user-select: none;
		}
	}
	.title {
		margin: 0;
		font-size: 1.8rem;
		font-weight: 700;
		color: #111;
		cursor: pointer;
		border-radius: 4px;
		padding: 2px 4px;
		display: inline-block;
	}
	.title:hover {
		background: #f3f4f6;
	}
	.title-input {
		flex: 1;
		min-width: 0;
		width: 100%;
		font-size: 1.8rem;
		font-weight: 700;
		color: #111;
		border: 1px solid #6366f1;
		border-radius: 4px;
		padding: 2px 6px;
		font-family: inherit;
		outline: none;
		box-sizing: border-box;
	}
	.properties {
		display: grid;
		grid-template-columns: 160px 1fr;
		gap: 2px 0;
		margin-bottom: 24px;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		padding: 8px 12px;
		background: #fafafa;
	}
</style>
