<script lang="ts">
	import { onMount } from 'svelte';
	import { getConfig, type VaultInfo } from '$lib/api/config';

	let vaults = $state<VaultInfo[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	onMount(async () => {
		try {
			const config = await getConfig();
			vaults = config.vaults;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load workspaces';
		} finally {
			loading = false;
		}
	});
</script>

<div class="home">
	<h2 class="page-title">Workspaces</h2>

	{#if loading}
		<p class="state">Loading…</p>
	{:else if error}
		<p class="state error">{error}</p>
	{:else if vaults.length === 0}
		<p class="state">No workspaces configured. <a href="/setup">Add one</a>.</p>
	{:else}
		<div class="vault-grid">
			{#each vaults as vault (vault.id)}
				<a class="vault-card" href="/{encodeURIComponent(vault.id)}">
					<span class="vault-name">{vault.name}</span>
					<span class="vault-path">{vault.path}</span>
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
	.vault-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
		gap: 12px;
	}
	.vault-card {
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
	.vault-card:hover {
		border-color: #6366f1;
		box-shadow: 0 2px 8px rgba(99, 102, 241, 0.1);
	}
	.vault-name {
		font-size: 1rem;
		font-weight: 600;
		color: #111;
	}
	.vault-path {
		font-size: 0.8rem;
		color: #9ca3af;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.state {
		color: #9ca3af;
	}
	.state a {
		color: #6366f1;
	}
	.state.error {
		color: #ef4444;
	}
</style>
