<script lang="ts">
	import { page } from '$app/stores';
	import { get } from 'svelte/store';
	import { onMount } from 'svelte';
	import { recordsStore } from '$lib/stores/records.svelte';
	import { schemaStore } from '$lib/stores/schema.svelte';
	import { getColWidths } from '$lib/api/folders';
	import DataTable from '$lib/components/table/DataTable.svelte';

	// folder is always defined on this route
	const folder = get(page).params.folder as string;
	let colWidths = $state<Record<string, number>>({});

	onMount(async () => {
		await Promise.all([
			recordsStore.load(folder),
			schemaStore.load(folder),
			getColWidths(folder).then((w) => { colWidths = w; })
		]);
	});
</script>

<div class="folder-page">
	<h2 class="folder-title">{folder as string}</h2>

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
	.folder-title {
		margin: 0 0 16px;
		font-size: 1.4rem;
		font-weight: 700;
		color: #111;
	}
	.loading {
		color: #9ca3af;
	}
</style>
