/**
 * Tests for the ChatInput component.
 * Verifies accessibility attributes, keyboard handling, and input behavior.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ChatInput from '../components/fan/ChatInput';

describe('ChatInput', () => {
  it('renders the input field and send button', () => {
    render(<ChatInput onSend={vi.fn()} isLoading={false} disabled={false} />);

    expect(screen.getByLabelText('Type your message')).toBeInTheDocument();
    expect(screen.getByLabelText('Send message')).toBeInTheDocument();
  });

  it('has proper aria labels for accessibility', () => {
    render(<ChatInput onSend={vi.fn()} isLoading={false} disabled={false} />);

    const form = screen.getByRole('form');
    expect(form).toHaveAttribute('aria-label', 'Chat message input');

    const input = screen.getByLabelText('Type your message');
    expect(input).toHaveAttribute('id', 'chat-input');
    expect(input).toHaveAttribute('maxLength', '2000');
  });

  it('disables send button when input is empty', () => {
    render(<ChatInput onSend={vi.fn()} isLoading={false} disabled={false} />);

    const sendBtn = screen.getByLabelText('Send message');
    expect(sendBtn).toBeDisabled();
  });

  it('enables send button when input has text', () => {
    render(<ChatInput onSend={vi.fn()} isLoading={false} disabled={false} />);

    const input = screen.getByLabelText('Type your message');
    fireEvent.change(input, { target: { value: 'Hello' } });

    const sendBtn = screen.getByLabelText('Send message');
    expect(sendBtn).not.toBeDisabled();
  });

  it('calls onSend when send button is clicked', () => {
    const mockSend = vi.fn();
    render(<ChatInput onSend={mockSend} isLoading={false} disabled={false} />);

    const input = screen.getByLabelText('Type your message');
    fireEvent.change(input, { target: { value: 'Where is Gate A?' } });

    const sendBtn = screen.getByLabelText('Send message');
    fireEvent.click(sendBtn);

    expect(mockSend).toHaveBeenCalledWith('Where is Gate A?');
  });

  it('clears input after sending', () => {
    const mockSend = vi.fn();
    render(<ChatInput onSend={mockSend} isLoading={false} disabled={false} />);

    const input = screen.getByLabelText('Type your message');
    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(screen.getByLabelText('Send message'));

    expect(input.value).toBe('');
  });

  it('disables input when disabled prop is true', () => {
    render(<ChatInput onSend={vi.fn()} isLoading={false} disabled={true} />);

    const input = screen.getByLabelText('Type your message');
    expect(input).toBeDisabled();
  });

  it('shows keyboard shortcut hint', () => {
    render(<ChatInput onSend={vi.fn()} isLoading={false} disabled={false} />);

    expect(screen.getByText('Enter')).toBeInTheDocument();
    expect(screen.getByText('Shift + Enter')).toBeInTheDocument();
  });
});
