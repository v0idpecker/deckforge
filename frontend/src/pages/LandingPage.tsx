import { Box, Button, Container, Stack, Typography } from "@mui/material";

const steps = [
  {
    title: "Paste your words",
    description: "Any list, one per line or comma-separated.",
  },
  {
    title: "We do the rest",
    description: "Lemmatization, context sentences, translations.",
  },
  {
    title: "Download and import",
    description: "Ready .apkg file for Anki.",
  },
];

function LandingPage() {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        py: { xs: 6, sm: 8 },
      }}
    >
      <Container maxWidth="sm">
        <Stack spacing={4}>
          <Box>
            <Typography
              variant="overline"
              sx={{
                color: "text.secondary",
                letterSpacing: "0.08em",
                fontFamily: '"DM Mono", ui-monospace, monospace',
              }}
            >
              DECKFORGE
            </Typography>
            <Typography
              variant="h3"
              sx={{
                mt: 1,
                fontWeight: 700,
                letterSpacing: "-0.03em",
                lineHeight: 1.1,
              }}
            >
              Turn any word list into an Anki deck — instantly.
            </Typography>
            <Typography
              variant="body1"
              color="text.secondary"
              sx={{ mt: 2, fontSize: 16, lineHeight: 1.6 }}
            >
              Paste words in any form. DeckForge normalizes them, finds real
              usage examples in context, and packages everything into a
              ready-to-import .apkg deck.
            </Typography>
          </Box>

          <Stack
            direction={{ xs: "column", md: "row" }}
            spacing={2.5}
            sx={{ alignItems: "stretch" }}
          >
            {steps.map((step, index) => (
              <Box key={step.title} sx={{ flex: 1 }}>
                <Typography
                  sx={{
                    color: "primary.main",
                    fontWeight: 700,
                    fontSize: 18,
                  }}
                >
                  {index + 1}
                </Typography>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, mt: 0.5 }}>
                  {step.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {step.description}
                </Typography>
              </Box>
            ))}
          </Stack>

          <Button
            variant="contained"
            size="large"
            onClick={() => {
              window.location.href = "http://127.0.0.1:8000/auth/google";
            }}
            sx={{ alignSelf: "center" }}
          >
            Get started with Google
          </Button>

          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ textAlign: "center" }}
          >
            Already using Anki? DeckForge plugs right in.
          </Typography>
        </Stack>
      </Container>
    </Box>
  );
}

export default LandingPage;
