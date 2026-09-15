import { alpha, createTheme } from "@mui/material/styles";

export type ThemeMode = "dark" | "light";

const primary = "#F84919";
const primaryHover = "#E23D12";
const secondary = "#F77019";
const secondaryHover = "#E06010";

const red = "#F72219";
const amber = "#F79719";
const success = "#10B981";
const info = "#2563EB";

const surfaces = {
  dark: {
    bg: "#0D0A08",
    paper: "#181210",
    ink: "#F5EDE8",
    muted: "#A3948C",
    border: "rgba(245, 237, 232, 0.10)",
    borderStrong: "rgba(245, 237, 232, 0.20)",
    chipBg: "rgba(245, 237, 232, 0.06)",
    chipHover: "rgba(245, 237, 232, 0.11)",
    inputBg: "#1D1512",
    rail: "rgba(245, 237, 232, 0.14)",
    progressBg: "rgba(245, 237, 232, 0.12)",
    paperShadow: "0 1px 2px rgba(0, 0, 0, 0.30)",
  },
  light: {
    bg: "#FAF4EE",
    paper: "#FFFFFF",
    ink: "#2A1E17",
    muted: "#8A776C",
    border: "rgba(26, 18, 13, 0.10)",
    borderStrong: "rgba(26, 18, 13, 0.24)",
    chipBg: "rgba(26, 18, 13, 0.05)",
    chipHover: "rgba(26, 18, 13, 0.09)",
    inputBg: "#FFFFFF",
    rail: "rgba(26, 18, 13, 0.12)",
    progressBg: "rgba(26, 18, 13, 0.08)",
    paperShadow: "0 1px 2px rgba(16, 24, 40, 0.04)",
  },
};

function createAppTheme(mode: ThemeMode) {
  const s = surfaces[mode];
  return createTheme({
    palette: {
      mode,
      primary: {
        main: primary,
        light: "#F97A4A",
        dark: primaryHover,
        contrastText: "#FFFFFF",
      },
      secondary: {
        main: secondary,
        light: "#F9934D",
        dark: secondaryHover,
        contrastText: "#FFFFFF",
      },
      background: {
        default: s.bg,
        paper: s.paper,
      },
      text: {
        primary: s.ink,
        secondary: s.muted,
      },
      divider: s.border,
      error: {
        main: red,
        light: mode === "dark" ? "rgba(247, 34, 25, 0.16)" : "#FDE7E3",
      },
      warning: {
        main: amber,
        light: mode === "dark" ? "rgba(247, 151, 25, 0.16)" : "#FDEEDC",
      },
      success: {
        main: success,
        light: mode === "dark" ? "rgba(16, 185, 129, 0.16)" : "#DCF5EA",
      },
      info: {
        main: info,
        light: mode === "dark" ? "rgba(37, 99, 235, 0.16)" : "#E0EAFA",
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
            color: s.ink,
            backgroundColor: s.bg,
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: "none",
            border: `1px solid ${s.border}`,
            boxShadow: s.paperShadow,
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
              backgroundColor: primaryHover,
            },
          },
          containedSecondary: {
            "&:hover": {
              backgroundColor: secondaryHover,
            },
          },
          outlined: {
            borderColor: s.border,
            color: s.ink,
            "&:hover": {
              borderColor: s.borderStrong,
              backgroundColor: alpha(s.ink, 0.04),
            },
          },
          text: {
            color: s.ink,
            "&:hover": {
              backgroundColor: alpha(s.ink, 0.06),
            },
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            height: 28,
            borderRadius: 6,
            backgroundColor: s.chipBg,
            color: s.ink,
            fontFamily: '"IBM Plex Mono", ui-monospace, monospace',
            fontSize: 12,
            fontWeight: 500,
            "&:hover": {
              backgroundColor: s.chipHover,
            },
          },
          deleteIcon: {
            color: s.muted,
            "&:hover": {
              color: s.ink,
            },
          },
        },
      },
      MuiOutlinedInput: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            backgroundColor: s.inputBg,
            "& .MuiOutlinedInput-notchedOutline": {
              borderColor: s.border,
            },
            "&:hover .MuiOutlinedInput-notchedOutline": {
              borderColor: s.borderStrong,
            },
            "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
              borderColor: primary,
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
            backgroundColor: s.progressBg,
          },
          bar: {
            borderRadius: 999,
          },
        },
      },
      MuiSlider: {
        styleOverrides: {
          root: {
            color: primary,
          },
          rail: {
            opacity: 1,
            backgroundColor: s.rail,
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
              color: "#FFFFFF",
            },
            "&.Mui-checked + .MuiSwitch-track": {
              backgroundColor: primary,
              opacity: 1,
            },
          },
          track: {
            opacity: 1,
            backgroundColor: s.rail,
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
}

export { createAppTheme, primary as brandPrimary };
