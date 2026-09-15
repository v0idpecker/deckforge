import { useState } from "react";
import { Box, Button, Container, IconButton, Stack, Typography } from "@mui/material";
import logoUrl from "../assets/logo-dark.svg";

const authBaseUrl = import.meta.env.VITE_AUTH_BASE_URL ?? "/auth";

type ThemeName = "dark" | "light";

interface Palette {
  bg: string;
  surface: string;
  border: string;
  borderSoft: string;
  text: string;
  headline: string;
  muted: string;
  red: string;
  primary: string;
  orange: string;
  amber: string;
  magenta: string;
}

const accents = {
  red: "#F72219",
  primary: "#F84919",
  orange: "#F77019",
  amber: "#F79719",
  magenta: "#F7197F",
};

const darkPalette: Palette = {
  bg: "#0D0A08",
  surface: "#181210",
  border: "rgba(248, 73, 25, 0.14)",
  borderSoft: "rgba(245, 237, 232, 0.08)",
  text: "#F5EDE8",
  headline: "#E9DBD2",
  muted: "#A3948C",
  ...accents,
};

const lightPalette: Palette = {
  bg: "#FAF4EE",
  surface: "#FFFFFF",
  border: "rgba(248, 73, 25, 0.18)",
  borderSoft: "rgba(26, 18, 13, 0.08)",
  text: "#2A1E17",
  headline: "#241A14",
  muted: "#8A776C",
  ...accents,
};

const palettes: Record<ThemeName, Palette> = {
  dark: darkPalette,
  light: lightPalette,
};

const STORAGE_KEY = "ankislop-theme";

function initialTheme(): ThemeName {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "dark" || stored === "light") {
      return stored;
    }
  } catch {
    return "dark";
  }
  return "dark";
}

const emberGradient = `linear-gradient(90deg, ${accents.red}, ${accents.primary} 45%, ${accents.orange} 72%, ${accents.amber})`;

const backgrounds: Record<ThemeName, string> = {
  dark: [
    "radial-gradient(1100px 640px at 88% -12%, rgba(247, 34, 25, 0.14), transparent 62%)",
    "radial-gradient(1000px 760px at -14% 114%, rgba(248, 73, 25, 0.12), transparent 62%)",
    "radial-gradient(700px 500px at 50% 118%, rgba(247, 25, 127, 0.07), transparent 60%)",
    darkPalette.bg,
  ].join(", "),
  light: [
    "radial-gradient(1100px 640px at 88% -12%, rgba(247, 34, 25, 0.07), transparent 62%)",
    "radial-gradient(1000px 760px at -14% 114%, rgba(248, 73, 25, 0.06), transparent 62%)",
    "radial-gradient(700px 500px at 50% 118%, rgba(247, 25, 127, 0.04), transparent 60%)",
    lightPalette.bg,
  ].join(", "),
};

interface Point {
  index: string;
  title: string;
  description: string;
  accent: string;
}

const steps: Point[] = [
  {
    index: "01",
    title: "Bring your words",
    description:
      "A list from your textbook, words from an article or a show you watched — just paste them in.",
    accent: accents.red,
  },
  {
    index: "02",
    title: "Get real flashcards",
    description:
      "Each word comes back as a card with a natural example sentence and a translation, matched to your level.",
    accent: accents.orange,
  },
  {
    index: "03",
    title: "Let Anki do the rest",
    description:
      "Download the deck, open it in Anki, and your reviews are scheduled automatically.",
    accent: accents.amber,
  },
];

const whyPoints: Point[] = [
  {
    index: "01",
    title: "You forget words",
    description:
      "Looking up a word twice is normal — memorizing it once is the hard part.",
    accent: accents.red,
  },
  {
    index: "02",
    title: "Reviews hit the sweet spot",
    description:
      "Anki quizzes you a day, a week, then a month later — right when memory starts to fade.",
    accent: accents.orange,
  },
  {
    index: "03",
    title: "Words move to long-term memory",
    description:
      "Minutes a day, and the vocabulary stops slipping away.",
    accent: accents.amber,
  },
];

