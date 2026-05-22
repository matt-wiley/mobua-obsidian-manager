import { render, screen, fireEvent, act } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import RelationField from '$lib/components/fields/RelationField.svelte';
import * as recordsApi from '$lib/api/records';

vi.mock('$lib/api/records', () => ({
	getRelations: vi.fn()
}));

vi.mock('$app/navigation', () => ({ goto: vi.fn() }));
vi.mock('$lib/stores/drawer.svelte', () => ({
	drawerStore: { open: false, push: vi.fn(), replace: vi.fn() }
}));
vi.mock('$lib/stores/records.svelte', () => ({
	recordsStore: { currentVaultId: 'test-vault', records: [] }
}));

const RELATIONS = [
	{ id: 'a', filename: 'Q3 Rebrand', folder_path: 'Projects/' },
	{ id: 'b', filename: 'Platform Migration', folder_path: 'Projects/' }
];

beforeEach(() => {
	vi.mocked(recordsApi.getRelations).mockResolvedValue(RELATIONS);
});

describe('RelationField', () => {
	it('renders the display label stripped of [[ ]]', () => {
		render(RelationField, {
			value: '[[Q3 Rebrand]]',
			recordId: 'rec1',
			fieldName: 'project',
			onSave: vi.fn()
		});
		expect(screen.getByText('Q3 Rebrand')).toBeInTheDocument();
	});

	it('fetches relations and shows select on click', async () => {
		render(RelationField, {
			value: '[[Q3 Rebrand]]',
			recordId: 'rec1',
			fieldName: 'project',
			onSave: vi.fn()
		});
		await userEvent.click(document.querySelector('.field-view') as HTMLElement);
		await screen.findByRole('combobox');
		expect(recordsApi.getRelations).toHaveBeenCalledWith('test-vault', 'rec1', 'project');
		expect(screen.getByRole('option', { name: 'Q3 Rebrand' })).toBeInTheDocument();
		expect(screen.getByRole('option', { name: 'Platform Migration' })).toBeInTheDocument();
	});

	it('calls onSave with [[ ]] wrapped value on selection', async () => {
		const onSave = vi.fn();
		render(RelationField, {
			value: '[[Q3 Rebrand]]',
			recordId: 'rec1',
			fieldName: 'project',
			onSave
		});
		await userEvent.click(document.querySelector('.field-view') as HTMLElement);
		await screen.findByRole('combobox');
		await userEvent.selectOptions(screen.getByRole('combobox'), 'Platform Migration');
		expect(onSave).toHaveBeenCalledWith('[[Platform Migration]]');
	});

	it('cancels on Escape', async () => {
		const onSave = vi.fn();
		render(RelationField, {
			value: '[[Q3 Rebrand]]',
			recordId: 'rec1',
			fieldName: 'project',
			onSave
		});
		await userEvent.click(document.querySelector('.field-view') as HTMLElement);
		const select = await screen.findByRole('combobox');
		await act(() => { fireEvent.keyDown(select, { key: 'Escape' }); });
		expect(onSave).not.toHaveBeenCalled();
		expect(screen.queryByRole('combobox')).not.toBeInTheDocument();
	});

	it('does not enter edit mode when readonly', async () => {
		render(RelationField, {
			value: '[[Q3 Rebrand]]',
			recordId: 'rec1',
			fieldName: 'project',
			readonly: true,
			onSave: vi.fn()
		});
		await userEvent.click(document.querySelector('.field-view') as HTMLElement);
		expect(screen.queryByRole('combobox')).not.toBeInTheDocument();
	});
});
