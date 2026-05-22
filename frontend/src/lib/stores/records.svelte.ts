import type { VaultRecord, RecordUpdate } from '$lib/api/records';
import * as api from '$lib/api/records';

let _records = $state<VaultRecord[]>([]);
let _loading = $state(false);
let _currentFolder = $state<string | null>(null);

export const recordsStore = {
	get records() { return _records; },
	get loading() { return _loading; },
	get currentFolder() { return _currentFolder; },

	async load(folder: string) {
		_currentFolder = folder;
		_loading = true;
		try {
			_records = await api.getRecords(folder);
		} finally {
			_loading = false;
		}
	},

	async update(id: string, patch: RecordUpdate): Promise<VaultRecord> {
		const updated = await api.updateRecord(id, patch);
		_records = _records.map((r) => (r.id === id ? updated : r));
		return updated;
	},

	invalidate() {
		if (_currentFolder) this.load(_currentFolder);
	}
};
