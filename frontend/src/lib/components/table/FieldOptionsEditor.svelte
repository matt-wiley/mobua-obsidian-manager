<script lang="ts">
	import { getFieldOptions, setFieldOptions, deleteFieldOptions } from '$lib/api/folders';

	let {
		vault,
		folder,
		field,
		initialOptions = [],
		onClose,
		onSaved
	}: {
		vault: string;
		folder: string;
		field: string;
		/** Currently-visible options (merged/detected) — used to seed an unconfigured field. */
		initialOptions?: string[];
		onClose: () => void;
		onSaved: () => void;
	} = $props();

	let options = $state<string[]>([]);
	let configured = $state(false);
	let loading = $state(true);
	let saving = $state(false);

	$effect(() => {
		let cancelled = false;
		getFieldOptions(vault, folder).then((all) => {
			if (cancelled) return;
			const canonical = all[field];
			if (canonical && canonical.length) {
				options = [...canonical];
				configured = true;
			} else {
				options = [...initialOptions];
				configured = false;
			}
			loading = false;
		});
		return () => { cancelled = true; };
	});

	function addOption() {
		options = [...options, ''];
	}
	function removeOption(i: number) {
		options = options.filter((_, idx) => idx !== i);
	}
	function updateOption(i: number, value: string) {
		options = options.map((o, idx) => (idx === i ? value : o));
	}
	function move(i: number, delta: number) {
		const j = i + delta;
		if (j < 0 || j >= options.length) return;
		const next = [...options];
		[next[i], next[j]] = [next[j], next[i]];
		options = next;
	}

	async function save() {
		saving = true;
		try {
			const cleaned = options.map((o) => o.trim()).filter((o) => o.length > 0);
			// De-duplicate, preserving order.
			const unique = [...new Set(cleaned)];
			await setFieldOptions(vault, folder, field, unique);
			onSaved();
			onClose();
		} finally {
			saving = false;
		}
	}

	async function clearConfig() {
		saving = true;
		try {
			await deleteFieldOptions(vault, folder, field);
			onSaved();
			onClose();
		} finally {
			saving = false;
		}
	}

	function onKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') onClose();
	}
</script>

<svelte:window onkeydown={onKeydown} />

