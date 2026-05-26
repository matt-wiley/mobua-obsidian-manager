<script lang="ts">
	import type { VaultRecord } from '$lib/api/records';
	import TextField from '$lib/components/fields/TextField.svelte';
	import DateField from '$lib/components/fields/DateField.svelte';
	import UrlField from '$lib/components/fields/UrlField.svelte';
	import RelationField from '$lib/components/fields/RelationField.svelte';
	import EnumField from '$lib/components/fields/EnumField.svelte';

	let {
		record,
		label,
		fieldType,
		options = [],
		value,
		onSave
	}: {
		record: VaultRecord;
		label: string;
		fieldType: string;
		options?: string[];
		value: string;
		onSave: (v: string) => void;
	} = $props();
</script>

<div class="field-block">
	<div class="field-label">{label}</div>
	<div class="field-value">
		{#if fieldType === 'date'}
			<DateField {value} {onSave} />
		{:else if fieldType === 'url'}
			<UrlField {value} {onSave} />
		{:else if fieldType === 'relation'}
			<RelationField {value} recordId={record.id} fieldName={label} {onSave} />
		{:else if fieldType === 'enum'}
			<EnumField {value} {options} {onSave} />
		{:else}
			<TextField {value} {onSave} />
		{/if}
	</div>
</div>

<style>
	.field-block {
		display: contents;
	}
	.field-label {
		padding: 6px 12px 6px 0;
		color: #6b7280;
		font-size: 0.85rem;
		font-weight: 500;
		white-space: nowrap;
		align-self: start;
		padding-top: 8px;
	}
	.field-value {
		padding: 2px 0;
		min-width: 0;
	}
</style>
