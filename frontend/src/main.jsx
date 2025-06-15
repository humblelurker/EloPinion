import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import App from './App.jsx';
import AuthPage from './pages/AuthPage.jsx';
import MyReviewsPage from './pages/MyReviewsPage.jsx';
ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <Routes>
      <Route path="/"           element={<App />} />
      <Route path="/auth"       element={<AuthPage />} />
      <Route path="/my-reviews" element={<MyReviewsPage />} />
    </Routes>
  </BrowserRouter>
);
