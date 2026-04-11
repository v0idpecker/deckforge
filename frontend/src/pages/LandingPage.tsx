import { Box, Button, Container, Paper, Stack, SvgIcon, Typography } from "@mui/material";

const authBaseUrl = import.meta.env.VITE_AUTH_BASE_URL ?? "/auth";

const steps = [
  {
    index: "01",
    title: "Feed the forge",
    description: "Drop any raw list. New lines, commas, mixed casing, messy notes.",
    tone: "#ff6b2c",
  },
  {
    index: "02",
    title: "Spin context",
    description: "DeckForge normalizes, finds sentences, and layers in translation.",
    tone: "#2358ff",
  },
  {
    index: "03",
    title: "Export the deck",
    description: "Receive an `.apkg` package built for immediate import into Anki.",
    tone: "#2d8f5c",
  },
];

const specimenWords = [
  "run",
  "wanderlust",
  "lernen",
  "bonjour",
  "caminhar",
  "apple",
  "tempo",
  "lernen",
];

const tickerWords = [
  "raw words",
  "normalized lemmas",
  "context sentences",
  "translation pairs",
  "anki package",
  "study faster",
  "wordlists in",
  "decks out",
];

function BurstIcon() {
  return (
    <SvgIcon viewBox="0 0 24 24" sx={{ fontSize: 22 }}>
      <path d="M12 2l1.45 5.24L19 5l-2.24 4.55L22 12l-5.24 1.45L19 19l-5.55-2.24L12 22l-1.45-5.24L5 19l2.24-5.55L2 12l5.24-2.45L5 5l5.55 2.24L12 2z" />
    </SvgIcon>
  );
}

function ArrowIcon() {
  return (
    <SvgIcon viewBox="0 0 24 24" sx={{ fontSize: 18 }}>
      <path d="M4 12h11.17l-3.58 3.59L13 17l6-6-6-6-1.41 1.41L15.17 10H4v2z" />
    </SvgIcon>
  );
}

