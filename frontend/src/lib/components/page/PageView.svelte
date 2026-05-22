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
			await recordsStore.update(record.id, { filename: titleDraft.trim() });
		}
	}

	function onTitleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') commitTitle();
		if (e.key === 'Escape') editingTitle = false;
	}

	// --- Field and section data ----------------------------------------------

	// Schema type lookup by field name
	const schemaMap = $derived(
		Object.fromEntries(schema.map((f) => [f.field_name, f]))
	);

	// Frontmatter entries from the record (in key order), with resolved type
	const fmEntries = $derived(
		Object.keys(record.frontmatter).map((key) => ({
			key,
			value:
				record.frontmatter[key] != null ? String(record.frontmatter[key]) : '',
			type: schemaMap[key]?.field_type ?? 'text'
		}))
	);

	// Section entries in insertion order
	const sectionEntries = $derived(Object.entries(record.sections));

	// --- Save handlers -------------------------------------------------------

	async function saveField(key: string, value: string) {
		const patch: RecordUpdate = {
			frontmatter: { ...record.frontmatter, [key]: value }
		};
		await recordsStore.update(record.id, patch);
	}

	async function saveSection(sectionTitle: string, value: string) {
		const patch: RecordUpdate = {
			sections: { ...record.sections, [sectionTitle]: value }
		};
		await recordsStore.update(record.id, patch);
	}

	async function renameSectionTitle(oldTitle: string, newTitle: string) {
		const newSections: Record<string, string> = {};
		for (const [k, v] of Object.entries(record.sections)) {
			newSections[k === oldTitle ? newTitle : k] = v as string;
		}
		await recordsStore.update(record.id, { sections: newSections });
	}
</script>

<div class="page-view">
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
