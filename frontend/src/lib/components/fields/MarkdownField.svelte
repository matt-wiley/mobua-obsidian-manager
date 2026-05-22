<script lang="ts">
	import { onDestroy } from 'svelte';
	import { marked } from 'marked';
	import { EditorView, keymap } from '@codemirror/view';
	import { EditorState } from '@codemirror/state';
	import { markdown } from '@codemirror/lang-markdown';
	import { defaultKeymap, history, historyKeymap } from '@codemirror/commands';

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
	let editorEl = $state<HTMLDivElement>();
	let view: EditorView | null = null;

	function startEdit() {
		if (readonly) return;
		editing = true;
	}

	function commit() {
		if (!view) return;
		const newValue = view.state.doc.toString();
		editing = false;
		if (newValue !== value) onSave(newValue);
	}

	// Mount CodeMirror whenever entering edit mode
	$effect(() => {
		if (!editing || !editorEl) return;

		view = new EditorView({
			state: EditorState.create({
				doc: value ?? '',
				extensions: [
					history(),
					keymap.of([
						...defaultKeymap,
						...historyKeymap,
						// Shift+Enter to save, plain Enter for newline
						{ key: 'Shift-Enter', run: () => { commit(); return true; } },
						{ key: 'Escape', run: () => { editing = false; return true; } }
					]),
					markdown(),
					EditorView.lineWrapping,
					EditorView.theme({
						'&': { minHeight: '120px', border: '1px solid #6366f1', borderRadius: '4px' },
						'.cm-content': { padding: '8px', fontFamily: 'inherit', fontSize: '14px' },
						'.cm-focused': { outline: 'none' }
					})
				]
			}),
			parent: editorEl
		});

		// Save on blur (focus leaving the editor wrapper entirely)
		const handleBlur = (e: FocusEvent) => {
			if (editorEl && e.relatedTarget instanceof Node && editorEl.contains(e.relatedTarget)) return;
			commit();
		};
		editorEl.addEventListener('focusout', handleBlur);

		// Focus the editor
		view.focus();

		return () => {
			editorEl?.removeEventListener('focusout', handleBlur);
			view?.destroy();
			view = null;
		};
	});

	onDestroy(() => view?.destroy());
</script>

{#if editing}
	<div class="editor-wrap">
		<div bind:this={editorEl}></div>
		<div class="editor-hint">Click away to save · Esc to cancel</div>
	</div>
{:else}
	<!-- svelte-ignore a11y_no_noninteractive_tabindex -->
	<div
		role={readonly ? undefined : 'button'}
		tabindex={readonly ? undefined : 0}
		onclick={startEdit}
		onkeydown={(e) => e.key === 'Enter' && startEdit()}
		class="field-view"
		class:editable={!readonly}
	>
		{#if value}
			<div class="markdown-body">{@html marked.parse(value)}</div>
		{:else}
			<span class="empty">Click to edit…</span>
		{/if}
	</div>
{/if}

<style>
	.editor-wrap {
		width: 100%;
	}
	.editor-hint {
		font-size: 11px;
		color: #9ca3af;
		margin-top: 4px;
		text-align: right;
	}
	.field-view {
		border-radius: 4px;
		padding: 4px;
	}
	.editable:hover {
		background: #f9fafb;
		cursor: text;
	}
	.markdown-body {
		font-size: 14px;
		line-height: 1.6;
	}
	.markdown-body :global(p) { margin: 0 0 0.5em; }
	.markdown-body :global(p:last-child) { margin-bottom: 0; }
	.markdown-body :global(h1) { margin: 0.75em 0 0.25em; font-weight: 600; }
	.markdown-body :global(h2) { margin: 0.75em 0 0.25em; font-weight: 600; }
	.markdown-body :global(h3) { margin: 0.75em 0 0.25em; font-weight: 600; }
	.markdown-body :global(h4) { margin: 0.75em 0 0.25em; font-weight: 600; }
	.markdown-body :global(ul) { margin: 0.25em 0; padding-left: 1.5em; }
	.markdown-body :global(ol) { margin: 0.25em 0; padding-left: 1.5em; }
	.markdown-body :global(code) { background: #f3f4f6; padding: 0.1em 0.3em; border-radius: 3px; font-size: 13px; }
	.markdown-body :global(pre) { background: #f3f4f6; padding: 0.75em; border-radius: 4px; overflow-x: auto; }
	.markdown-body :global(blockquote) { border-left: 3px solid #d1d5db; margin: 0.5em 0; padding-left: 0.75em; color: #6b7280; }
	.markdown-body :global(a) { color: #6366f1; text-decoration: underline; }
	.empty {
		color: #9ca3af;
		font-style: italic;
		font-size: 13px;
	}
</style>
