import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import App             from "./App.jsx";
import AuthPage        from "./pages/AuthPage.jsx";
import MyReviewsPage   from "./pages/MyReviewsPage.jsx";
import AdminReportsPage from "./pages/AdminReportsPage.jsx"; 
import StatisticsPage  from "./pages/StatisticsPage.jsx"; 

ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <Routes>
      <Route path="/"            element={<App />} />
      <Route path="/auth"        element={<AuthPage />} />
      <Route path="/statistics"  element={<StatisticsPage />} />
      <Route path="/my-reviews"  element={<MyReviewsPage />} />
      <Route path="/moderate"    element={<AdminReportsPage />} />
    </Routes>
  </BrowserRouter>
);
