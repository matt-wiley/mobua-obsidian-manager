<script lang="ts">
	let {
		label,
		canResize = false,
		isResizing = false,
		onResizeStart,
		sortDir = null,
		sortPriority = null,
		onSortClick,
		onEditOptions
	}: {
		label: string;
		canResize?: boolean;
		isResizing?: boolean;
		onResizeStart?: (e: MouseEvent | TouchEvent) => void;
		sortDir?: 'asc' | 'desc' | null;
		sortPriority?: number | null;
		onSortClick?: () => void;
		onEditOptions?: () => void;
	} = $props();
</script>

<span class="label">{label}</span>
{#if onEditOptions}
	<button
		class="opts-btn"
		onclick={(e) => { e.stopPropagation(); onEditOptions!(); }}
		title="Edit options"
		aria-label="Edit options"
	>⋯</button>
{/if}
{#if onSortClick}
	<button
		class="sort-btn"
		class:active={sortDir !== null}
		onclick={(e) => { e.stopPropagation(); onSortClick!(); }}
		title={sortDir === null ? 'Sort ascending' : sortDir === 'asc' ? 'Sort descending' : 'Clear sort'}
	>
		{#if sortDir === 'asc'}▲{:else if sortDir === 'desc'}▼{:else}⇅{/if}{#if sortPriority !== null && sortPriority > 1}<sup>{sortPriority}</sup>{/if}
	</button>
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
	.sort-btn {
		flex-shrink: 0;
		background: none;
		border: 1px solid transparent;
		border-radius: 3px;
		cursor: pointer;
		font-size: 10px;
		color: #9ca3af;
		padding: 1px 3px;
		margin-left: 2px;
		line-height: 1;
		opacity: 0;
	}
	.opts-btn {
		flex-shrink: 0;
		background: none;
		border: 1px solid transparent;
		border-radius: 3px;
		cursor: pointer;
		font-size: 12px;
		color: #9ca3af;
		padding: 0 4px;
		margin-left: 2px;
		line-height: 1;
		opacity: 0;
	}
	:global(th:hover) .opts-btn {
		opacity: 1;
	}
	.opts-btn:hover {
		border-color: #d1d5db;
		background: #f3f4f6;
		color: #374151;
	}
	:global(th:hover) .sort-btn,
	.sort-btn.active {
		opacity: 1;
	}
	.sort-btn.active {
		color: #6366f1;
		border-color: #c7d2fe;
		background: #eef2ff;
	}
	.sort-btn:hover {
		border-color: #d1d5db;
		background: #f3f4f6;
		color: #374151;
	}
	.sort-btn.active:hover {
		border-color: #a5b4fc;
		background: #e0e7ff;
		color: #4f46e5;
	}
	.resizer {
		position: absolute;
		right: 0;
		top: 0;
		height: 100%;
		width: 5px;
		cursor: col-resize;
		user-select: none;
		touch-action: none;
		background: linear-gradient(to right, transparent 2px, #d1d5db 2px, #d1d5db 3px, transparent 3px);
	}
	.resizer:hover,
	.resizer.isResizing {
		background: linear-gradient(to right, transparent 1px, #6366f1 1px, #6366f1 4px, transparent 4px);
	}
</style>
