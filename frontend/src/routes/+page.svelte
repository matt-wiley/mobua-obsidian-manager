<script lang="ts">
	import { onMount } from 'svelte';
	import { getConfig, removeVault, type VaultInfo } from '$lib/api/config';

	let vaults = $state<VaultInfo[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let confirmingId = $state<string | null>(null);
	let removingId = $state<string | null>(null);

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

	async function handleRemove(id: string) {
		removingId = id;
		error = null;
		try {
			await removeVault(id);
			vaults = vaults.filter((v) => v.id !== id);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to remove workspace';
		} finally {
			removingId = null;
			confirmingId = null;
		}
	}
</script>

<div class="home">
	<h2 class="page-title">Workspaces</h2>

	{#if loading}
		<p class="state">Loading…</p>
	{:else if error}
		<p class="state error">{error}</p>
	{:else if vaults.length === 0}
		<p class="state">No workspaces configured yet.</p>
	{:else}
		<div class="vault-grid">
			{#each vaults as vault (vault.id)}
				<div class="vault-card">
					<a class="vault-link" href="/{encodeURIComponent(vault.id)}">
						<span class="vault-name">{vault.name}</span>
						<span class="vault-path">{vault.path}</span>
					</a>
					{#if confirmingId === vault.id}
						<div class="confirm" role="group" aria-label="Confirm removal">
							<span class="confirm-text">Remove?</span>
							<button
								type="button"
								class="confirm-yes"
								onclick={() => handleRemove(vault.id)}
								disabled={removingId === vault.id}
							>
								{removingId === vault.id ? 'Removing…' : 'Remove'}
							</button>
							<button
								type="button"
								class="confirm-no"
								onclick={() => (confirmingId = null)}
								disabled={removingId === vault.id}
							>
								Cancel
							</button>
						</div>
					{:else}
						<button
							type="button"
							class="remove-btn"
							title="Remove workspace"
							aria-label="Remove workspace {vault.name}"
							onclick={() => (confirmingId = vault.id)}
						>
							✕
						</button>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
	{#if !loading}
		<a class="add-link" href="/setup">＋ Add workspace</a>
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
		position: relative;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		background: #fff;
		transition: border-color 0.15s, box-shadow 0.15s;
	}
	.vault-card:hover {
		border-color: #6366f1;
		box-shadow: 0 2px 8px rgba(99, 102, 241, 0.1);
	}
	.vault-link {
		display: flex;
		flex-direction: column;
		gap: 6px;
		padding: 16px 20px;
		text-decoration: none;
	}
	.remove-btn {
		position: absolute;
		top: 8px;
		right: 8px;
		width: 22px;
		height: 22px;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0;
		border: none;
		border-radius: 4px;
		background: transparent;
		color: #9ca3af;
		font-size: 0.75rem;
		line-height: 1;
		cursor: pointer;
		opacity: 0;
		transition: opacity 0.15s, background 0.15s, color 0.15s;
	}
	.vault-card:hover .remove-btn,
	.remove-btn:focus-visible {
		opacity: 1;
	}
	.remove-btn:hover {
		background: #fee2e2;
		color: #ef4444;
	}
	.confirm {
		position: absolute;
		top: 8px;
		right: 8px;
		display: flex;
		align-items: center;
		gap: 6px;
		padding: 4px 6px;
		border-radius: 6px;
		background: #fff;
		box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
	}
	.confirm-text {
		font-size: 0.75rem;
		color: #6b7280;
	}
	.confirm button {
		padding: 2px 8px;
		border: none;
		border-radius: 4px;
		font-size: 0.75rem;
		cursor: pointer;
	}
	.confirm button:disabled {
		opacity: 0.6;
		cursor: default;
	}
	.confirm-yes {
		background: #ef4444;
		color: #fff;
	}
	.confirm-yes:hover:not(:disabled) {
		background: #dc2626;
	}
	.confirm-no {
		background: #f3f4f6;
		color: #374151;
	}
	.confirm-no:hover:not(:disabled) {
		background: #e5e7eb;
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
	.add-link {
		display: inline-block;
		margin-top: 16px;
		font-size: 0.875rem;
		color: #6366f1;
		text-decoration: none;
	}
	.add-link:hover {
		text-decoration: underline;
	}
	.state a {
		color: #6366f1;
	}
	.state.error {
		color: #ef4444;
	}
</style>
