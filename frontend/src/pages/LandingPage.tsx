import { Box, Button, Container, Paper, Stack, SvgIcon, Typography } from "@mui/material";

const authBaseUrl = import.meta.env.VITE_AUTH_BASE_URL ?? "/auth";

const steps = [
  {
    index: "01",
    title: "Paste words",
    description:
      "Drop a raw list — newlines or commas, any casing, duplicates removed.",
    color: "#0d9488",
    tint: "rgba(13, 148, 136, 0.05)",
    border: "rgba(13, 148, 136, 0.2)",
  },
  {
    index: "02",
    title: "Generate context",
    description:
      "Each word gets example sentences with translations at your chosen level.",
    color: "#4f46e5",
    tint: "rgba(79, 70, 229, 0.05)",
    border: "rgba(79, 70, 229, 0.2)",
  },
  {
    index: "03",
    title: "Export deck",
    description:
      "Download an `.apkg` file and import it straight into Anki.",
    color: "#10b981",
    tint: "rgba(16, 185, 129, 0.05)",
    border: "rgba(16, 185, 129, 0.2)",
  },
];

function ForgeMark() {
  return (
    <SvgIcon viewBox="0 0 24 24" sx={{ fontSize: 16 }}>
      <path d="M13 2l-1.7 6H7.5a.5.5 0 0 0-.41.79l3.77 5.39L9 22l7.91-11.21A.5.5 0 0 0 16.5 10h-3.8L14 2h-1z" />
    </SvgIcon>
  );
}

function LandingPage() {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        background:
          "radial-gradient(1000px 620px at 90% -10%, rgba(79, 70, 229, 0.06), transparent 60%), radial-gradient(900px 700px at -10% 110%, rgba(13, 148, 136, 0.05), transparent 60%)",
      }}
    >
      <Container maxWidth="lg" sx={{ py: { xs: 2.5, md: 3.5 } }}>
        <Stack direction="row" alignItems="center">
          <Stack direction="row" spacing={1.5} alignItems="center">
            <Box
              sx={{
                width: 30,
                height: 30,
                borderRadius: 2,
                background: "linear-gradient(135deg, #0d9488, #4f46e5)",
                color: "#ffffff",
                display: "grid",
                placeItems: "center",
              }}
            >
              <ForgeMark />
            </Box>
            <Typography variant="h6">DeckForge</Typography>
          </Stack>
        </Stack>
      </Container>

      <Container
        maxWidth="md"
        sx={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          py: { xs: 4, md: 6 },
        }}
      >
        <Stack spacing={3} alignItems="center" textAlign="center">
          <Typography
            variant="h1"
            sx={{ fontSize: { xs: "2.4rem", md: "3.4rem" }, maxWidth: 640 }}
          >
            Turn word lists into{" "}
            <Box component="span" sx={{ color: "primary.main" }}>
              Anki decks
            </Box>
          </Typography>
          <Typography
            variant="body1"
            sx={{
              maxWidth: 480,
              color: "text.secondary",
              fontSize: { xs: 15, md: 17 },
            }}
          >
            DeckForge normalizes your words, generates example sentences with
            translations at your level, and packages everything into an `.apkg`
            file.
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={() => {
              window.location.href = `${authBaseUrl}/google`;
            }}
            sx={{ mt: 1, px: 4 }}
          >
            Sign in with Google
          </Button>
        </Stack>
      </Container>

      <Container maxWidth="lg" sx={{ pb: { xs: 4, md: 6 } }}>
        <Stack
          direction={{ xs: "column", sm: "row" }}
          spacing={2}
          justifyContent="center"
        >
          {steps.map((step) => (
            <Paper
              key={step.index}
              sx={{
                p: 3,
                flex: 1,
                maxWidth: { sm: 320 },
                backgroundColor: step.tint,
                borderColor: step.border,
              }}
            >
              <Typography
                className="mono"
                variant="overline"
                sx={{ color: step.color }}
              >
                {step.index}
              </Typography>
              <Typography variant="h6" sx={{ mt: 1 }}>
                {step.title}
              </Typography>
              <Typography
                variant="body2"
                sx={{ mt: 0.75, color: "text.secondary" }}
              >
                {step.description}
              </Typography>
            </Paper>
          ))}
        </Stack>
      </Container>
    </Box>
  );
}

export default LandingPage;
