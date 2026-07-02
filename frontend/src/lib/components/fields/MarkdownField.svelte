<script lang="ts">
	import { onDestroy } from 'svelte';
	import { marked } from 'marked';
	import hljs from 'highlight.js';
	import { EditorView, keymap } from '@codemirror/view';
	import { EditorState } from '@codemirror/state';
	import { markdown } from '@codemirror/lang-markdown';
	import { defaultKeymap, history, historyKeymap } from '@codemirror/commands';

	marked.use({
		renderer: {
			code({ text, lang }) {
				const language = lang && hljs.getLanguage(lang) ? lang : 'plaintext';
				const highlighted = hljs.highlight(text, { language }).value;
				return `<pre><code class="hljs language-${language}">${highlighted}</code></pre>`;
			}
		}
	});

	let {
		value,
		readonly = false,
		onSave
	}: {
		value: string;
		readonly?: boolean;
		onSave: (v: string) => void;
	} = $props();

	const MIN_EDIT_HEIGHT = 60;
	const MAX_EDIT_HEIGHT = 380;

	let editing = $state(false);
	let editorEl = $state<HTMLDivElement>();
	let fieldViewEl = $state<HTMLElement>();
	let view: EditorView | null = null;

	// The read view is the source of truth for height; the editor conforms to
	// whatever the rendered markdown last measured, so switching modes doesn't
	// visibly resize the field. A ResizeObserver (not just value/editing
	// changes) is required because layout reflows — window resize, dragging
	// the column splitter, the 1/2-col layout toggle — don't touch any
	// reactive state the effect would otherwise re-run on.
	let measuredHeight = $state<number | null>(null);

	$effect(() => {
		if (!fieldViewEl || editing) return;
		const el = fieldViewEl;

		const measure = () => { measuredHeight = el.offsetHeight; };
		measure();

		const observer = new ResizeObserver(measure);
		observer.observe(el);

		if (value) {
			const parent = el.parentElement;
			if (parent) requestAnimationFrame(() => { parent.scrollTop = parent.scrollHeight; });
		}

		return () => observer.disconnect();
	});

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

		const editHeight = Math.min(
			Math.max(measuredHeight ?? MIN_EDIT_HEIGHT, MIN_EDIT_HEIGHT),
			MAX_EDIT_HEIGHT
		);

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
						'&': { height: `${editHeight}px`, border: '1px solid #6366f1', borderRadius: '4px', boxSizing: 'border-box' },
						'.cm-scroller': { overflow: 'auto' },
						'.cm-content': { padding: '4px', fontFamily: 'inherit', fontSize: '14px', lineHeight: '1.6' },
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

		// Focus and scroll to bottom
		view.focus();
		view.dispatch({ effects: EditorView.scrollIntoView(view.state.doc.length) });

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
		bind:this={fieldViewEl}
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
	@import 'highlight.js/styles/github.css';

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
		border: 1px solid transparent;
		border-radius: 4px;
		padding: 4px;
		box-sizing: border-box;
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
	.markdown-body :global(pre) { background: #f6f8fa; padding: 0; border-radius: 6px; overflow-x: auto; }
	.markdown-body :global(pre code.hljs) { background: transparent; padding: 0.75em; border-radius: 6px; font-size: 13px; }
	.markdown-body :global(blockquote) { border-left: 3px solid #d1d5db; margin: 0.5em 0; padding-left: 0.75em; color: #6b7280; }
	.markdown-body :global(a) { color: #6366f1; text-decoration: underline; }
	.empty {
		color: #9ca3af;
		font-style: italic;
		font-size: 13px;
	}
</style>
