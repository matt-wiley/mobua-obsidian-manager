import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import EnumField from '$lib/components/fields/EnumField.svelte';

const OPTIONS = ['active', 'done', 'blocked'];

describe('EnumField', () => {
	it('renders the value as a pill in view mode', () => {
		render(EnumField, { value: 'active', options: OPTIONS, onSave: vi.fn() });
		expect(screen.getByText('active')).toBeInTheDocument();
		expect(screen.getByText('active').className).toContain('pill');
	});

	it('switches to a select on click', async () => {
		render(EnumField, { value: 'active', options: OPTIONS, onSave: vi.fn() });
		await userEvent.click(document.querySelector('.field-view') as HTMLElement);
		expect(screen.getByRole('combobox')).toBeInTheDocument();
	});

	it('lists all options in the select', async () => {
		render(EnumField, { value: 'active', options: OPTIONS, onSave: vi.fn() });
		await userEvent.click(document.querySelector('.field-view') as HTMLElement);
		for (const opt of OPTIONS) {
			expect(screen.getByRole('option', { name: opt })).toBeInTheDocument();
		}
	});

	it('calls onSave when selection changes', async () => {
		const onSave = vi.fn();
		render(EnumField, { value: 'active', options: OPTIONS, onSave });
		await userEvent.click(document.querySelector('.field-view') as HTMLElement);
		await userEvent.selectOptions(screen.getByRole('combobox'), 'done');
		expect(onSave).toHaveBeenCalledWith('done');
	});

	it('cancels on Escape', async () => {
		const onSave = vi.fn();
		render(EnumField, { value: 'active', options: OPTIONS, onSave });
		await userEvent.click(document.querySelector('.field-view') as HTMLElement);
		await userEvent.keyboard('{Escape}');
		expect(onSave).not.toHaveBeenCalled();
		expect(screen.queryByRole('combobox')).not.toBeInTheDocument();
	});

	it('includes the current value in options even if not in list', async () => {
		render(EnumField, { value: 'custom', options: OPTIONS, onSave: vi.fn() });
		await userEvent.click(document.querySelector('.field-view') as HTMLElement);
		expect(screen.getByRole('option', { name: 'custom' })).toBeInTheDocument();
	});

	it('does not enter edit mode when readonly', async () => {
		render(EnumField, { value: 'active', options: OPTIONS, readonly: true, onSave: vi.fn() });
		await userEvent.click(document.querySelector('.field-view') as HTMLElement);
		expect(screen.queryByRole('combobox')).not.toBeInTheDocument();
	});
});
