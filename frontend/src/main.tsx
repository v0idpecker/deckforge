import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { CssBaseline, ThemeProvider } from "@mui/material";

import App from "./App";
import Landing from "./Landing";
import { theme } from "./app/theme";
import "./index.css";

const pathname = window.location.pathname;
const RootView = pathname.startsWith("/app") ? App : Landing;

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <RootView />
    </ThemeProvider>
  </StrictMode>,
);
