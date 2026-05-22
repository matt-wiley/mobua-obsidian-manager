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

export function getRecords(vaultId: string, folder: string): Promise<VaultRecord[]> {
	return apiFetch(`/vaults/${encodeURIComponent(vaultId)}/folders/${encodeURIComponent(folder)}/records`);
}

export function getRecord(vaultId: string, id: string): Promise<VaultRecord> {
	return apiFetch(`/vaults/${encodeURIComponent(vaultId)}/records/${id}`);
}

export function createRecord(vaultId: string, folder: string, data: RecordCreate): Promise<VaultRecord> {
	return apiFetch(`/vaults/${encodeURIComponent(vaultId)}/folders/${encodeURIComponent(folder)}/records`, {
		method: 'POST',
		body: JSON.stringify(data)
	});
}

export function updateRecord(vaultId: string, id: string, data: RecordUpdate): Promise<VaultRecord> {
	return apiFetch(`/vaults/${encodeURIComponent(vaultId)}/records/${id}`, {
		method: 'PUT',
		body: JSON.stringify(data)
	});
}

export function deleteRecord(vaultId: string, id: string): Promise<void> {
	return apiFetch(`/vaults/${encodeURIComponent(vaultId)}/records/${id}`, { method: 'DELETE' });
}

export function getRelations(vaultId: string, id: string, field: string): Promise<RelationOption[]> {
	return apiFetch(`/vaults/${encodeURIComponent(vaultId)}/records/${id}/relations/${encodeURIComponent(field)}`);
}
