import { describe, it, expect } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Playground } from '../pages/Playground';

describe('Playground Page Component', () => {
  it('renders Playground header and prompt textareas', () => {
    render(
      <BrowserRouter>
        <Playground />
      </BrowserRouter>
    );

    expect(screen.getByText(/Prompt Playground/i)).toBeDefined();
    expect(screen.getByText(/User Prompt Template/i)).toBeDefined();
    expect(screen.getByText(/Run Prompt/i)).toBeDefined();
  });
});
