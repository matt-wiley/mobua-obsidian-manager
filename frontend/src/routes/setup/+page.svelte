<script lang="ts">
	import { goto } from '$app/navigation';
	import { addVault } from '$lib/api/config';

	let vaultName = $state('My Vault');
	let vaultPath = $state('');
	let saving = $state(false);
	let error = $state<string | null>(null);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!vaultPath.trim()) return;
		saving = true;
		error = null;
		try {
			await addVault(vaultName.trim() || 'My Vault', vaultPath.trim());
			goto('/');
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to add vault';
		} finally {
			saving = false;
		}
	}
</script>

<div class="setup">
	<div class="card">
		<h1>Welcome to Obsidian Manager</h1>
		<p class="subtitle">Connect an Obsidian vault to get started.</p>

		<form onsubmit={handleSubmit}>
			<label for="vault-name">Workspace name</label>
			<input
				id="vault-name"
				type="text"
				bind:value={vaultName}
				placeholder="My Vault"
				disabled={saving}
				autocomplete="off"
			/>

			<label for="vault-path">Vault path</label>
			<input
				id="vault-path"
				type="text"
				bind:value={vaultPath}
				placeholder="/Users/you/Documents/MyVault"
				disabled={saving}
				autocomplete="off"
				spellcheck="false"
			/>

			{#if error}
				<p class="error">{error}</p>
			{/if}

			<button type="submit" disabled={saving || !vaultPath.trim()}>
				{saving ? 'Connecting…' : 'Connect vault'}
			</button>
		</form>
	</div>
</div>

<style>
	.setup {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 60vh;
	}
	.card {
		background: #fff;
		border: 1px solid #e5e7eb;
		border-radius: 12px;
		padding: 40px 48px;
		max-width: 480px;
		width: 100%;
	}
	h1 {
		margin: 0 0 8px;
		font-size: 1.5rem;
		font-weight: 700;
		color: #111;
	}
	.subtitle {
		margin: 0 0 28px;
		color: #6b7280;
		font-size: 0.95rem;
	}
	form {
		display: flex;
		flex-direction: column;
		gap: 10px;
	}
	label {
		font-size: 0.875rem;
		font-weight: 500;
		color: #374151;
	}
	input {
		padding: 9px 12px;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		font-size: 0.9rem;
		outline: none;
		transition: border-color 0.15s;
	}
	input[id="vault-path"] {
		font-family: monospace;
	}
	input:focus {
		border-color: #6366f1;
		box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
	}
	input:disabled {
		background: #f9fafb;
		color: #9ca3af;
	}
	button {
		margin-top: 6px;
		padding: 10px;
		background: #6366f1;
		color: #fff;
		border: none;
		border-radius: 6px;
		font-size: 0.9rem;
		font-weight: 500;
		cursor: pointer;
		transition: background 0.15s;
	}
	button:hover:not(:disabled) {
		background: #4f46e5;
	}
	button:disabled {
		opacity: 0.5;
		cursor: default;
	}
	.error {
		margin: 0;
		font-size: 0.85rem;
		color: #ef4444;
	}
</style>
