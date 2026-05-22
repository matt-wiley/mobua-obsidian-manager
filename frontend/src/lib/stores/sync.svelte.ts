export type SyncStatus = 'connected' | 'reconnecting' | 'error';

let _status = $state<SyncStatus>('reconnecting');
let _lastPing = $state<number>(0);

export const syncStore = {
	get status() { return _status; },
	get lastPing() { return _lastPing; },

	setConnected() {
		_status = 'connected';
		_lastPing = Date.now();
	},
	setReconnecting() {
		_status = 'reconnecting';
	},
	setError() {
		_status = 'error';
	},
	ping() {
		_lastPing = Date.now();
	}
};
