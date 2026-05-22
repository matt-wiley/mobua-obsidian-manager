<script lang="ts">
	import { page } from '$app/stores';
	import { get } from 'svelte/store';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { recordsStore } from '$lib/stores/records.svelte';
	import { schemaStore } from '$lib/stores/schema.svelte';
	import { deleteRecord } from '$lib/api/records';
	import PageView from '$lib/components/page/PageView.svelte';

	const vault = get(page).params.vault as string;
	const folder = get(page).params.folder as string;
	const filename = decodeURIComponent(get(page).params.record as string);

	let deleting = $state(false);

	onMount(async () => {
		await Promise.all([
			recordsStore.load(vault, folder),
			schemaStore.load(vault, folder)
		]);
	});

	const record = $derived(
		recordsStore.records.find((r) => r.filename === filename)
	);

	async function handleDelete() {
		if (!record) return;
		const confirmed = confirm(`Delete "${record.filename}"? This cannot be undone.`);
		if (!confirmed) return;
		deleting = true;
		try {
			await deleteRecord(vault, record.id);
			await goto(`/${encodeURIComponent(vault)}/${encodeURIComponent(folder)}`);
		} finally {
			deleting = false;
		}
	}
</script>

<div class="page-container">
	<nav class="breadcrumb">
		<a href="/{encodeURIComponent(vault)}/{encodeURIComponent(folder)}">{folder}</a>
		<span class="sep">›</span>
		<span>{filename}</span>

		<button
			class="delete-btn"
			onclick={handleDelete}
			disabled={deleting || !record}
			title="Delete this record"
		>
			{deleting ? '…' : '🗑'}
		</button>
	</nav>

	{#if recordsStore.loading}
		<p class="loading">Loading…</p>
	{:else if record}
		<PageView {record} schema={schemaStore.schema} />
	{:else}
		<p class="not-found">Record "{filename}" not found in {folder}.</p>
	{/if}
</div>

<style>
	.page-container {
		max-width: 800px;
	}
	.breadcrumb {
		display: flex;
		align-items: center;
		gap: 6px;
		margin-bottom: 24px;
		font-size: 0.9rem;
		color: #6b7280;
	}
	.breadcrumb a {
		color: #6366f1;
		text-decoration: none;
	}
	.breadcrumb a:hover {
		text-decoration: underline;
	}
	.sep {
		color: #d1d5db;
	}
	.delete-btn {
		margin-left: auto;
		background: none;
		border: none;
		cursor: pointer;
		font-size: 1rem;
		padding: 2px 6px;
		border-radius: 4px;
		opacity: 0.5;
	}
	.delete-btn:hover:not(:disabled) {
		background: #fee2e2;
		opacity: 1;
	}
	.delete-btn:disabled {
		cursor: default;
	}
	.loading,
	.not-found {
		color: #9ca3af;
	}
</style>
