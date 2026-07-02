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

	const vault = get(page).params.vault as string;
	const folder = get(page).params.folder as string;
	let quickSearch = $state('');
	let colWidths = $state<Record<string, number>>({});
	let ready = $state(false);
	let creating = $state(false);
	let createError = $state<string | null>(null);

	onMount(async () => {
		await Promise.all([
			recordsStore.load(vault, folder),
			schemaStore.load(vault, folder),
			getColWidths(vault, folder).then((w) => { colWidths = w; })
		]);
		ready = true;
	});

	async function handleCreate() {
		creating = true;
		createError = null;
		try {
			let name = 'Untitled';
			let n = 2;
			while (n <= 20) {
				try {
					const record = await createRecord(vault, folder, { filename: name });
					await goto(`/${encodeURIComponent(vault)}/${encodeURIComponent(folder)}/${encodeURIComponent(record.filename)}`);
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
		<div class="search-wrap">
			<input
				class="search-input"
				type="text"
				placeholder="Search…"
				bind:value={quickSearch}
			/>
			{#if quickSearch}
				<button
					class="search-clear"
					aria-label="Clear search"
					onclick={() => (quickSearch = '')}
				>×</button>
			{/if}
		</div>
		<button class="new-btn" onclick={handleCreate} disabled={creating}>
			{creating ? 'Creating…' : '+ New record'}
		</button>
	</div>

	{#if createError}
		<p class="create-error">{createError}</p>
	{/if}

	<div class="table-container">
		{#if !ready}
			<p class="loading">Loading…</p>
		{:else}
			<DataTable
				records={recordsStore.records}
				schema={schemaStore.schema}
				{vault}
				{folder}
				{colWidths}
				{quickSearch}
			/>
		{/if}
	</div>
</div>

<style>
	.folder-page {
		padding: 0;
		flex: 1;
		display: flex;
		flex-direction: column;
		min-height: 0;
		overflow: hidden;
	}
	.table-container {
		flex: 1;
		display: flex;
		flex-direction: column;
		min-height: 0;
		overflow: hidden;
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
	.search-wrap {
		position: relative;
		flex: 1;
		max-width: 360px;
		margin: 0 16px;
	}
	.search-input {
		width: 100%;
		box-sizing: border-box;
		padding: 6px 28px 6px 10px;
		font-size: 0.875rem;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		outline: none;
	}
	.search-input:focus {
		border-color: #6366f1;
	}
	.search-clear {
		position: absolute;
		right: 6px;
		top: 50%;
		transform: translateY(-50%);
		border: none;
		background: none;
		color: #9ca3af;
		font-size: 1rem;
		line-height: 1;
		cursor: pointer;
		padding: 2px 4px;
	}
	.search-clear:hover {
		color: #374151;
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
