<script lang="ts">
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
</style>
