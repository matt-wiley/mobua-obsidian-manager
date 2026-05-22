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
			type: schemaMap[key]?.field_type ?? 'text'
		}))
	);

	const sectionEntries = $derived(Object.entries(record.sections));

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

<div class="page-view">
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
	</div>

	<!-- Frontmatter properties -->
	{#if fmEntries.length > 0}
		<div class="properties">
			{#each fmEntries as fm (fm.key)}
				<FieldBlock
					{record}
					label={fm.key}
					fieldType={fm.type}
					value={fm.value}
					onSave={(v) => saveField(fm.key, v)}
				/>
			{/each}
		</div>
	{/if}

	<!-- H2 sections -->
	{#each sectionEntries as [title, content] (title)}
		<SectionBlock
			{title}
			{content}
			onSaveContent={(v) => saveSection(title, v)}
			onSaveTitle={(newTitle) => renameSectionTitle(title, newTitle)}
		/>
	{/each}
</div>

<style>
	.page-view {
		max-width: 760px;
	}
	.save-error {
		background: #fee2e2;
		color: #991b1b;
		border: 1px solid #fca5a5;
		border-radius: 6px;
		padding: 8px 12px;
		font-size: 0.875rem;
		margin-bottom: 12px;
	}
	.title-row {
		margin-bottom: 20px;
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
