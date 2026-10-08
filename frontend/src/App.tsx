import React from 'react';
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
