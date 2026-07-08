<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import favicon from '$lib/assets/favicon.svg';
	import SyncBadge from '$lib/components/shared/SyncBadge.svelte';
	import BuildBadge from '$lib/components/shared/BuildBadge.svelte';
	import Drawer from '$lib/components/drawer/Drawer.svelte';
	import { syncStore } from '$lib/stores/sync.svelte';
	import { recordsStore } from '$lib/stores/records.svelte';
	import { apiFetch } from '$lib/api/client';
	import { getConfig, type VaultInfo } from '$lib/api/config';
	import { goto } from '$app/navigation';

	let { children } = $props();

	let repairMsg = $state<string | null>(null);
	let repairTimer: ReturnType<typeof setTimeout> | null = null;
	let vaults = $state<VaultInfo[]>([]);
	let switcherOpen = $state(false);

	async function handleRepair() {
		const vaultId = $page.params.vault;
		if (!vaultId) return;
		try {
			const result = await apiFetch<{ reindexed: number }>(`/vaults/${encodeURIComponent(vaultId)}/sync/repair`, { method: 'POST' });
			repairMsg = `Reindexed ${result.reindexed} files`;
		} catch {
			repairMsg = 'Repair failed';
		}
		if (repairTimer) clearTimeout(repairTimer);
		repairTimer = setTimeout(() => { repairMsg = null; }, 4000);
	}

	onMount(async () => {
		try {
			const config = await getConfig();
			if (config.vaults.length === 0 && $page.url.pathname !== '/setup') {
				goto('/setup');
				return;
			}
			vaults = config.vaults;
		} catch {
			// Backend unreachable — let each page handle its own error state
		}
	});

	onMount(() => {
		const es = new EventSource('/api/events');
		let errorTimer: ReturnType<typeof setTimeout> | null = null;

		es.onopen = () => {
			if (errorTimer) { clearTimeout(errorTimer); errorTimer = null; }
			syncStore.setConnected();
		};

		es.onerror = () => {
			if (!errorTimer) {
				errorTimer = setTimeout(() => syncStore.setReconnecting(), 3000);
			}
		};

		es.addEventListener('ping', () => syncStore.setConnected());

		es.onmessage = (e) => {
			syncStore.setConnected();
			const event = JSON.parse(e.data) as { type: string; folder_path: string; vault_id?: string };
			if (event.type === 'record_changed' || event.type === 'record_deleted') {
				if (event.vault_id && event.vault_id !== recordsStore.currentVaultId) return;
				const currentFolder = recordsStore.currentFolder;
				if (currentFolder && event.folder_path === currentFolder + '/') {
					recordsStore.invalidate();
				}
			}
		};

		return () => {
			if (errorTimer) clearTimeout(errorTimer);
			es.close();
		};
	});

	function closeSwitcher(e: MouseEvent) {
		if (!(e.target as HTMLElement).closest('.vault-switcher')) {
			switcherOpen = false;
		}
	}
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<svelte:document onclick={closeSwitcher} />

<div class="app-shell">
	<header>
		<a href="/" class="home-link">Obsidian Manager</a>

		{#if $page.params.vault}
			<div class="vault-switcher">
				<button class="switcher-btn" onclick={() => switcherOpen = !switcherOpen}>
					{vaults.find((v) => v.id === $page.params.vault)?.name ?? $page.params.vault}
					<span class="caret">▾</span>
				</button>
				{#if switcherOpen}
					<div class="switcher-dropdown">
						{#each vaults as v}
							<a
								class="switcher-item"
								class:active={v.id === $page.params.vault}
								href="/{encodeURIComponent(v.id)}"
								onclick={() => switcherOpen = false}
							>{v.name}</a>
						{/each}
						<a class="switcher-item add-item" href="/setup" onclick={() => switcherOpen = false}>＋ Add workspace</a>
					</div>
				{/if}
			</div>
		{/if}

		<SyncBadge />
		<BuildBadge />
	</header>

	<main>
		{@render children()}
	</main>

	<footer>
		{#if repairMsg}
			<span class="repair-msg">{repairMsg}</span>
		{/if}
		{#if $page.params.vault}
			<button class="repair-btn" onclick={handleRepair}>Repair index</button>
		{/if}
	</footer>
</div>

<Drawer />

<style>
	.app-shell {
		display: flex;
		flex-direction: column;
		height: 100vh;
		overflow: hidden;
		font-family: system-ui, sans-serif;
	}
	header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 10px 20px;
		border-bottom: 1px solid #e5e7eb;
		background: #fff;
		gap: 12px;
	}
	.home-link {
		font-weight: 600;
		text-decoration: none;
		color: #111;
	}
	.vault-switcher {
		position: relative;
		flex: 1;
	}
	.switcher-btn {
		background: none;
		border: 1px solid #e5e7eb;
		border-radius: 6px;
		padding: 4px 10px;
		font-size: 0.875rem;
		font-weight: 500;
		color: #374151;
		cursor: pointer;
		display: flex;
		align-items: center;
		gap: 6px;
	}
	.switcher-btn:hover {
		border-color: #6366f1;
		color: #111;
	}
	.caret {
		font-size: 0.7rem;
		color: #9ca3af;
	}
	.switcher-dropdown {
		position: absolute;
		top: calc(100% + 4px);
		left: 0;
		min-width: 180px;
		background: #fff;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
		z-index: 100;
		overflow: hidden;
	}
	.switcher-item {
		display: block;
		padding: 8px 14px;
		font-size: 0.875rem;
		color: #374151;
		text-decoration: none;
	}
	.switcher-item:hover {
		background: #f3f4f6;
	}
	.switcher-item.active {
		color: #6366f1;
		font-weight: 600;
	}
	.add-item {
		border-top: 1px solid #f3f4f6;
		color: #6366f1;
	}
	main {
		flex: 1;
		padding: 20px;
		overflow: hidden;
		display: flex;
		flex-direction: column;
		min-height: 0;
	}
	footer {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		gap: 12px;
		padding: 8px 20px;
		border-top: 1px solid #f3f4f6;
		background: #fff;
	}
	.repair-btn {
		background: none;
		border: none;
		cursor: pointer;
		font-size: 0.75rem;
		color: #9ca3af;
		padding: 2px 6px;
		border-radius: 4px;
	}
	.repair-btn:hover {
		color: #6b7280;
		background: #f3f4f6;
	}
	.repair-msg {
		font-size: 0.75rem;
		color: #6b7280;
	}
</style>
