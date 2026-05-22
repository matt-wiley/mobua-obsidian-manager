<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import favicon from '$lib/assets/favicon.svg';
	import SyncBadge from '$lib/components/shared/SyncBadge.svelte';
	import { syncStore } from '$lib/stores/sync.svelte';
	import { recordsStore } from '$lib/stores/records.svelte';

	let { children } = $props();

	onMount(() => {
		const es = new EventSource('/api/events');
		let errorTimer: ReturnType<typeof setTimeout> | null = null;

		es.onopen = () => {
			if (errorTimer) { clearTimeout(errorTimer); errorTimer = null; }
			syncStore.setConnected();
		};

		// Debounce: only go amber if the connection is lost for >3s.
		// The EventSource fires onerror on every reconnection attempt, so without
		// this the badge flickers amber on any brief hiccup.
		es.onerror = () => {
			if (!errorTimer) {
				errorTimer = setTimeout(() => syncStore.setReconnecting(), 3000);
			}
		};

		// Any received event proves the connection is alive — clear reconnecting status.
		es.addEventListener('ping', () => syncStore.setConnected());

		es.onmessage = (e) => {
			syncStore.setConnected();
			const event = JSON.parse(e.data) as { type: string; folder_path: string };
			if (event.type === 'record_changed' || event.type === 'record_deleted') {
				const currentFolder = recordsStore.currentFolder;
				if (currentFolder && event.folder_path === currentFolder + '/') {
					recordsStore.invalidate();
				}
			}
		};

		return () => {
			if (errorTimer) clearTimeout(errorTimer);
			es.close();
		};
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="app-shell">
	<header>
		<a href="/" class="home-link">Obsidian Manager</a>
		<SyncBadge />
	</header>

	<main>
		{@render children()}
	</main>
</div>

<style>
	.app-shell {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
		font-family: system-ui, sans-serif;
	}
	header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 10px 20px;
		border-bottom: 1px solid #e5e7eb;
		background: #fff;
	}
	.home-link {
		font-weight: 600;
		text-decoration: none;
		color: #111;
	}
	main {
		flex: 1;
		padding: 20px;
	}
</style>
