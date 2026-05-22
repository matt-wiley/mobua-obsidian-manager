<script lang="ts">
	import { goto } from '$app/navigation';
	import type { VaultRecord } from '$lib/api/records';
	import { drawerStore } from '$lib/stores/drawer.svelte';

	let {
		label,
		record
	}: {
		label: string;
		record?: VaultRecord;
	} = $props();

	function handleClick(e: MouseEvent) {
		e.preventDefault();
		e.stopPropagation();

		if (!record) return;

		const isModified = e.metaKey || e.ctrlKey;
		if (isModified) {
			const folder = record.folder_path.replace(/\/$/, '');
			goto(`/${encodeURIComponent(folder)}/${encodeURIComponent(record.filename)}`);
			return;
		}

		if (drawerStore.open) {
			drawerStore.replace(record);
		} else {
			drawerStore.push(record);
		}
	}
</script>

<span
	role="link"
	tabindex="0"
	class="wikilink"
	class:resolved={!!record}
	onclick={handleClick}
	onkeydown={(e) => e.key === 'Enter' && handleClick(e as unknown as MouseEvent)}
	title={record ? `${record.folder_path}${record.filename}` : label}
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
