<script lang="ts">
	import { onMount } from 'svelte';
	import { getBuildInfo, type BuildInfo } from '$lib/api/meta';
	import hljs from 'highlight.js';
	import { settingsStore, HLJS_THEMES } from '$lib/stores/settings.svelte';

	const SAMPLE_CODE = `function greet(name) {
  const msg = \`Hello, \${name}!\`;
  return msg;
}

greet('world');`;

	const LAYOUT_KEY = 'pageview-layout-mode';
	type LayoutMode = 'single' | 'two-centered' | 'two-full';

	const stored = localStorage.getItem(LAYOUT_KEY);
	let layout = $state<LayoutMode>(
		stored === 'single' || stored === 'two-centered' || stored === 'two-full'
			? stored
			: 'two-centered'
	);

	function setLayout(mode: LayoutMode) {
		layout = mode;
		localStorage.setItem(LAYOUT_KEY, mode);
	}

	let buildInfo = $state<BuildInfo | null>(null);

	onMount(async () => {
		try {
			buildInfo = await getBuildInfo();
		} catch {
			// non-essential
		}
	});

	function formatDate(iso: string | null): string {
		if (!iso) return '—';
		const d = new Date(iso);
		return isNaN(d.getTime()) ? iso : d.toLocaleString();
	}
</script>

<div class="settings">
	<h2 class="page-title">Settings</h2>

	<div class="sections">
		<section class="section">
			<h3 class="section-title">Appearance</h3>

			<div class="field">
				<div class="field-label">Default page layout</div>
				<div class="field-hint">
					Applied when opening a record. Existing open pages keep their current layout until
					reopened.
				</div>
				<div class="options" role="radiogroup" aria-label="Default page layout">
					{#each [
						{ value: 'single', label: 'Single column' },
						{ value: 'two-centered', label: 'Two columns (centered)' },
						{ value: 'two-full', label: 'Two columns (full width)' }
					] as opt (opt.value)}
						<label class="option" class:active={layout === opt.value}>
							<input
								type="radio"
								name="layout"
								value={opt.value}
								checked={layout === opt.value}
								onchange={() => setLayout(opt.value as LayoutMode)}
							/>
							{opt.label}
						</label>
					{/each}
				</div>
			</div>
		</section>

		<section class="section">
			<h3 class="section-title">Code Highlighting</h3>
			<div class="field">
				<div class="field-label">Code block theme</div>
				<div class="field-hint">Applied to syntax-highlighted code blocks in all markdown views.</div>
				<div class="theme-picker">
					<select
						class="theme-select"
						value={settingsStore.hljsTheme}
						onchange={(e) => settingsStore.setHljsTheme((e.target as HTMLSelectElement).value)}
					>
						<optgroup label="Light">
							{#each HLJS_THEMES.filter(t => !t.dark) as t (t.value)}
								<option value={t.value}>{t.label}</option>
							{/each}
						</optgroup>
						<optgroup label="Dark">
							{#each HLJS_THEMES.filter(t => t.dark) as t (t.value)}
								<option value={t.value}>{t.label}</option>
							{/each}
						</optgroup>
					</select>
					<pre class="code-preview"><code class="hljs">{@html hljs.highlight(SAMPLE_CODE, { language: 'javascript' }).value}</code></pre>
				</div>
			</div>
		</section>

		{#if buildInfo}
			<section class="section">
				<h3 class="section-title">About</h3>
				<dl class="about-dl">
					<dt>Version</dt>
					<dd>{buildInfo.version}</dd>
					<dt>Commit</dt>
					<dd><code>{buildInfo.commit}</code></dd>
					<dt>Build date</dt>
					<dd>{formatDate(buildInfo.build_date)}</dd>
				</dl>
			</section>
		{/if}
	</div>
</div>

<style>
	.settings {
		max-width: 640px;
	}
	.page-title {
		margin: 0 0 24px;
		font-size: 1.4rem;
		font-weight: 700;
		color: #111;
	}
	.sections {
		display: flex;
		flex-direction: column;
		gap: 32px;
	}
	.section {
		border: 1px solid #e5e7eb;
		border-radius: 10px;
		padding: 20px 24px;
		background: #fff;
	}
	.section-title {
		margin: 0 0 20px;
		font-size: 0.95rem;
		font-weight: 600;
		color: #374151;
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}
	.field {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}
	.field-label {
		font-size: 0.9rem;
		font-weight: 500;
		color: #111;
	}
	.field-hint {
		font-size: 0.8rem;
		color: #9ca3af;
		margin-bottom: 4px;
	}
	.options {
		display: flex;
		flex-direction: column;
		gap: 4px;
		margin-top: 4px;
	}
	.option {
		display: flex;
		align-items: center;
		gap: 10px;
		padding: 9px 12px;
		border: 1px solid #e5e7eb;
		border-radius: 6px;
		font-size: 0.875rem;
		color: #374151;
		cursor: pointer;
		transition: border-color 0.12s, background 0.12s;
	}
	.option:hover {
		border-color: #a5b4fc;
		background: #f5f3ff;
	}
	.option.active {
		border-color: #6366f1;
		background: #eef2ff;
		color: #4338ca;
		font-weight: 500;
	}
	.option input[type='radio'] {
		accent-color: #6366f1;
	}
	.about-dl {
		display: grid;
		grid-template-columns: auto 1fr;
		gap: 8px 20px;
		margin: 0;
		font-size: 0.875rem;
	}
	.about-dl dt {
		color: #6b7280;
	}
	.about-dl dd {
		margin: 0;
		color: #111;
		word-break: break-all;
	}
	.about-dl code {
		font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
		font-size: 0.8rem;
	}
	.theme-picker {
		display: flex;
		flex-direction: column;
		gap: 10px;
		margin-top: 4px;
	}
	.theme-select {
		width: 100%;
		padding: 8px 10px;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		font-size: 0.875rem;
		font-family: inherit;
		color: #374151;
		background: #fff;
		outline: none;
		cursor: pointer;
		transition: border-color 0.12s;
	}
	.theme-select:focus {
		border-color: #6366f1;
		box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
	}
	.code-preview {
		margin: 0;
		border-radius: 6px;
		overflow: hidden;
		font-size: 0.8rem;
		line-height: 1.5;
	}
	.code-preview .hljs {
		display: block;
		padding: 12px 14px;
		border-radius: 6px;
	}
</style>
