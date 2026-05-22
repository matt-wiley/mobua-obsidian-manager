<script lang="ts">
	import { onMount } from 'svelte';
	import { getFolders, type Folder } from '$lib/api/folders';

	let folders = $state<Folder[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	onMount(async () => {
		try {
			folders = await getFolders();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load folders';
		} finally {
			loading = false;
		}
	});
</script>

<div class="home">
	<h2 class="page-title">Vault</h2>

	{#if loading}
		<p class="state">Loading…</p>
	{:else if error}
		<p class="state error">{error}</p>
	{:else if folders.length === 0}
		<p class="state">No folders found. Add some <code>.md</code> files to your vault.</p>
	{:else}
		<div class="folder-grid">
			{#each folders as folder (folder.path)}
				<a class="folder-card" href="/{encodeURIComponent(folder.name)}">
					<span class="folder-name">{folder.name}</span>
					<span class="record-count">{folder.record_count} record{folder.record_count === 1 ? '' : 's'}</span>
				</a>
			{/each}
		</div>
	{/if}
</div>

<style>
	.home {
		max-width: 800px;
	}
	.page-title {
		margin: 0 0 20px;
		font-size: 1.4rem;
		font-weight: 700;
		color: #111;
	}
	.folder-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
		gap: 12px;
	}
	.folder-card {
		display: flex;
		flex-direction: column;
		gap: 6px;
		padding: 16px 20px;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		background: #fff;
		text-decoration: none;
		transition: border-color 0.15s, box-shadow 0.15s;
	}
	.folder-card:hover {
		border-color: #6366f1;
		box-shadow: 0 2px 8px rgba(99, 102, 241, 0.1);
	}
	.folder-name {
		font-size: 1rem;
		font-weight: 600;
		color: #111;
	}
	.record-count {
		font-size: 0.8rem;
		color: #9ca3af;
	}
	.state {
		color: #9ca3af;
	}
	.state.error {
		color: #ef4444;
	}
</style>
