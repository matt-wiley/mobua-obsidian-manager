import type { VaultRecord, RecordUpdate } from '$lib/api/records';
import * as api from '$lib/api/records';

let _records = $state<VaultRecord[]>([]);
let _loading = $state(false);
let _currentFolder = $state<string | null>(null);
let _currentVaultId = $state<string | null>(null);

export const recordsStore = {
	get records() { return _records; },
	get loading() { return _loading; },
	get currentFolder() { return _currentFolder; },
	get currentVaultId() { return _currentVaultId; },

	async load(vaultId: string, folder: string) {
		_currentVaultId = vaultId;
		_currentFolder = folder;
		_loading = true;
		try {
			_records = await api.getRecords(vaultId, folder);
		} finally {
			_loading = false;
		}
	},

	async refresh() {
		if (!_currentVaultId || !_currentFolder) return;
		const records = await api.getRecords(_currentVaultId, _currentFolder);
		_records = records;
	},

	async update(id: string, patch: RecordUpdate): Promise<VaultRecord> {
		const updated = await api.updateRecord(_currentVaultId!, id, patch);
		_records = _records.map((r) => (r.id === id ? updated : r));
		return updated;
	},

	invalidate() {
		this.refresh();
	}
};
