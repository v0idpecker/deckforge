import { alpha, createTheme } from "@mui/material/styles";

const ink = "#151a21";
const muted = "#5a6472";
const border = "#dde3ea";

const teal = "#0d9488";
const tealHover = "#0f766e";
const indigo = "#4f46e5";
const indigoDark = "#4338ca";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: teal,
      light: "#2dd4bf",
      dark: "#115e59",
      contrastText: "#ffffff",
    },
    secondary: {
      main: indigo,
      light: "#6366f1",
      dark: indigoDark,
      contrastText: "#ffffff",
    },
    background: {
      default: "#f3f5f7",
      paper: "#ffffff",
    },
    text: {
      primary: ink,
      secondary: muted,
    },
    divider: border,
    error: {
      main: "#e11d48",
      light: "#ffe4e6",
    },
    warning: {
      main: "#f59e0b",
      light: "#fef3c7",
    },
    success: {
      main: "#10b981",
      light: "#d1fae5",
    },
    info: {
      main: "#2563eb",
      light: "#dbeafe",
    },
  },
  shape: {
    borderRadius: 10,
  },
  typography: {
    fontFamily: '"Inter", "Segoe UI", sans-serif',
    h1: {
      fontWeight: 700,
      letterSpacing: "-0.03em",
      lineHeight: 1.12,
    },
    h2: {
      fontWeight: 700,
      letterSpacing: "-0.025em",
      lineHeight: 1.15,
    },
    h3: {
      fontWeight: 700,
      letterSpacing: "-0.02em",
      lineHeight: 1.2,
    },
    h4: {
      fontWeight: 700,
      letterSpacing: "-0.02em",
      lineHeight: 1.25,
    },
    h5: {
      fontWeight: 600,
      letterSpacing: "-0.015em",
      lineHeight: 1.3,
    },
    h6: {
      fontWeight: 600,
      letterSpacing: "-0.01em",
      lineHeight: 1.3,
    },
    body1: {
      lineHeight: 1.6,
    },
    body2: {
      lineHeight: 1.55,
    },
    overline: {
      fontFamily: '"IBM Plex Mono", ui-monospace, monospace',
      fontWeight: 500,
      fontSize: 11,
      letterSpacing: "0.1em",
      textTransform: "uppercase",
    },
    button: {
      fontWeight: 600,
      letterSpacing: "0.01em",
      textTransform: "none",
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          color: ink,
          backgroundColor: "#f3f5f7",
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          border: `1px solid ${border}`,
          boxShadow: "0 1px 2px rgba(16, 24, 40, 0.04)",
        },
      },
    },
    MuiButton: {
      defaultProps: {
        disableElevation: true,
      },
      styleOverrides: {
        root: {
          minHeight: 40,
          borderRadius: 8,
          paddingInline: 16,
        },
        containedPrimary: {
          "&:hover": {
            backgroundColor: tealHover,
          },
        },
        containedSecondary: {
          "&:hover": {
            backgroundColor: indigoDark,
          },
        },
        outlined: {
          borderColor: border,
          color: ink,
          "&:hover": {
            borderColor: ink,
            backgroundColor: alpha(ink, 0.03),
          },
        },
        text: {
          color: ink,
          "&:hover": {
            backgroundColor: alpha(ink, 0.05),
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          height: 28,
          borderRadius: 6,
          backgroundColor: "#eef0f3",
          color: ink,
          fontFamily: '"IBM Plex Mono", ui-monospace, monospace',
          fontSize: 12,
          fontWeight: 500,
          "&:hover": {
            backgroundColor: "#e2e5ea",
          },
        },
        deleteIcon: {
          color: muted,
          "&:hover": {
            color: ink,
          },
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          backgroundColor: "#ffffff",
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: border,
          },
          "&:hover .MuiOutlinedInput-notchedOutline": {
            borderColor: "#c3ccd6",
          },
          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
            borderColor: teal,
            borderWidth: 1,
          },
        },
        input: {
          paddingTop: 12,
          paddingBottom: 12,
        },
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          fontWeight: 500,
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: "none",
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          height: 6,
          borderRadius: 999,
          backgroundColor: "#e2e5ea",
        },
        bar: {
          borderRadius: 999,
        },
      },
    },
    MuiSlider: {
      styleOverrides: {
        root: {
          color: teal,
        },
        rail: {
          opacity: 1,
          backgroundColor: "#d5dae1",
        },
        track: {
          border: "none",
        },
        thumb: {
          width: 16,
          height: 16,
          boxShadow: "none",
        },
      },
    },
    MuiSwitch: {
      styleOverrides: {
        switchBase: {
          "&.Mui-checked": {
            color: "#ffffff",
          },
          "&.Mui-checked + .MuiSwitch-track": {
            backgroundColor: teal,
            opacity: 1,
          },
        },
        track: {
          opacity: 1,
          backgroundColor: "#d5dae1",
        },
      },
    },
    MuiMenuItem: {
      styleOverrides: {
        root: {
          minHeight: 36,
        },
      },
    },
  },
});
