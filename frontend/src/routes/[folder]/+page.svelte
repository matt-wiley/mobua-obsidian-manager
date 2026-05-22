<script lang="ts">
	import { page } from '$app/stores';
	import { get } from 'svelte/store';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { recordsStore } from '$lib/stores/records.svelte';
	import { schemaStore } from '$lib/stores/schema.svelte';
	import { getColWidths } from '$lib/api/folders';
	import { createRecord } from '$lib/api/records';
	import DataTable from '$lib/components/table/DataTable.svelte';

	// folder is always defined on this route
	const folder = get(page).params.folder as string;
	let colWidths = $state<Record<string, number>>({});
	let creating = $state(false);
	let createError = $state<string | null>(null);

	onMount(async () => {
		await Promise.all([
			recordsStore.load(folder),
			schemaStore.load(folder),
			getColWidths(folder).then((w) => { colWidths = w; })
		]);
	});

	async function handleCreate() {
		creating = true;
		createError = null;
		try {
			// Try "Untitled", then "Untitled 2", etc.
			let name = 'Untitled';
			let n = 2;
			while (n <= 20) {
				try {
					const record = await createRecord(folder, { filename: name });
					await goto(`/${encodeURIComponent(folder)}/${encodeURIComponent(record.filename)}`);
					return;
				} catch (e) {
					if (e instanceof Error && e.message.includes('already exists')) {
						name = `Untitled ${n++}`;
					} else {
						throw e;
					}
				}
			}
		} catch (e) {
			createError = e instanceof Error ? e.message : 'Failed to create record';
		} finally {
			creating = false;
		}
	}
</script>

<div class="folder-page">
	<div class="folder-header">
		<h2 class="folder-title">{folder}</h2>
		<button class="new-btn" onclick={handleCreate} disabled={creating}>
			{creating ? 'Creating…' : '+ New record'}
		</button>
	</div>

	{#if createError}
		<p class="create-error">{createError}</p>
	{/if}

	{#if recordsStore.loading}
		<p class="loading">Loading…</p>
	{:else}
		<DataTable
			records={recordsStore.records}
			schema={schemaStore.schema}
			{folder}
			{colWidths}
		/>
	{/if}
</div>

<style>
	.folder-page {
		padding: 0;
	}
	.folder-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 16px;
	}
	.folder-title {
		margin: 0;
		font-size: 1.4rem;
		font-weight: 700;
		color: #111;
	}
	.new-btn {
		background: #6366f1;
		color: #fff;
		border: none;
		border-radius: 6px;
		padding: 6px 14px;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
	}
	.new-btn:hover:not(:disabled) {
		background: #4f46e5;
	}
	.new-btn:disabled {
		opacity: 0.6;
		cursor: default;
	}
	.create-error {
		color: #ef4444;
		font-size: 0.875rem;
		margin: 0 0 12px;
	}
	.loading {
		color: #9ca3af;
	}
</style>
