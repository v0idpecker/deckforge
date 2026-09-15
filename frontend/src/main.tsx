import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import AppPage from "./pages/AppPage";
import LandingPage from "./pages/LandingPage";
import { ThemeModeProvider } from "./app/ThemeModeProvider";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeModeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/app" element={<AppPage />} />
        </Routes>
      </BrowserRouter>
    </ThemeModeProvider>
  </StrictMode>,
);
