import { apiFetch } from './client';

export interface Folder {
	name: string;
	path: string;
	record_count: number;
}

export interface SchemaField {
	field_name: string;
	field_type: 'text' | 'date' | 'url' | 'number' | 'relation' | 'markdown' | 'enum';
	source: 'frontmatter' | 'section';
	options?: string[];
}

export interface View {
	id: string;
	name: string;
	filters: { field: string; op: string; value: string }[];
	sort: { id: string; dir: 'asc' | 'desc' }[];
	col_order: string[];
	hidden_cols: string[];
}

export function getFolders(vaultId: string): Promise<Folder[]> {
	return apiFetch(`/vaults/${encodeURIComponent(vaultId)}/folders`);
}

export function getFolderSchema(vaultId: string, folder: string): Promise<SchemaField[]> {
	return apiFetch(`/vaults/${encodeURIComponent(vaultId)}/folders/${encodeURIComponent(folder)}/schema`);
}

export function getFieldOptions(vaultId: string, folder: string): Promise<Record<string, string[]>> {
	return apiFetch(
		`/vaults/${encodeURIComponent(vaultId)}/folders/${encodeURIComponent(folder)}/field-options`
	);
}

export function setFieldOptions(
	vaultId: string,
	folder: string,
	field: string,
	options: string[]
): Promise<void> {
	return apiFetch(
		`/vaults/${encodeURIComponent(vaultId)}/folders/${encodeURIComponent(folder)}/field-options/${encodeURIComponent(field)}`,
		{ method: 'PUT', body: JSON.stringify({ options }) }
	);
}

export function deleteFieldOptions(vaultId: string, folder: string, field: string): Promise<void> {
	return apiFetch(
		`/vaults/${encodeURIComponent(vaultId)}/folders/${encodeURIComponent(folder)}/field-options/${encodeURIComponent(field)}`,
		{ method: 'DELETE' }
	);
}

export function getColWidths(vaultId: string, folder: string): Promise<Record<string, number>> {
	return apiFetch(`/vaults/${encodeURIComponent(vaultId)}/folders/${encodeURIComponent(folder)}/col_widths`);
}

export function setColWidth(vaultId: string, folder: string, field: string, width: number): Promise<void> {
	return apiFetch(
		`/vaults/${encodeURIComponent(vaultId)}/folders/${encodeURIComponent(folder)}/col_widths/${encodeURIComponent(field)}`,
		{ method: 'PUT', body: JSON.stringify({ width }) }
	);
}

export function getViews(vaultId: string, folder: string): Promise<View[]> {
	return apiFetch(`/vaults/${encodeURIComponent(vaultId)}/folders/${encodeURIComponent(folder)}/views`);
}

export function createView(vaultId: string, folder: string, view: Omit<View, 'id'>): Promise<View> {
	return apiFetch(
		`/vaults/${encodeURIComponent(vaultId)}/folders/${encodeURIComponent(folder)}/views`,
		{ method: 'POST', body: JSON.stringify(view) }
	);
}

export function deleteView(vaultId: string, folder: string, viewId: string): Promise<void> {
	return apiFetch(
		`/vaults/${encodeURIComponent(vaultId)}/folders/${encodeURIComponent(folder)}/views/${encodeURIComponent(viewId)}`,
		{ method: 'DELETE' }
	);
}
