import { apiFetch } from './client';

export interface VaultRecord {
	id: string;
	folder_path: string;
	file_path: string;
	filename: string;
	frontmatter: Record<string, unknown>;
	sections: Record<string, string>;
	content_hash: string;
	updated_at: string;
}

export interface RecordCreate {
	filename: string;
	frontmatter?: Record<string, unknown>;
	sections?: Record<string, string>;
}

export interface RecordUpdate {
	filename?: string;
	frontmatter?: Record<string, unknown>;
	sections?: Record<string, string>;
}

export interface RelationOption {
	id: string | null;
	filename: string;
	folder_path: string | null;
}

export function getRecords(folder: string): Promise<VaultRecord[]> {
	return apiFetch(`/folders/${encodeURIComponent(folder)}/records`);
}

export function getRecord(id: string): Promise<VaultRecord> {
	return apiFetch(`/records/${id}`);
}

export function createRecord(folder: string, data: RecordCreate): Promise<VaultRecord> {
	return apiFetch(`/folders/${encodeURIComponent(folder)}/records`, {
		method: 'POST',
		body: JSON.stringify(data)
	});
}

export function updateRecord(id: string, data: RecordUpdate): Promise<VaultRecord> {
	return apiFetch(`/records/${id}`, {
		method: 'PUT',
		body: JSON.stringify(data)
	});
}

export function deleteRecord(id: string): Promise<void> {
	return apiFetch(`/records/${id}`, { method: 'DELETE' });
}

export function getRelations(id: string, field: string): Promise<RelationOption[]> {
	return apiFetch(`/records/${id}/relations/${encodeURIComponent(field)}`);
}
