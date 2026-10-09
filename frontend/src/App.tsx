/// <reference types="vite/client" />
import React, { useState } from 'react';
import { api } from './services/api';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Playground } from './pages/Playground';
import { Optimizer } from './pages/Optimizer';
import { Comparison } from './pages/Comparison';
import { Evaluations } from './pages/Evaluations';
import { Library } from './pages/Library';
import { Analytics } from './pages/Analytics';

export const App: React.FC = () => {
  const [authenticated, setAuthenticated] = useState(!import.meta.env.PROD);
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  if (!authenticated) {
    return <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-6">
      <form className="bg-slate-900 p-8 rounded-xl max-w-sm w-full space-y-4" onSubmit={async e => {
        e.preventDefault();
        try { await api.login(password); setAuthenticated(true); setPassword(''); }
        catch (err) { setError(err instanceof Error ? err.message : 'Authentication failed'); }
      }}>
        <h1 className="text-xl font-semibold">PromptLab AI — Private Workspace</h1>
        <label htmlFor="workspace-password" className="block text-sm">Access passphrase</label>
        <input id="workspace-password" type="password" autoComplete="current-password" required
          value={password} onChange={e => setPassword(e.target.value)}
          className="w-full p-3 bg-slate-800 rounded-lg" />
        {error && <p role="alert" className="text-red-400">{error}</p>}
        <button type="submit" className="w-full bg-blue-600 p-3 rounded-lg">Sign in</button>
      </form>
    </main>;
  }
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/playground" replace />} />
            <Route path="/playground" element={<Playground />} />
            <Route path="/optimizer" element={<Optimizer />} />
            <Route path="/comparison" element={<Comparison />} />
            <Route path="/evaluations" element={<Evaluations />} />
            <Route path="/library" element={<Library />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="*" element={<Navigate to="/playground" replace />} />
          </Routes>
        </Layout>
      </ErrorBoundary>
    </BrowserRouter>
  );
};
export default App;
