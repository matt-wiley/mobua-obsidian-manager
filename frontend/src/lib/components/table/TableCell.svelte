<script lang="ts">
	import type { VaultRecord } from '$lib/api/records';
	import type { SchemaField } from '$lib/api/folders';
	import TextField from '$lib/components/fields/TextField.svelte';
	import DateField from '$lib/components/fields/DateField.svelte';
	import UrlField from '$lib/components/fields/UrlField.svelte';
	import RelationField from '$lib/components/fields/RelationField.svelte';
	import MarkdownField from '$lib/components/fields/MarkdownField.svelte';
	import EnumField from '$lib/components/fields/EnumField.svelte';

	let {
		record,
		field,
		onSave
	}: {
		record: VaultRecord;
		field: SchemaField;
		onSave: (v: string) => void;
	} = $props();

	let value = $derived(
		field.source === 'frontmatter'
			? (record.frontmatter[field.field_name] != null
					? String(record.frontmatter[field.field_name])
					: '')
			: (record.sections[field.field_name] ?? '')
	);
</script>

{#if field.field_type === 'date'}
	<DateField {value} {onSave} />
{:else if field.field_type === 'url'}
	<UrlField {value} {onSave} />
{:else if field.field_type === 'relation'}
	<RelationField {value} recordId={record.id} fieldName={field.field_name} {onSave} />
{:else if field.field_type === 'markdown'}
	<MarkdownField {value} {onSave} />
{:else if field.field_type === 'enum'}
	<EnumField {value} options={field.options ?? []} {onSave} />
{:else}
	<TextField {value} {onSave} />
{/if}
