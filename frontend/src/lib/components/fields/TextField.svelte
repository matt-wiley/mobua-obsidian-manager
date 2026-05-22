<script lang="ts">
	let {
		value,
		readonly = false,
		onSave
	}: {
		value: string;
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
</script>

{#if editing}
	<!-- svelte-ignore a11y_autofocus -->
	<input
		type="text"
		autofocus
		bind:value={draft}
		onblur={commit}
		onkeydown={onKeydown}
		class="field-input"
	/>
{:else}
	<!-- svelte-ignore a11y_no_noninteractive_tabindex -->
	<span
		role={readonly ? undefined : 'button'}
		tabindex={readonly ? undefined : 0}
		onclick={startEdit}
		onkeydown={(e) => e.key === 'Enter' && startEdit()}
		class="field-view"
		class:editable={!readonly}
	>{value ?? ''}</span>
{/if}

<style>
	.field-input {
		width: 100%;
		border: 1px solid #6366f1;
		border-radius: 4px;
		padding: 2px 6px;
		font: inherit;
		outline: none;
	}
	.field-view {
		display: block;
		min-height: 1.2em;
		padding: 2px 4px;
		border-radius: 4px;
		white-space: pre-wrap;
		word-break: break-word;
	}
	.editable:hover {
		background: #f3f4f6;
		cursor: text;
	}
</style>
