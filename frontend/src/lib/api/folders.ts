import { apiFetch } from './client';

export interface Folder {
	name: string;
	path: string;
	record_count: number;
}

export interface SchemaField {
	field_name: string;
	field_type: 'text' | 'date' | 'url' | 'number' | 'relation' | 'markdown';
	source: 'frontmatter' | 'section';
}

export function getFolders(): Promise<Folder[]> {
	return apiFetch('/folders');
}

export function getFolderSchema(folder: string): Promise<SchemaField[]> {
	return apiFetch(`/folders/${encodeURIComponent(folder)}/schema`);
}
