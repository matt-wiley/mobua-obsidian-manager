<script lang="ts">
	let {
		label,
		canResize = false,
		isResizing = false,
		onResizeStart,
		sortDir = null,
		sortPriority = null
	}: {
		label: string;
		canResize?: boolean;
		isResizing?: boolean;
		onResizeStart?: (e: MouseEvent | TouchEvent) => void;
		sortDir?: 'asc' | 'desc' | null;
		sortPriority?: number | null;
	} = $props();
</script>

<span class="label">{label}</span>
{#if sortDir}
	<span class="sort-indicator">
		{sortDir === 'asc' ? '▲' : '▼'}{#if sortPriority !== null && sortPriority > 1}<sup>{sortPriority}</sup>{/if}
	</span>
{/if}
{#if canResize}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="resizer"
		class:isResizing
		draggable="false"
		onmousedown={onResizeStart}
		ontouchstart={onResizeStart}
		ondragstart={(e) => e.stopPropagation()}
	></div>
{/if}

<style>
	.label {
		flex: 1;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.sort-indicator {
		font-size: 10px;
		color: #6366f1;
		margin-left: 4px;
		flex-shrink: 0;
	}
	.resizer {
		position: absolute;
		right: 0;
		top: 0;
		height: 100%;
		width: 4px;
		cursor: col-resize;
		user-select: none;
		touch-action: none;
	}
	.resizer:hover,
	.resizer.isResizing {
		background: #6366f1;
	}
</style>