const sparks = [
  { top: "22%", left: "18%", size: 4, color: accents.magenta, delay: "0s" },
  { top: "34%", left: "82%", size: 5, color: accents.orange, delay: "0.8s" },
  { top: "58%", left: "12%", size: 3, color: accents.amber, delay: "1.6s" },
];

const sparkOpacity: Record<ThemeName, { xs: number; md: number; anim: number }> = {
  dark: { xs: 0.35, md: 0.55, anim: 0.7 },
  light: { xs: 0.2, md: 0.3, anim: 0.45 },
};

function SunIcon() {
  return (
    <Box
      component="svg"
      viewBox="0 0 24 24"
      sx={{ width: 20, height: 20 }}
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      aria-hidden
    >
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
    </Box>
  );
}

function MoonIcon() {
  return (
    <Box
      component="svg"
      viewBox="0 0 24 24"
      sx={{ width: 18, height: 18 }}
      fill="currentColor"
      aria-hidden
    >
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </Box>
  );
}

function GoogleG() {
  return (
    <Box
      component="svg"
      viewBox="0 0 48 48"
      sx={{ width: 20, height: 20, mr: 1 }}
      aria-hidden
    >
      <path
        fill="#FFC107"
        d="M43.611 20.083H42V20H24v8h11.303c-1.649 4.657-6.08 8-11.303 8-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-1.341-.138-2.65-.389-3.917z"
      />
      <path
        fill="#FF3D00"
        d="M6.306 14.691l6.571 4.819C14.655 15.108 18.961 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 16.318 4 9.656 8.337 6.306 14.691z"
      />
      <path
        fill="#4CAF50"
        d="M24 44c5.166 0 9.86-1.977 13.409-5.192l-6.19-5.238C29.211 35.091 26.715 36 24 36c-5.202 0-9.619-3.317-11.283-7.946l-6.522 5.025C9.505 39.556 16.227 44 24 44z"
      />
      <path
        fill="#1976D2"
        d="M43.611 20.083H42V20H24v8h11.303c-.792 2.237-2.231 4.166-4.087 5.571l.003-.002 6.19 5.238C36.971 39.205 44 34 44 24c0-1.341-.138-2.65-.389-3.917z"
      />
    </Box>
  );
}

function googleButtonSx(theme: ThemeName) {
  if (theme === "light") {
    return {
      mt: 1.5,
      px: 4,
      py: 1.4,
      borderRadius: 2,
      backgroundColor: "#FFFFFF",
      color: "#1F1F1F",
      fontSize: 16,
      fontWeight: 600,
      textTransform: "none",
      boxShadow: `0 0 0 1px rgba(26, 18, 13, 0.12), 0 6px 18px rgba(26, 18, 13, 0.08)`,
      transition: "transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease",
      "&:hover": {
        backgroundColor: "#FFF7F2",
        transform: "translateY(-2px)",
        boxShadow: `0 0 0 1px rgba(26, 18, 13, 0.16), 0 12px 28px rgba(26, 18, 13, 0.12)`,
      },
    } as const;
  }
  return {
    mt: 1.5,
    px: 4,
    py: 1.4,
    borderRadius: 2,
    backgroundColor: "#FFFFFF",
    color: "#1F1F1F",
    fontSize: 16,
    fontWeight: 600,
    textTransform: "none",
    boxShadow: `0 0 0 1px rgba(255, 255, 255, 0.10), 0 12px 36px rgba(247, 34, 25, 0.22)`,
    transition: "transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease",
    "&:hover": {
      backgroundColor: "#FFF7F2",
      transform: "translateY(-2px)",
      boxShadow: `0 0 0 1px rgba(255, 255, 255, 0.14), 0 18px 44px rgba(247, 34, 25, 0.32)`,
    },
  } as const;
}

