<script lang="ts">
	import { onMount } from 'svelte';

	let status = $state<string>('checking...');

	onMount(async () => {
		try {
			const res = await fetch('/api/health');
			if (res.ok) {
				const data = await res.json();
				status = `connected — vault: ${data.vault_path}, records: ${data.record_count}`;
			} else {
				status = `backend error: ${res.status}`;
			}
		} catch {
			status = 'backend unreachable';
		}
	});
</script>

<h1>It works.</h1>
<p>Backend: {status}</p>
