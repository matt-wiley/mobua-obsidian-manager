<script lang="ts">
	import { onDestroy } from 'svelte';
	import { syncStore } from '$lib/stores/sync.svelte';

	let now = $state(Date.now());
	const ticker = setInterval(() => { now = Date.now(); }, 1000);
	onDestroy(() => clearInterval(ticker));

	// Amber if connected but no ping in 20s (two missed server pings)
	const STALE_MS = 20_000;

	let color = $derived(
		syncStore.status === 'error'
			? 'red'
			: syncStore.status === 'reconnecting' || (syncStore.lastPing > 0 && now - syncStore.lastPing > STALE_MS)
				? 'amber'
				: 'green'
	);

	let label = $derived(
		color === 'green' ? 'Live' : color === 'amber' ? 'Reconnecting…' : 'Sync error'
	);
</script>

<div class="sync-badge {color}" title={label}>
	<span class="dot"></span>
	<span class="label">{label}</span>
</div>

<style>
	.sync-badge {
		display: inline-flex;
		align-items: center;
		gap: 5px;
		font-size: 12px;
		font-weight: 500;
		padding: 3px 8px;
		border-radius: 99px;
	}
	.dot {
		width: 7px;
		height: 7px;
		border-radius: 50%;
	}
	.green { color: #166534; background: #dcfce7; }
	.green .dot { background: #16a34a; }
	.amber { color: #92400e; background: #fef3c7; }
	.amber .dot { background: #d97706; }
	.red   { color: #991b1b; background: #fee2e2; }
	.red   .dot { background: #dc2626; }
</style>
