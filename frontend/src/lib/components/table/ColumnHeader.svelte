<script lang="ts">
	let {
		label,
		canResize = false,
		isResizing = false,
		onResizeStart
	}: {
		label: string;
		canResize?: boolean;
		isResizing?: boolean;
		onResizeStart?: (e: MouseEvent | TouchEvent) => void;
	} = $props();
</script>

<span class="label">{label}</span>
{#if canResize}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="resizer"
		class:isResizing
		onmousedown={onResizeStart}
		ontouchstart={onResizeStart}
	></div>
{/if}

<style>
	.label {
		flex: 1;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
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
