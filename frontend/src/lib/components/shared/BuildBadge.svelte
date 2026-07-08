<script lang="ts">
	import { onMount } from 'svelte';
	import { getBuildInfo, type BuildInfo } from '$lib/api/meta';

	let info = $state<BuildInfo | null>(null);
	let open = $state(false);

	onMount(async () => {
		try {
			info = await getBuildInfo();
		} catch {
			// Build info is non-essential; stay silent if the endpoint is unreachable.
		}
	});

	function formatDate(iso: string | null): string {
		if (!iso) return '—';
		const d = new Date(iso);
		return isNaN(d.getTime()) ? iso : d.toLocaleString();
	}
</script>

<svelte:window onkeydown={(e) => open && e.key === 'Escape' && (open = false)} />

{#if info}
	<button class="build-badge" title="About this build" onclick={() => (open = true)}>
		v{info.version}
	</button>
{/if}

{#if open && info}
	<div class="overlay" role="presentation" onclick={() => (open = false)}>
		<div class="about" role="dialog" aria-modal="true" aria-label="About this build" tabindex="-1" onclick={(e) => e.stopPropagation()}>
			<header>
				<h2>About</h2>
				<button class="close" aria-label="Close" onclick={() => (open = false)}>×</button>
			</header>
			<dl>
				<dt>Version</dt>
				<dd>{info.version}</dd>
				<dt>Commit</dt>
				<dd><code>{info.commit}</code></dd>
				<dt>Build date</dt>
				<dd>{formatDate(info.build_date)}</dd>
			</dl>
		</div>
	</div>
{/if}

<style>
	.build-badge {
		font: inherit;
		font-size: 12px;
		font-weight: 500;
		color: #64748b;
		background: transparent;
		border: none;
		padding: 3px 6px;
		border-radius: 6px;
		cursor: pointer;
	}
	.build-badge:hover {
		color: #334155;
		background: #f1f5f9;
	}

	.overlay {
		position: fixed;
		inset: 0;
		background: rgba(15, 23, 42, 0.35);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
	}
	.about {
		background: #fff;
		border-radius: 10px;
		box-shadow: 0 10px 40px rgba(0, 0, 0, 0.25);
		width: 320px;
		max-width: calc(100vw - 32px);
		padding: 16px 20px 20px;
	}
	.about header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 8px;
	}
	.about h2 {
		font-size: 15px;
		font-weight: 600;
		margin: 0;
	}
	.close {
		border: none;
		background: transparent;
		font-size: 20px;
		line-height: 1;
		color: #94a3b8;
		cursor: pointer;
	}
	.close:hover {
		color: #334155;
	}
	dl {
		display: grid;
		grid-template-columns: auto 1fr;
		gap: 6px 16px;
		margin: 0;
		font-size: 13px;
	}
	dt {
		color: #64748b;
	}
	dd {
		margin: 0;
		color: #0f172a;
		word-break: break-word;
	}
	code {
		font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
		font-size: 12px;
	}
</style>