function LandingPage() {
  return (
    <Box
      sx={{
        position: "relative",
        minHeight: "100vh",
        overflow: "hidden",
        py: { xs: 2.5, md: 4 },
      }}
    >
      <Box
        className="float-slow"
        sx={{
          position: "absolute",
          top: { xs: -40, md: -20 },
          right: { xs: -50, md: 80 },
          width: { xs: 180, md: 260 },
          height: { xs: 180, md: 260 },
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(255, 107, 44, 0.36), rgba(255, 107, 44, 0))",
          pointerEvents: "none",
        }}
      />
      <Box
        className="float-slower"
        sx={{
          position: "absolute",
          left: { xs: -60, md: 40 },
          bottom: { xs: 140, md: 30 },
          width: { xs: 200, md: 280 },
          height: { xs: 200, md: 280 },
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(35, 88, 255, 0.24), rgba(35, 88, 255, 0))",
          pointerEvents: "none",
        }}
      />

      <Container maxWidth="xl" sx={{ position: "relative", zIndex: 1 }}>
        <Stack spacing={{ xs: 3, md: 4 }}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: 2,
              flexWrap: "wrap",
            }}
          >
            <Stack direction="row" spacing={1.25} alignItems="center">
              <Box
                sx={{
                  width: 44,
                  height: 44,
                  borderRadius: "50%",
                  border: "2px solid var(--ink)",
                  backgroundColor: "var(--signal-yellow)",
                  display: "grid",
                  placeItems: "center",
                  boxShadow: "4px 4px 0 rgba(23, 19, 18, 0.16)",
                }}
              >
                <BurstIcon />
              </Box>
              <Box>
                <Typography variant="overline">DeckForge</Typography>
                <Typography variant="body2" sx={{ color: "text.secondary" }}>
                  Editorial study engine for word lists
                </Typography>
              </Box>
            </Stack>

            <Paper
              className="poster-surface panel-reveal"
              sx={{
                px: 1.5,
                py: 1,
                borderRadius: 999,
                backgroundColor: "rgba(255, 255, 255, 0.55)",
              }}
            >
              <Stack direction="row" spacing={1.5} alignItems="center">
                <Typography variant="overline" sx={{ color: "text.secondary" }}>
                  Google Sign-In
                </Typography>
                <Typography className="mono" sx={{ fontSize: 12 }}>
                  /auth/google
                </Typography>
              </Stack>
            </Paper>
          </Box>

          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "1fr", lg: "minmax(0, 1.15fr) minmax(360px, 0.85fr)" },
              gap: 3,
              alignItems: "stretch",
            }}
          >
            <Paper
              className="poster-surface panel-reveal"
              sx={{
                p: { xs: 3, md: 4.5 },
                borderRadius: { xs: 6, md: 8 },
                minHeight: { md: 620 },
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                background:
                  "linear-gradient(145deg, rgba(255,255,255,0.8), rgba(255,246,231,0.94))",
              }}
            >
              <Stack spacing={{ xs: 3, md: 4 }}>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 2,
                    flexWrap: "wrap",
                    alignItems: "center",
                  }}
                >
                  <Paper
                    sx={{
                      px: 1.5,
                      py: 0.8,
                      borderRadius: 999,
                      backgroundColor: "rgba(255, 255, 255, 0.72)",
                    }}
                  >
                    <Stack direction="row" spacing={1} alignItems="center">
                      <ArrowIcon />
                      <Typography variant="overline" sx={{ color: "text.secondary" }}>
                        Words in. Decks out.
                      </Typography>
                    </Stack>
                  </Paper>

                  <Typography className="mono" sx={{ fontSize: 12, color: "text.secondary" }}>
                    no templates / no spreadsheets / no manual card crafting
                  </Typography>
                </Box>

                <Box>
                  <Typography
                    variant="h1"
                    sx={{
                      fontSize: { xs: "3.5rem", sm: "4.75rem", md: "6.5rem" },
                      maxWidth: 900,
                    }}
                  >
                    Turn stray words into a{" "}
                    <Box component="span" sx={{ color: "primary.main" }}>
                      vivid
                    </Box>{" "}
                    Anki deck with one pass through the forge.
                  </Typography>

                  <Typography
                    variant="body1"
                    sx={{
                      mt: 2.5,
                      maxWidth: 680,
                      fontSize: { xs: 16, md: 18 },
                      color: "text.secondary",
                    }}
                  >
                    DeckForge takes the roughest possible input, cleans it up, adds
                    context, translation, and ships back an `.apkg` file that behaves
                    exactly like your usual Anki import workflow.
                  </Typography>
                </Box>

                <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5}>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={() => {
                      window.location.href = `${authBaseUrl}/google`;
                    }}
                    sx={{
                      minWidth: { sm: 240 },
                      fontSize: 15,
                    }}
                  >
                    Start With Google
                  </Button>
                  <Paper
                    sx={{
                      px: 2,
                      py: 1.25,
                      borderRadius: 999,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      backgroundColor: "rgba(35, 88, 255, 0.08)",
                    }}
                  >
                    <Typography className="mono" sx={{ fontSize: 12 }}>
                      output: `.apkg` / example sentences / translations
                    </Typography>
                  </Paper>
                </Stack>
              </Stack>

              <Box
                sx={{
                  display: "grid",
                  gridTemplateColumns: { xs: "1fr", sm: "repeat(3, minmax(0, 1fr))" },
                  gap: 1.5,
                  mt: { xs: 3, md: 4 },
                }}
              >
                {[
                  ["Parse", "dedupe and keep the list clean"],
                  ["Augment", "normalize, translate, and source context"],
                  ["Export", "ship a ready-to-import Anki package"],
                ].map(([label, description]) => (
                  <Paper
                    key={label}
                    sx={{
                      p: 2,
                      borderRadius: 4,
                      backgroundColor: "rgba(255, 255, 255, 0.64)",
                    }}
                  >
                    <Typography variant="overline" sx={{ color: "text.secondary" }}>
                      {label}
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 0.75 }}>
                      {description}
                    </Typography>
                  </Paper>
                ))}
              </Box>
            </Paper>

            <Paper
              className="poster-surface panel-reveal"
              sx={{
                p: { xs: 2.5, md: 3 },
                borderRadius: { xs: 6, md: 8 },
                display: "flex",
                flexDirection: "column",
                gap: 2,
                transform: { lg: "rotate(1.25deg)" },
                background:
                  "linear-gradient(180deg, rgba(255,255,255,0.76), rgba(248, 201, 79, 0.16))",
              }}
            >
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  gap: 2,
                }}
              >
                <Box>
                  <Typography variant="overline" sx={{ color: "text.secondary" }}>
                    Deck Blueprint
                  </Typography>
                  <Typography variant="h5" sx={{ mt: 0.5 }}>
                    Issue 01: language salvage
                  </Typography>
                </Box>
                <Paper
                  sx={{
                    width: 54,
                    height: 54,
                    borderRadius: "50%",
                    display: "grid",
                    placeItems: "center",
                    backgroundColor: "var(--signal-yellow)",
                  }}
                >
                  <BurstIcon />
                </Paper>
              </Box>

              <Paper
                sx={{
                  p: 2,
                  borderRadius: 4,
                  backgroundColor: "rgba(255, 255, 255, 0.66)",
                }}
              >
                <Typography variant="overline" sx={{ color: "text.secondary" }}>
                  Raw Intake
                </Typography>
                <Stack
                  direction="row"
                  spacing={1}
                  useFlexGap
                  flexWrap="wrap"
                  sx={{ mt: 1.25 }}
                >
                  {specimenWords.map((word, index) => (
                    <Box
                      key={`${word}-${index}`}
                      className="mono"
                      sx={{
                        px: 1.15,
                        py: 0.65,
                        borderRadius: 999,
                        border: "1.5px solid var(--ink)",
                        backgroundColor: index % 2 === 0 ? "rgba(255,255,255,0.7)" : "rgba(244, 201, 79, 0.3)",
                        fontSize: 12,
                      }}
                    >
                      {word}
                    </Box>
                  ))}
                </Stack>
              </Paper>

              <Box
                sx={{
                  display: "grid",
                  gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
                  gap: 1.25,
                }}
              >
                {[
                  ["Normalize", "lemmas"],
                  ["Compose", "context"],
                  ["Translate", "gloss"],
                ].map(([label, detail], index) => (
                  <Paper
                    key={label}
                    sx={{
                      p: 1.5,
                      borderRadius: 4,
                      textAlign: "center",
                      backgroundColor:
                        index === 1 ? "rgba(35, 88, 255, 0.12)" : "rgba(255, 255, 255, 0.68)",
                    }}
                  >
                    <Typography className="mono" sx={{ fontSize: 11, color: "text.secondary" }}>
                      {label}
                    </Typography>
                    <Typography sx={{ mt: 0.5, fontWeight: 700 }}>{detail}</Typography>
                  </Paper>
                ))}
              </Box>

              <Paper
                sx={{
                  p: 2,
                  borderRadius: 4,
                  backgroundColor: "rgba(23, 19, 18, 0.96)",
                  color: "#fff7ea",
                }}
              >
                <Typography variant="overline" sx={{ color: "rgba(255, 247, 234, 0.66)" }}>
                  Output Preview
                </Typography>
                <Typography variant="h6" sx={{ mt: 1 }}>
                  deckforge-session.apkg
                </Typography>
                <Typography
                  className="mono"
                  sx={{ mt: 1.5, fontSize: 12, color: "rgba(255, 247, 234, 0.74)" }}
                >
                  cards: 48
                </Typography>
                <Typography
                  className="mono"
                  sx={{ fontSize: 12, color: "rgba(255, 247, 234, 0.74)" }}
                >
                  sentences: real usage examples
                </Typography>
                <Typography
                  className="mono"
                  sx={{ fontSize: 12, color: "rgba(255, 247, 234, 0.74)" }}
                >
                  import target: Anki desktop / mobile
                </Typography>
              </Paper>
            </Paper>
          </Box>

          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "1fr", xl: "minmax(0, 1.25fr) minmax(320px, 0.75fr)" },
              gap: 3,
            }}
          >
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: { xs: "1fr", md: "repeat(3, minmax(0, 1fr))" },
                gap: 2,
              }}
            >
              {steps.map((step, index) => (
                <Paper
                  key={step.index}
                  className="poster-surface panel-reveal"
                  sx={{
                    p: 2.5,
                    borderRadius: 5,
                    backgroundColor:
                      index === 1 ? "rgba(35, 88, 255, 0.08)" : "rgba(255, 255, 255, 0.62)",
                  }}
                >
                  <Typography
                    className="mono"
                    sx={{
                      fontSize: 13,
                      color: step.tone,
                    }}
                  >
                    {step.index}
                  </Typography>
                  <Typography variant="h6" sx={{ mt: 1.25 }}>
                    {step.title}
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1, color: "text.secondary" }}>
                    {step.description}
                  </Typography>
                </Paper>
              ))}
            </Box>

            <Paper
              className="poster-surface panel-reveal"
              sx={{
                p: { xs: 2.5, md: 3 },
                borderRadius: 6,
                background:
                  "linear-gradient(180deg, rgba(255,255,255,0.8), rgba(255,107,44,0.12))",
              }}
            >
              <Typography variant="overline" sx={{ color: "text.secondary" }}>
                Why It Feels Different
              </Typography>
              <Typography variant="h5" sx={{ mt: 0.75 }}>
                Less dashboard. More print workshop.
              </Typography>
              <Typography variant="body2" sx={{ mt: 1.25, color: "text.secondary" }}>
                The app behaves exactly like a practical utility, but the interface
                leans into poster typography, tactile panels, and visible structure so
                it feels deliberate instead of anonymous.
              </Typography>
              <Stack spacing={1.25} sx={{ mt: 2.5 }}>
                {[
                  "A warm paper backdrop instead of flat SaaS gray",
                  "Strong outlines and offsets instead of soft glass panels",
                  "Typography that carries the mood, not just the information",
                ].map((line) => (
                  <Box
                    key={line}
                    sx={{
                      display: "flex",
                      gap: 1,
                      alignItems: "flex-start",
                    }}
                  >
                    <Box
                      sx={{
                        width: 10,
                        height: 10,
                        borderRadius: "50%",
                        backgroundColor: "var(--signal-blue)",
                        mt: "7px",
                        flexShrink: 0,
                      }}
                    />
                    <Typography variant="body2">{line}</Typography>
                  </Box>
                ))}
              </Stack>
            </Paper>
          </Box>

          <Paper
            className="poster-surface panel-reveal ticker"
            sx={{
              px: 0,
              py: 1.25,
              borderRadius: 999,
              backgroundColor: "rgba(255, 255, 255, 0.5)",
            }}
          >
            <Box className="ticker-track">
              {[...tickerWords, ...tickerWords].map((word, index) => (
                <Stack
                  key={`${word}-${index}`}
                  direction="row"
                  spacing={1}
                  alignItems="center"
                  sx={{ px: 1.5 }}
                >
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      backgroundColor:
                        index % 3 === 0
                          ? "var(--signal)"
                          : index % 3 === 1
                            ? "var(--signal-blue)"
                            : "var(--signal-yellow)",
                    }}
                  />
                  <Typography className="mono" sx={{ fontSize: 12 }}>
                    {word}
                  </Typography>
                </Stack>
              ))}
            </Box>
          </Paper>
        </Stack>
      </Container>
    </Box>
  );
}

export default LandingPage;
