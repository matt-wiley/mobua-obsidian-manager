<script lang="ts">
	import WikiLink from '$lib/components/shared/WikiLink.svelte';
	import type { RelationOption, VaultRecord } from '$lib/api/records';
	import { getRelations } from '$lib/api/records';
	import { recordsStore } from '$lib/stores/records.svelte';

	let {
		value,
		recordId,
		fieldName,
		readonly = false,
		onSave
	}: {
		value: string;
		recordId: string;
		fieldName: string;
		readonly?: boolean;
		onSave: (v: string) => void;
	} = $props();

	let editing = $state(false);
	let draft = $state('');
	let options = $state<RelationOption[]>([]);
	let loading = $state(false);

	// Strip [[ ]] from the stored value for display
	let displayLabel = $derived(() => value?.replace(/^\[\[|\]\]$/g, '') ?? '');

	async function startEdit() {
		if (readonly) return;
		draft = displayLabel();
		editing = true;
		loading = true;
		try {
			options = await getRelations(recordsStore.currentVaultId!, recordId, fieldName);
		} finally {
			loading = false;
		}
	}

	function commit() {
		editing = false;
		if (!draft) {
			if (value) onSave('');
			return;
		}
		const newValue = `[[${draft}]]`;
		if (newValue !== value) onSave(newValue);
	}

	function onKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') commit();
		if (e.key === 'Escape') editing = false;
	}
</script>

{#if editing}
	<!-- svelte-ignore a11y_autofocus -->
	<select
		autofocus
		bind:value={draft}
		onblur={commit}
		onkeydown={onKeydown}
		onchange={commit}
		class="field-select"
		disabled={loading}
	>
		<option value="">—</option>
		{#each options as opt}
			<option value={opt.filename}>{opt.filename}</option>
		{/each}
	</select>
{:else}
	<!-- svelte-ignore a11y_no_noninteractive_tabindex -->
	<span
		role={readonly ? undefined : 'button'}
		tabindex={readonly ? undefined : 0}
		onclick={startEdit}
		onkeydown={(e) => e.key === 'Enter' && startEdit()}
		class="field-view"
		class:editable={!readonly}
	>
		{#if displayLabel()}
			<WikiLink label={displayLabel()} />
		{/if}
	</span>
{/if}

<style>
	.field-select {
		width: 100%;
		border: 1px solid #6366f1;
		border-radius: 4px;
		padding: 2px 6px;
		font: inherit;
		outline: none;
		background: white;
	}
	.field-view {
		display: block;
		padding: 2px 4px;
		border-radius: 4px;
	}
	.editable:hover {
		background: #f3f4f6;
		cursor: pointer;
	}
</style>
