import type { SchemaField } from '$lib/api/folders';
import { getFolderSchema } from '$lib/api/folders';

let _schema = $state<SchemaField[]>([]);
let _currentFolder = $state<string | null>(null);
let _currentVaultId = $state<string | null>(null);

export const schemaStore = {
	get schema() { return _schema; },
	get currentFolder() { return _currentFolder; },
	get currentVaultId() { return _currentVaultId; },

	async load(vaultId: string, folder: string) {
		_currentVaultId = vaultId;
		_currentFolder = folder;
		_schema = await getFolderSchema(vaultId, folder);
	},

	async reload() {
		if (_currentVaultId && _currentFolder) {
			_schema = await getFolderSchema(_currentVaultId, _currentFolder);
		}
	}
};
