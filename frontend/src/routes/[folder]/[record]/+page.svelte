<script lang="ts">
	import { page } from '$app/stores';
	import { get } from 'svelte/store';
	import { onMount } from 'svelte';
	import { recordsStore } from '$lib/stores/records.svelte';
	import { schemaStore } from '$lib/stores/schema.svelte';
	import PageView from '$lib/components/page/PageView.svelte';

	const folder = get(page).params.folder as string;
	const filename = decodeURIComponent(get(page).params.record as string);

	onMount(async () => {
		await Promise.all([
			recordsStore.load(folder),
			schemaStore.load(folder)
		]);
	});

	const record = $derived(
		recordsStore.records.find((r) => r.filename === filename)
	);
</script>

<div class="page-container">
	<nav class="breadcrumb">
		<a href="/{folder}">{folder}</a>
		<span class="sep">›</span>
		<span>{filename}</span>
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
	.loading,
	.not-found {
		color: #9ca3af;
	}
</style>
