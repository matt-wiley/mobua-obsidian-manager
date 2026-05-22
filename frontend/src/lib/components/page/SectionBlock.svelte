<script lang="ts">
	import MarkdownField from '$lib/components/fields/MarkdownField.svelte';

	let {
		title,
		content,
		onSaveContent,
		onSaveTitle
	}: {
		title: string;
		content: string;
		onSaveContent: (v: string) => void;
		onSaveTitle: (v: string) => void;
	} = $props();

	let editingTitle = $state(false);
	let titleDraft = $state('');

	function startEdit() {
		titleDraft = title;
		editingTitle = true;
	}

	function commit() {
		editingTitle = false;
		if (titleDraft.trim() && titleDraft !== title) {
			onSaveTitle(titleDraft.trim());
		}
	}

	function onKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') commit();
		if (e.key === 'Escape') editingTitle = false;
	}
</script>

<div class="section-block">
	{#if editingTitle}
		<!-- svelte-ignore a11y_autofocus -->
		<input
			class="title-input"
			type="text"
			autofocus
			bind:value={titleDraft}
			onblur={commit}
			onkeydown={onKeydown}
		/>
	{:else}
		<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_noninteractive_element_interactions -->
		<h2 class="section-title" onclick={startEdit}>{title}</h2>
	{/if}

	<MarkdownField value={content} onSave={onSaveContent} />
</div>

<style>
	.section-block {
		margin-top: 24px;
	}
	.section-title {
		margin: 0 0 8px;
		font-size: 1.1rem;
		font-weight: 600;
		color: #374151;
		cursor: pointer;
		border-radius: 4px;
		padding: 2px 4px;
	}
	.section-title:hover {
		background: #f3f4f6;
	}
	.title-input {
		width: 100%;
		font-size: 1.1rem;
		font-weight: 600;
		color: #374151;
		border: 1px solid #6366f1;
		border-radius: 4px;
		padding: 2px 6px;
		margin-bottom: 8px;
		font-family: inherit;
		outline: none;
		box-sizing: border-box;
	}
</style>
