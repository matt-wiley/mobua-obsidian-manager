<script lang="ts">
	import { goto } from '$app/navigation';
	import type { VaultRecord } from '$lib/api/records';
	import { drawerStore } from '$lib/stores/drawer.svelte';
	import { recordsStore } from '$lib/stores/records.svelte';

	let {
		label,
		record
	}: {
		label: string;
		record?: VaultRecord;
	} = $props();

	// Resolve the record from the store if not explicitly provided
	const resolvedRecord = $derived(
		record ?? recordsStore.records.find((r) => r.filename === label)
	);

	function handleClick(e: MouseEvent) {
		e.preventDefault();
		e.stopPropagation();

		if (!resolvedRecord) return;

		const isModified = e.metaKey || e.ctrlKey;
		if (isModified) {
			const vaultId = recordsStore.currentVaultId;
			const folder = resolvedRecord.folder_path.replace(/\/$/, '');
			goto(`/${encodeURIComponent(vaultId!)}/${encodeURIComponent(folder)}/${encodeURIComponent(resolvedRecord.filename)}`);
			return;
		}

		if (drawerStore.open) {
			drawerStore.replace(resolvedRecord);
		} else {
			drawerStore.push(resolvedRecord);
		}
	}
</script>

<span
	role="link"
	tabindex="0"
	class="wikilink"
	class:resolved={!!resolvedRecord}
	onclick={handleClick}
	onkeydown={(e) => e.key === 'Enter' && handleClick(e as unknown as MouseEvent)}
	title={resolvedRecord ? `${resolvedRecord.folder_path}${resolvedRecord.filename}` : label}
>
	{label}
</span>

<style>
	.wikilink {
		color: #4f46e5;
		cursor: default;
		border-radius: 3px;
		padding: 0 2px;
	}
	.resolved {
		cursor: pointer;
		text-decoration: underline dotted;
	}
	.resolved:hover {
		background: #eef2ff;
		text-decoration: underline;
	}
</style>
