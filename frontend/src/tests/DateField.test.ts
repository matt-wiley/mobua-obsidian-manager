import { render, screen, fireEvent, act } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import DateField from '$lib/components/fields/DateField.svelte';

describe('DateField', () => {
	it('renders a formatted date in view mode', () => {
		render(DateField, { value: '2026-06-10', onSave: vi.fn() });
		// Should show a human-readable date, not the raw ISO string
		expect(screen.queryByText('2026-06-10')).not.toBeInTheDocument();
		// The container should have some text
		expect(document.body.textContent?.trim()).not.toBe('');
	});

	it('switches to a date input on click', async () => {
		render(DateField, { value: '2026-06-10', onSave: vi.fn() });
		const view = document.querySelector('.field-view') as HTMLElement;
		await userEvent.click(view);
		const input = screen.getByDisplayValue('2026-06-10');
		expect(input).toBeInTheDocument();
		expect((input as HTMLInputElement).type).toBe('date');
	});

	it('calls onSave on Enter after changing value', async () => {
		const onSave = vi.fn();
		render(DateField, { value: '2026-06-10', onSave });
		await userEvent.click(document.querySelector('.field-view') as HTMLElement);
		const input = screen.getByDisplayValue('2026-06-10');
		await act(() => {
			fireEvent.input(input, { target: { value: '2026-07-15' } });
			fireEvent.keyDown(input, { key: 'Enter' });
		});
		expect(onSave).toHaveBeenCalledWith('2026-07-15');
	});

	it('cancels on Escape', async () => {
		const onSave = vi.fn();
		render(DateField, { value: '2026-06-10', onSave });
		await userEvent.click(document.querySelector('.field-view') as HTMLElement);
		await userEvent.keyboard('{Escape}');
		expect(onSave).not.toHaveBeenCalled();
		expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
	});

	it('does not enter edit mode when readonly', async () => {
		render(DateField, { value: '2026-06-10', readonly: true, onSave: vi.fn() });
		await userEvent.click(document.querySelector('.field-view') as HTMLElement);
		expect(screen.queryByDisplayValue('2026-06-10')).not.toBeInTheDocument();
	});
});