function PointCard({
  point,
  palette,
  theme,
}: {
  point: Point;
  palette: Palette;
  theme: ThemeName;
}) {
  const hoverShadow =
    theme === "dark"
      ? `0 10px 36px rgba(248, 73, 25, 0.12)`
      : `0 10px 28px rgba(26, 18, 13, 0.10)`;
  return (
    <Stack
      sx={{
        p: 3,
        flex: 1,
        maxWidth: { sm: 340 },
        borderRadius: 3,
        backgroundColor: palette.surface,
        border: `1px solid ${palette.border}`,
        transition: "border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease",
        "&:hover": {
          borderColor: point.accent,
          boxShadow: hoverShadow,
          transform: "translateY(-3px)",
        },
      }}
    >
      <Typography
        className="mono"
        sx={{
          fontSize: 13,
          fontWeight: 600,
          letterSpacing: "0.12em",
          color: point.accent,
          textShadow:
            theme === "dark" ? `0 0 14px ${point.accent}` : "none",
        }}
      >
        {point.index}
      </Typography>
      <Typography sx={{ mt: 1, fontSize: 18, fontWeight: 600, color: palette.text }}>
        {point.title}
      </Typography>
      <Typography
        sx={{ mt: 0.75, fontSize: 14, lineHeight: 1.6, color: palette.muted }}
      >
        {point.description}
      </Typography>
    </Stack>
  );
}

function PointRow({
  points,
  palette,
  theme,
}: {
  points: Point[];
  palette: Palette;
  theme: ThemeName;
}) {
  return (
    <Stack
      direction={{ xs: "column", sm: "row" }}
      spacing={2}
      justifyContent="center"
    >
      {points.map((point) => (
        <PointCard key={point.index} point={point} palette={palette} theme={theme} />
      ))}
    </Stack>
  );
}

function SectionLabel({
  children,
  palette,
}: {
  children: string;
  palette: Palette;
}) {
  return (
    <Typography
      className="mono"
      textAlign="center"
      sx={{
        fontSize: 11,
        fontWeight: 600,
        letterSpacing: "0.22em",
        color: palette.muted,
        mb: 2.5,
      }}
    >
      {children}
    </Typography>
  );
}

