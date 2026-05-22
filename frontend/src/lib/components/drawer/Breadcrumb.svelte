<script lang="ts">
	import { drawerStore } from '$lib/stores/drawer.svelte';
</script>

{#if drawerStore.breadcrumbs.length > 0}
	<nav class="breadcrumb" aria-label="Drawer navigation">
		{#each drawerStore.breadcrumbs as crumb, i}
			<button class="crumb" onclick={() => drawerStore.goToBreadcrumb(i)}>
				{crumb.filename}
			</button>
			<span class="sep" aria-hidden="true">›</span>
		{/each}
		<span class="current">{drawerStore.record?.filename}</span>
	</nav>
{/if}

<style>
	.breadcrumb {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 2px;
		font-size: 0.8rem;
		min-width: 0;
	}
	.crumb {
		background: none;
		border: none;
		cursor: pointer;
		color: #6366f1;
		padding: 2px 4px;
		border-radius: 3px;
		font-size: 0.8rem;
		white-space: nowrap;
		max-width: 120px;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.crumb:hover {
		background: #eef2ff;
		text-decoration: underline;
	}
	.sep {
		color: #d1d5db;
		flex-shrink: 0;
	}
	.current {
		color: #374151;
		font-weight: 500;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		max-width: 160px;
	}
</style>
