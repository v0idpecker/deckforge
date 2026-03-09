import { createTheme } from '@mui/material/styles'

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2D6A4F',
      light: '#EBF5EE',
      dark: '#245740',
    },
    background: {
      default: '#F7F8F5',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#1A1F1C',
      secondary: '#7A8A80',
    },
    divider: '#E8EAE4',
    error: {
      main: '#C0392B',
      light: '#FDECEA',
    },
    success: {
      main: '#2D6A4F',
      light: '#EBF5EE',
    },
  },
  shape: {
    borderRadius: 16,
  },
  typography: {
    fontFamily: '"DM Sans", "Segoe UI", sans-serif',
    h4: {
      fontWeight: 700,
      letterSpacing: '-0.02em',
      lineHeight: 1.15,
    },
    h6: {
      fontWeight: 700,
      letterSpacing: '-0.01em',
    },
    body1: {
      lineHeight: 1.65,
    },
    body2: {
      lineHeight: 1.6,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
      letterSpacing: '0.01em',
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: '#F7F8F5',
          color: '#1A1F1C',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          border: '1px solid #E8EAE4',
          boxShadow: '0 8px 24px rgba(26, 31, 28, 0.04)',
          transition: 'box-shadow 0.2s ease, border-color 0.2s ease',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          paddingLeft: 18,
          paddingRight: 18,
          transition: 'all 0.2s ease',
        },
        containedPrimary: {
          boxShadow: 'none',
        },
        outlined: {
          borderColor: '#E8EAE4',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 999,
          backgroundColor: '#EBF5EE',
          color: '#1A1F1C',
          fontFamily: '"DM Mono", ui-monospace, monospace',
          border: '1px solid #D9E9DE',
          transition: 'all 0.2s ease',
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
})
