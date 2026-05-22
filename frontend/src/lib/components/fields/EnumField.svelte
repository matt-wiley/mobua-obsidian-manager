<script lang="ts">
	let {
		value,
		options = [],
		readonly = false,
		onSave
	}: {
		value: string;
		options?: string[];
		readonly?: boolean;
		onSave: (v: string) => void;
	} = $props();

	let editing = $state(false);
	let draft = $state('');

	function startEdit() {
		if (readonly) return;
		draft = value ?? '';
		editing = true;
	}

	function commit() {
		editing = false;
		if (draft !== value) onSave(draft);
	}

	function onKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') commit();
		if (e.key === 'Escape') editing = false;
	}

	// All options plus the current value (in case it's not in the list)
	let allOptions = $derived(() => {
		const set = new Set([...options]);
		if (value) set.add(value);
		return [...set];
	});
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
	>
		<option value="">—</option>
		{#each allOptions() as opt}
			<option value={opt}>{opt}</option>
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
		{#if value}
			<span class="pill">{value}</span>
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
	.pill {
		display: inline-block;
		padding: 1px 8px;
		border-radius: 99px;
		background: #e0e7ff;
		color: #3730a3;
		font-size: 0.85em;
		font-weight: 500;
	}
</style>
