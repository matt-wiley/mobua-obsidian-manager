<script lang="ts">
	import { drawerStore } from '$lib/stores/drawer.svelte';
	import { recordsStore } from '$lib/stores/records.svelte';
	import { getFolderSchema } from '$lib/api/folders';
	import type { SchemaField } from '$lib/api/folders';
	import PageView from '$lib/components/page/PageView.svelte';
	import Breadcrumb from './Breadcrumb.svelte';
	import SettingsPanel from './SettingsPanel.svelte';

	// Load schema when the drawer's record folder changes
	let drawerSchema = $state<SchemaField[]>([]);
	let loadedFolder = $state<string | null>(null);

	$effect(() => {
		const record = drawerStore.record;
		if (!record) return;
		const folder = record.folder_path.replace(/\/$/, '');
		if (folder === loadedFolder) return;
		loadedFolder = folder;
		getFolderSchema(recordsStore.currentVaultId!, folder).then((s) => { drawerSchema = s; });
	});

	// Use the live record from recordsStore when available (same folder),
	// otherwise fall back to the snapshot in drawerStore.
	const liveRecord = $derived(
		drawerStore.record
			? (recordsStore.records.find((r) => r.id === drawerStore.record!.id) ??
					drawerStore.record)
			: null
	);

	function onKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape' && drawerStore.open) drawerStore.close();
	}
</script>

<svelte:window onkeydown={onKeydown} />

{#if drawerStore.open}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="backdrop" onclick={() => drawerStore.close()}></div>
{/if}

<div
	class="drawer"
	class:open={drawerStore.open}
	aria-hidden={!drawerStore.open}
	aria-label={drawerStore.mode === 'settings' ? 'Settings drawer' : 'Record drawer'}
>
	<div class="drawer-header">
		{#if drawerStore.mode === 'settings'}
			<span class="drawer-title">Settings</span>
		{:else}
			<Breadcrumb />
		{/if}
		<button class="close-btn" onclick={() => drawerStore.close()} aria-label="Close drawer">
			✕
		</button>
	</div>
	<div class="drawer-body">
		{#if drawerStore.mode === 'settings'}
			<SettingsPanel />
		{:else if liveRecord}
			<PageView record={liveRecord} schema={drawerSchema} />
		{/if}
	</div>
</div>

<style>
	.backdrop {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.15);
		z-index: 40;
	}
	.drawer {
		position: fixed;
		top: 0;
		right: 0;
		height: 100vh;
		width: 480px;
		max-width: 92vw;
		background: #fff;
		border-left: 1px solid #e5e7eb;
		box-shadow: -4px 0 24px rgba(0, 0, 0, 0.08);
		z-index: 50;
		display: flex;
		flex-direction: column;
		transform: translateX(100%);
		transition: transform 0.2s ease;
		font-family: system-ui, sans-serif;
		/* Always in the DOM so the transition plays */
	}
	.drawer.open {
		transform: translateX(0);
	}
	.drawer-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 10px 16px;
		border-bottom: 1px solid #e5e7eb;
		min-height: 48px;
		gap: 8px;
		flex-shrink: 0;
	}
	.drawer-title {
		font-size: 0.9rem;
		font-weight: 600;
		color: #111;
	}
	.drawer-body {
		flex: 1;
		overflow-y: auto;
		padding: 20px 20px 48px;
	}
	.close-btn {
		background: none;
		border: none;
		cursor: pointer;
		font-size: 1rem;
		color: #6b7280;
		padding: 4px 8px;
		border-radius: 4px;
		flex-shrink: 0;
		line-height: 1;
	}
	.close-btn:hover {
		background: #f3f4f6;
		color: #111;
	}
</style>
