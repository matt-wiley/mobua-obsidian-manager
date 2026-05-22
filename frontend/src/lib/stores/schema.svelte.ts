import type { SchemaField } from '$lib/api/folders';
import { getFolderSchema } from '$lib/api/folders';

let _schema = $state<SchemaField[]>([]);
let _currentFolder = $state<string | null>(null);

export const schemaStore = {
	get schema() { return _schema; },
	get currentFolder() { return _currentFolder; },

	async load(folder: string) {
		_currentFolder = folder;
		_schema = await getFolderSchema(folder);
	}
};