<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
<div class="overlay" onclick={onClose}>
	<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
	<div class="modal" role="dialog" tabindex="-1" aria-label="Edit field options" onclick={(e) => e.stopPropagation()}>
		<header class="modal-header">
			<h3>Options for <span class="field-name">{field}</span></h3>
			<button class="close-btn" onclick={onClose} aria-label="Close">✕</button>
		</header>

		{#if loading}
			<p class="hint">Loading…</p>
		{:else}
			{#if !configured}
				<p class="hint">
					No fixed list yet — seeded from existing values. Saving pins these options so
					they stay selectable even when no record uses them.
				</p>
			{/if}

			<ul class="option-list">
				{#each options as opt, i (i)}
					<li class="option-row">
						<div class="reorder">
							<button class="mv" onclick={() => move(i, -1)} disabled={i === 0} aria-label="Move up">▲</button>
							<button class="mv" onclick={() => move(i, 1)} disabled={i === options.length - 1} aria-label="Move down">▼</button>
						</div>
						<input
							class="option-input"
							value={opt}
							placeholder="Option value"
							oninput={(e) => updateOption(i, (e.currentTarget as HTMLInputElement).value)}
						/>
						<button class="remove-btn" onclick={() => removeOption(i)} aria-label="Remove option">✕</button>
					</li>
				{/each}
				{#if options.length === 0}
					<li class="empty-hint">No options. Add one below.</li>
				{/if}
			</ul>

			<button class="add-btn" onclick={addOption}>+ Add option</button>

			<footer class="modal-footer">
				{#if configured}
					<button class="clear-btn" onclick={clearConfig} disabled={saving}>
						Clear fixed list
					</button>
				{/if}
				<div class="footer-actions">
					<button class="cancel-btn" onclick={onClose} disabled={saving}>Cancel</button>
					<button class="save-btn" onclick={save} disabled={saving}>
						{saving ? 'Saving…' : 'Save'}
					</button>
				</div>
			</footer>
		{/if}
	</div>
</div>

<style>
	.overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.35);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
	}
	.modal {
		background: #fff;
		border-radius: 8px;
		box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
		width: 420px;
		max-width: calc(100vw - 32px);
		max-height: calc(100vh - 64px);
		display: flex;
		flex-direction: column;
		padding: 16px;
	}
	.modal-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 8px;
	}
	.modal-header h3 {
		margin: 0;
		font-size: 1rem;
		font-weight: 600;
		color: #111827;
	}
	.field-name {
		font-family: ui-monospace, monospace;
		color: #6366f1;
	}
	.close-btn {
		background: none;
		border: none;
		cursor: pointer;
		color: #9ca3af;
		font-size: 0.875rem;
		padding: 2px 4px;
		border-radius: 4px;
		line-height: 1;
	}
	.close-btn:hover {
		color: #374151;
		background: #f3f4f6;
	}
	.hint {
		color: #6b7280;
		font-size: 0.8125rem;
		margin: 0 0 10px;
		line-height: 1.4;
	}
	.option-list {
		list-style: none;
		margin: 0 0 8px;
		padding: 0;
		overflow-y: auto;
	}
	.option-row {
		display: flex;
		align-items: center;
		gap: 6px;
		padding: 3px 0;
	}
	.reorder {
		display: flex;
		flex-direction: column;
		gap: 1px;
	}
	.mv {
		background: none;
		border: 1px solid #e5e7eb;
		border-radius: 3px;
		cursor: pointer;
		font-size: 7px;
		line-height: 1;
		color: #9ca3af;
		padding: 1px 3px;
	}
	.mv:hover:not(:disabled) {
		background: #f3f4f6;
		color: #374151;
	}
	.mv:disabled {
		opacity: 0.3;
		cursor: default;
	}
	.option-input {
		flex: 1;
		border: 1px solid #e5e7eb;
		border-radius: 4px;
		font-size: 0.875rem;
		color: #374151;
		padding: 4px 8px;
		min-width: 0;
	}
	.option-input:focus {
		outline: none;
		border-color: #6366f1;
		box-shadow: 0 0 0 2px #eef2ff;
	}
	.remove-btn {
		background: none;
		border: none;
		cursor: pointer;
		color: #9ca3af;
		font-size: 0.75rem;
		padding: 2px 4px;
		border-radius: 4px;
		line-height: 1;
	}
	.remove-btn:hover {
		color: #ef4444;
		background: #fee2e2;
	}
	.empty-hint {
		color: #9ca3af;
		font-size: 0.8125rem;
		padding: 4px 0;
	}
	.add-btn {
		background: none;
		border: none;
		cursor: pointer;
		font-size: 0.8125rem;
		color: #6366f1;
		padding: 2px 4px;
		border-radius: 4px;
		align-self: flex-start;
	}
	.add-btn:hover {
		background: #eef2ff;
	}
	.modal-footer {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-top: 14px;
		gap: 8px;
	}
	.footer-actions {
		display: flex;
		gap: 8px;
		margin-left: auto;
	}
	.clear-btn {
		background: none;
		border: 1px solid #fca5a5;
		color: #b91c1c;
		cursor: pointer;
		font-size: 0.8125rem;
		padding: 5px 10px;
		border-radius: 6px;
	}
	.clear-btn:hover:not(:disabled) {
		background: #fee2e2;
	}
	.cancel-btn {
		background: none;
		border: 1px solid #e5e7eb;
		color: #6b7280;
		cursor: pointer;
		font-size: 0.8125rem;
		padding: 5px 12px;
		border-radius: 6px;
	}
	.cancel-btn:hover:not(:disabled) {
		background: #f3f4f6;
	}
	.save-btn {
		background: #6366f1;
		color: #fff;
		border: none;
		cursor: pointer;
		font-size: 0.8125rem;
		padding: 5px 14px;
		border-radius: 6px;
	}
	.save-btn:hover:not(:disabled) {
		background: #4f46e5;
	}
	.save-btn:disabled,
	.clear-btn:disabled,
	.cancel-btn:disabled {
		opacity: 0.6;
		cursor: default;
	}
</style>