function LandingPage() {
  const [theme, setTheme] = useState<ThemeName>(initialTheme);
  const palette = palettes[theme];

  const toggleTheme = () => {
    const next: ThemeName = theme === "dark" ? "light" : "dark";
    setTheme(next);
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch {
      return;
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        background: backgrounds[theme],
        transition: "background 0.3s ease",
      }}
    >
      {sparks.map((spark, i) => (
        <Box
          key={i}
          aria-hidden
          sx={{
            position: "fixed",
            top: spark.top,
            left: spark.left,
            width: spark.size,
            height: spark.size,
            borderRadius: "50%",
            backgroundColor: spark.color,
            boxShadow: `0 0 ${spark.size * 3}px ${spark.size}px ${spark.color}`,
            opacity: {
              xs: sparkOpacity[theme].xs,
              md: sparkOpacity[theme].md,
            },
            animation: "emberFloat 5s ease-in-out infinite",
            animationDelay: spark.delay,
            "@keyframes emberFloat": {
              "0%, 100%": { transform: "translateY(0)", opacity: 0.3 },
              "50%": {
                transform: "translateY(-14px)",
                opacity: sparkOpacity[theme].anim,
              },
            },
          }}
        />
      ))}

      <Container maxWidth="lg" sx={{ py: { xs: 2.5, md: 3.5 } }}>
        <Stack direction="row" alignItems="center" justifyContent="space-between">
          <Box
            component="img"
            src={logoUrl}
            alt="AnkiSlop"
            sx={{
              height: { xs: 44, md: 52 },
              width: "auto",
              filter: "drop-shadow(0 4px 20px rgba(248, 73, 25, 0.25))",
            }}
          />
          <IconButton
            onClick={toggleTheme}
            aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
            sx={{
              color: palette.muted,
              border: `1px solid ${palette.borderSoft}`,
              borderRadius: 2,
              transition: "color 0.2s ease, border-color 0.2s ease",
              "&:hover": {
                color: palette.primary,
                borderColor: palette.border,
                backgroundColor: "transparent",
              },
            }}
          >
            {theme === "dark" ? <SunIcon /> : <MoonIcon />}
          </IconButton>
        </Stack>
      </Container>

      <Container
        maxWidth="md"
        sx={{
          flex: 1,
          minHeight: { xs: "62vh", md: "76vh" },
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          py: { xs: 4, md: 5 },
        }}
      >
        <Stack spacing={3} alignItems="center" textAlign="center">
          <Stack
            direction="row"
            spacing={1.25}
            alignItems="center"
            sx={{
              px: 2,
              py: 0.75,
              borderRadius: 999,
              border: `1px solid ${palette.border}`,
              backgroundColor: "rgba(248, 73, 25, 0.06)",
            }}
          >
            <Box
              sx={{
                width: 6,
                height: 6,
                borderRadius: "50%",
                backgroundColor: palette.magenta,
                boxShadow: `0 0 8px 2px ${palette.magenta}`,
              }}
            />
            <Typography
              className="mono"
              sx={{
                fontSize: 11,
                fontWeight: 600,
                letterSpacing: "0.22em",
                color: palette.muted,
              }}
            >
              FORGET LESS · REMEMBER LONGER
            </Typography>
          </Stack>

          <Typography
            variant="h1"
            sx={{
              fontSize: { xs: "2.7rem", md: "4rem" },
              fontWeight: 700,
              letterSpacing: "-0.03em",
              lineHeight: 1.12,
              width: "100%",
              textAlign: "center",
              color: palette.headline,
            }}
          >
            Learn words once.
            <Box
              component="span"
              sx={{
                display: "block",
                background: emberGradient,
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                filter:
                  theme === "dark"
                    ? "drop-shadow(0 0 24px rgba(248, 73, 25, 0.35))"
                    : "drop-shadow(0 0 18px rgba(248, 73, 25, 0.18))",
              }}
            >
              Remember them for good.
            </Box>
          </Typography>

          <Typography
            variant="body1"
            sx={{
              maxWidth: 540,
              color: palette.muted,
              fontSize: { xs: 15, md: 17 },
              lineHeight: 1.65,
            }}
          >
            AnkiSlop turns any list of new words into smart flashcards with
            real example sentences and translations — and schedules your
            reviews so the words actually stay in your head.
          </Typography>

          <Button
            variant="contained"
            size="large"
            disableElevation
            startIcon={<GoogleG />}
            onClick={() => {
              window.location.href = `${authBaseUrl}/google`;
            }}
            sx={googleButtonSx(theme)}
          >
            Sign in with Google
          </Button>
        </Stack>
      </Container>

      <Container maxWidth="lg" sx={{ pb: { xs: 4, md: 6 } }}>
        <SectionLabel palette={palette}>THE METHOD</SectionLabel>
        <Typography
          variant="h2"
          textAlign="center"
          sx={{
            fontSize: { xs: "1.8rem", md: "2.4rem" },
            fontWeight: 700,
            letterSpacing: "-0.02em",
            color: palette.text,
          }}
        >
          Why it works
        </Typography>
        <Typography
          textAlign="center"
          sx={{
            mt: 1.5,
            mx: "auto",
            maxWidth: 640,
            fontSize: { xs: 15, md: 16 },
            lineHeight: 1.7,
            color: palette.muted,
          }}
        >
          Every memory fades on a curve. But if you recall a word right before
          you'd forget it, the memory resets — and lasts longer each time. Apps
          like Anki automate this: they show you a card at the exact moment
          you're about to forget it. That's spaced repetition — the method
          behind some of the most successful language learners.
        </Typography>
        <Box sx={{ mt: 3.5 }}>
          <PointRow points={whyPoints} palette={palette} theme={theme} />
        </Box>
      </Container>

      <Container maxWidth="lg" sx={{ pb: { xs: 4, md: 6 } }}>
        <SectionLabel palette={palette}>HOW IT WORKS</SectionLabel>
        <PointRow points={steps} palette={palette} theme={theme} />
      </Container>

      <Container maxWidth="lg" sx={{ pb: { xs: 3, md: 4 } }}>
        <Stack
          direction="row"
          justifyContent="center"
          sx={{ pt: 3, borderTop: `1px solid ${palette.borderSoft}` }}
        >
          <Typography
            className="mono"
            sx={{
              fontSize: 11,
              letterSpacing: "0.18em",
              color: palette.muted,
            }}
          >
            WORD LISTS IN · ANKI DECKS OUT ·{" "}
            <Box component="span" sx={{ color: palette.primary }}>
              ANKISLOP
            </Box>
          </Typography>
        </Stack>
      </Container>
    </Box>
  );
}

export default LandingPage;
