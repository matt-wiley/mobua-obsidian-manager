import type { VaultRecord } from '$lib/api/records';

let _open = $state(false);
let _record = $state<VaultRecord | null>(null);
let _breadcrumbs = $state<VaultRecord[]>([]);

export const drawerStore = {
	get open() { return _open; },
	get record() { return _record; },
	get breadcrumbs() { return _breadcrumbs; },

	push(record: VaultRecord) {
		if (_record) _breadcrumbs = [..._breadcrumbs, _record];
		_record = record;
		_open = true;
	},

	replace(record: VaultRecord) {
		_record = record;
		_open = true;
	},

	pop() {
		if (_breadcrumbs.length > 0) {
			_record = _breadcrumbs[_breadcrumbs.length - 1];
			_breadcrumbs = _breadcrumbs.slice(0, -1);
		} else {
			this.close();
		}
	},

	goToBreadcrumb(index: number) {
		if (index < 0 || index >= _breadcrumbs.length) return;
		_record = _breadcrumbs[index];
		_breadcrumbs = _breadcrumbs.slice(0, index);
	},

	close() {
		_open = false;
		_record = null;
		_breadcrumbs = [];
	}
};
