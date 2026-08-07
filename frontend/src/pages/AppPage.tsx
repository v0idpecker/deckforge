import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Container,
  FormControl,
  FormControlLabel,
  InputLabel,
  LinearProgress,
  MenuItem,
  Paper,
  Select,
  Slider,
  Stack,
  SvgIcon,
  Switch,
  TextField,
  Typography,
} from "@mui/material";
import { alpha } from "@mui/material/styles";

import {
  createDeckTask,
  downloadDeckResult,
  getDeckTaskStatus,
  listDeckTasks,
} from "../api/decks";
import type {
  DeckTaskHistoryItem,
  DeckItemStageValue,
  DeckItemStatusValue,
  DeckTaskItemStatus,
  DeckTaskStatusValue,
  DifficultyLevel,
} from "../types/decks";

type ViewState = "INPUT" | "PROCESSING" | "DONE";

const TERMINAL_TASK_STATUSES = new Set<DeckTaskStatusValue>([
  "DONE",
  "PARTIALLY_DONE",
]);

const STAGE_LABELS: Record<Exclude<DeckItemStageValue, null>, string> = {
  INIT: "Starting",
  NORMILIZED: "Normalized",
  CONTEXT_GENERATED: "Context ready",
  DONE: "Done",
};

const TASK_STATUS_LABELS: Record<DeckTaskStatusValue, string> = {
  PENDING: "Queued",
  PROCESSING: "Processing",
  DONE: "Done",
  PARTIALLY_DONE: "Partial",
};

const TASK_STATUS_COLORS: Record<DeckTaskStatusValue, string> = {
  PENDING: "#64748b",
  PROCESSING: "#2563eb",
  DONE: "#10b981",
  PARTIALLY_DONE: "#f59e0b",
};

const ITEM_STATUS_LABELS: Record<DeckItemStatusValue, string> = {
  PENDING: "Pending",
  PROCESSING: "Processing",
  DONE: "Done",
  ERROR: "Failed",
};

const ITEM_STATUS_COLORS: Record<DeckItemStatusValue, string> = {
  PENDING: "#94a3b8",
  PROCESSING: "#2563eb",
  DONE: "#10b981",
  ERROR: "#e11d48",
};

const SENTENCE_LANGUAGE_LABELS = {
  english: "English",
  german: "German",
  spanish: "Spanish",
  french: "French",
  italian: "Italian",
} as const;

const TRANSLATION_LANGUAGE_LABELS = {
  russian: "Russian",
  english: "English",
  german: "German",
  spanish: "Spanish",
  french: "French",
} as const;

const DIFFICULTY_LABELS: Record<DifficultyLevel, string> = {
  A1: "A1 (Beginner)",
  A2: "A2 (Elementary)",
  B1: "B1 (Intermediate)",
  B2: "B2 (Upper intermediate)",
  C1: "C1 (Advanced)",
  C2: "C2 (Proficiency)",
};

const DIFFICULTY_LEVELS: DifficultyLevel[] = [
  "A1",
  "A2",
  "B1",
  "B2",
  "C1",
  "C2",
];

function parseWords(raw: string): string[] {
  const uniqueWords: string[] = [];
  const seen = new Set<string>();

  for (const chunk of raw.split(/[\n,]/)) {
    const word = chunk.trim();
    if (!word || seen.has(word)) {
      continue;
    }

    seen.add(word);
    uniqueWords.push(word);
  }

  return uniqueWords;
}

function buildInitialItems(words: string[]): DeckTaskItemStatus[] {
  return words.map((rawWord) => ({
    raw_word: rawWord,
    status: "PENDING",
    stage: null,
  }));
}

function mergeItemsByWords(
  words: string[],
  apiItems: DeckTaskItemStatus[],
): DeckTaskItemStatus[] {
  const itemByWord = new Map(apiItems.map((item) => [item.raw_word, item]));
  const wordsSet = new Set(words);

  const orderedItems = words.map((word) => {
    const pendingItem: DeckTaskItemStatus = {
      raw_word: word,
      status: "PENDING",
      stage: null,
    };

    return itemByWord.get(word) ?? pendingItem;
  });

  const extraItems = apiItems.filter((item) => !wordsSet.has(item.raw_word));

  return [...orderedItems, ...extraItems];
}

function getProcessingSubtitle(stage: DeckItemStageValue): string {
  if (!stage) {
    return STAGE_LABELS.INIT;
  }

  return STAGE_LABELS[stage] ?? STAGE_LABELS.INIT;
}

function getRowLabel(item: DeckTaskItemStatus): string {
  if (item.status === "PROCESSING") {
    return getProcessingSubtitle(item.stage);
  }

  return ITEM_STATUS_LABELS[item.status];
}

function ForgeIcon() {
  return (
    <SvgIcon viewBox="0 0 24 24" sx={{ fontSize: 18 }}>
      <path d="M13 2l-1.7 6H7.5a.5.5 0 0 0-.41.79l3.77 5.39L9 22l7.91-11.21A.5.5 0 0 0 16.5 10h-3.8L14 2h-1z" />
    </SvgIcon>
  );
}

function DownloadIcon() {
  return (
    <SvgIcon viewBox="0 0 24 24" sx={{ fontSize: 22 }}>
      <path d="M5 20h14v-2H5v2zM11 4v8.17L8.41 9.59 7 11l5 5 5-5-1.41-1.41L13 12.17V4h-2z" />
    </SvgIcon>
  );
}

function WordStatusCard({ item }: { item: DeckTaskItemStatus }) {
  const color = ITEM_STATUS_COLORS[item.status];

  return (
    <Stack
      direction="row"
      spacing={1.5}
      alignItems="center"
      sx={{
        py: 0.75,
        px: 1.25,
        borderRadius: 2,
        backgroundColor: alpha(color, 0.06),
      }}
    >
      <Box
        sx={{
          width: 8,
          height: 8,
          borderRadius: "50%",
          backgroundColor: color,
          flexShrink: 0,
        }}
      />
      <Typography
        className="mono"
        title={item.raw_word}
        sx={{
          fontSize: 13,
          flex: 1,
          minWidth: 0,
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap",
        }}
      >
        {item.raw_word}
      </Typography>
      <Typography sx={{ fontSize: 12, fontWeight: 600, color, flexShrink: 0 }}>
        {getRowLabel(item)}
      </Typography>
    </Stack>
  );
}

function CountTile({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  return (
    <Box
      sx={{
        p: 1.5,
        borderRadius: 2,
        backgroundColor: alpha(color, 0.08),
      }}
    >
      <Typography variant="body2" sx={{ color: "text.secondary" }}>
        {label}
      </Typography>
      <Typography sx={{ mt: 0.5, fontSize: 22, fontWeight: 700, color }}>
        {value}
      </Typography>
    </Box>
  );
}

function AppPage() {
  const [hasToken, setHasToken] = useState(false);
  const [viewState, setViewState] = useState<ViewState>("INPUT");
  const [wordsInput, setWordsInput] = useState("");

  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskStatus, setTaskStatus] = useState<DeckTaskStatusValue | null>(null);
  const [submittedWords, setSubmittedWords] = useState<string[]>([]);
  const [items, setItems] = useState<DeckTaskItemStatus[]>([]);
  const [normalizationEnabled, setNormalizationEnabled] = useState(true);
  const [cardsPerWord, setCardsPerWord] = useState(1);
  const [sentenceLang, setSentenceLang] = useState<
    "english" | "german" | "spanish" | "french" | "italian"
  >("english");
  const [translationLang, setTranslationLang] = useState<
    "russian" | "english" | "german" | "spanish" | "french"
  >("russian");
  const [difficulty, setDifficulty] = useState<DifficultyLevel>("B1");

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [taskHistory, setTaskHistory] = useState<DeckTaskHistoryItem[]>([]);

  const parsedWords = useMemo(() => parseWords(wordsInput), [wordsInput]);

  useEffect(() => {
    const url = new URL(window.location.href);
    const token = url.searchParams.get("token");

    if (token) {
      localStorage.setItem("access_token", token);
      url.searchParams.delete("token");
      window.history.replaceState(
        {},
        document.title,
        `${url.pathname}${url.search}${url.hash}`,
      );
    }

    const storedToken = localStorage.getItem("access_token");
    if (!storedToken) {
      window.location.replace("/");
      return;
    }

    setHasToken(true);
  }, []);

  const fetchTaskHistory = async () => {
    try {
      const decks = await listDeckTasks();
      setTaskHistory(decks);
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : "Unknown error";
      setError(message);
    }
  };

  useEffect(() => {
    if (!hasToken) {
      return;
    }

    void fetchTaskHistory();
  }, [hasToken]);

  useEffect(() => {
    if (!hasToken || viewState !== "DONE") {
      return;
    }

    void fetchTaskHistory();
  }, [hasToken, viewState]);

  const downloadTaskFile = async (deckId: string) => {
    const { blob, filename } = await downloadDeckResult(deckId);
    const objectUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = objectUrl;
    link.download = filename ?? `deck-${deckId}.apkg`;
    document.body.append(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(objectUrl);
  };

  const handleGenerateDeck = async () => {
    if (parsedWords.length === 0) {
      return;
    }

    setError(null);
    setIsSubmitting(true);

    try {
      const response = await createDeckTask({
        words: parsedWords,
        options: {
          normalization: normalizationEnabled,
          limit: cardsPerWord,
          sentence_lang: sentenceLang,
          translation_lang: translationLang,
          difficulty,
        },
      });

      if (!response.task_id) {
        throw new Error("Backend returned empty task id.");
      }

      setTaskId(response.task_id);
      setTaskStatus("PENDING");
      setSubmittedWords(parsedWords);
      setItems(buildInitialItems(parsedWords));
      setViewState("PROCESSING");
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : "Unknown error";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteChip = (wordToDelete: string) => {
    const nextWords = parsedWords.filter((word) => word !== wordToDelete);
    setWordsInput(nextWords.join("\n"));
  };

  const handleDownloadDeck = async () => {
    if (!taskId) {
      return;
    }

    setError(null);
    setIsDownloading(true);

    try {
      await downloadTaskFile(taskId);
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : "Unknown error";
      setError(message);
    } finally {
      setIsDownloading(false);
    }
  };

  const handleHistoryDownload = async (deckId: string) => {
    setError(null);

    try {
      await downloadTaskFile(deckId);
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : "Unknown error";
      setError(message);
    }
  };

  const handleCreateAnother = () => {
    setViewState("INPUT");
    setWordsInput("");
    setTaskId(null);
    setTaskStatus(null);
    setSubmittedWords([]);
    setItems([]);
    setError(null);
  };

  const handleSignOut = () => {
    localStorage.removeItem("access_token");
    window.location.replace("/");
  };

  useEffect(() => {
    if (viewState !== "PROCESSING" || !taskId) {
      return;
    }

    let isCancelled = false;

    const pollStatus = async () => {
      try {
        const response = await getDeckTaskStatus(taskId);
        if (isCancelled) {
          return;
        }

        setTaskStatus(response.status);
        setItems(mergeItemsByWords(submittedWords, response.items));

        if (TERMINAL_TASK_STATUSES.has(response.status)) {
          setViewState("DONE");
        }
      } catch (cause) {
        if (isCancelled) {
          return;
        }

        const message = cause instanceof Error ? cause.message : "Unknown error";
        setError(message);
      }
    };

    void pollStatus();
    const intervalId = window.setInterval(() => {
      void pollStatus();
    }, 2500);

    return () => {
      isCancelled = true;
      window.clearInterval(intervalId);
    };
  }, [viewState, taskId, submittedWords]);

  const isPartiallyDone = taskStatus === "PARTIALLY_DONE";
  const totalItems = items.length > 0 ? items.length : submittedWords.length;
  const doneItems = items.filter((item) => item.status === "DONE").length;
  const errorItems = items.filter((item) => item.status === "ERROR").length;
  const processingItems = items.filter((item) => item.status === "PROCESSING").length;
  const pendingItems = items.filter((item) => item.status === "PENDING").length;
  const successfulCards =
    items.length > 0
      ? doneItems
      : taskStatus === "DONE"
        ? submittedWords.length
        : doneItems;
  const processingProgress = totalItems > 0 ? (doneItems / totalItems) * 100 : 0;
  const roundedProgress = Math.round(processingProgress);
  const hasStartedProcessing =
    taskStatus === "PROCESSING" || items.some((item) => item.status !== "PENDING");

  if (!hasToken) {
    return null;
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        py: { xs: 2, md: 4 },
        background:
          "radial-gradient(1000px 620px at 92% -12%, rgba(79, 70, 229, 0.06), transparent 60%), radial-gradient(900px 700px at -12% 112%, rgba(13, 148, 136, 0.05), transparent 60%)",
      }}
    >
      <Container maxWidth="lg">
        <Stack spacing={3}>
          <Stack
            direction="row"
            justifyContent="space-between"
            alignItems="center"
          >
            <Stack direction="row" spacing={1.5} alignItems="center">
              <Box
                sx={{
                  width: 30,
                  height: 30,
                  borderRadius: 2,
                  background:
                    "linear-gradient(135deg, #0d9488, #4f46e5)",
                  color: "#ffffff",
                  display: "grid",
                  placeItems: "center",
                }}
              >
                <ForgeIcon />
              </Box>
              <Typography variant="h6">DeckForge</Typography>
            </Stack>
            <Button variant="text" size="small" onClick={handleSignOut}>
              Sign out
            </Button>
          </Stack>

          {error && <Alert severity="error">{error}</Alert>}

          {viewState === "INPUT" && (
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: {
                  xs: "1fr",
                  lg: "minmax(0, 1.2fr) minmax(340px, 0.8fr)",
                },
                gap: 3,
                alignItems: "start",
              }}
            >
              <Paper sx={{ p: { xs: 2.5, md: 3 } }}>
                <Stack spacing={2.5}>
                  <Stack
                    direction="row"
                    justifyContent="space-between"
                    alignItems="center"
                  >
                    <Stack direction="row" spacing={1.5} alignItems="center">
                      <Box
                        sx={{
                          width: 10,
                          height: 10,
                          borderRadius: "50%",
                          backgroundColor: "primary.main",
                        }}
                      />
                      <Typography variant="h6">Source words</Typography>
                    </Stack>
                    <Typography
                      className="mono"
                      variant="body2"
                      sx={{ color: "primary.main" }}
                    >
                      {parsedWords.length} parsed
                    </Typography>
                  </Stack>

                  <TextField
                    label="Words"
                    placeholder={"apple\nrun\nlernen\nbonjour"}
                    multiline
                    minRows={10}
                    fullWidth
                    value={wordsInput}
                    onChange={(event) => setWordsInput(event.target.value)}
                    InputProps={{
                      sx: {
                        alignItems: "flex-start",
                        fontFamily: '"IBM Plex Mono", ui-monospace, monospace',
                        fontSize: 14,
                        lineHeight: 1.75,
                      },
                    }}
                  />

                  {parsedWords.length > 0 && (
                    <Stack
                      direction="row"
                      spacing={1}
                      useFlexGap
                      flexWrap="wrap"
                    >
                      {parsedWords.map((word) => (
                        <Chip
                          key={word}
                          label={word}
                          onDelete={() => handleDeleteChip(word)}
                        />
                      ))}
                    </Stack>
                  )}
                </Stack>
              </Paper>

              <Stack spacing={3}>
                <Paper sx={{ p: { xs: 2.5, md: 3 } }}>
                  <Stack spacing={2.5}>
                    <Stack direction="row" spacing={1.5} alignItems="center">
                      <Box
                        sx={{
                          width: 10,
                          height: 10,
                          borderRadius: "50%",
                          backgroundColor: "secondary.main",
                        }}
                      />
                      <Typography variant="h6">Options</Typography>
                    </Stack>

                    <FormControlLabel
                      control={
                        <Switch
                          checked={normalizationEnabled}
                          onChange={(event) =>
                            setNormalizationEnabled(event.target.checked)
                          }
                        />
                      }
                      label="Normalize words"
                    />

                    <Box>
                      <Stack
                        direction="row"
                        justifyContent="space-between"
                        alignItems="center"
                      >
                        <Typography variant="body2">Cards per word</Typography>
                        <Typography className="mono" variant="body2">
                          {cardsPerWord}
                        </Typography>
                      </Stack>
                      <Slider
                        min={1}
                        max={5}
                        step={1}
                        value={cardsPerWord}
                        onChange={(_, value) => setCardsPerWord(value as number)}
                        sx={{ mt: 1 }}
                      />
                    </Box>

                    <FormControl fullWidth>
                      <InputLabel id="sentence-lang-label">
                        Example language
                      </InputLabel>
                      <Select
                        labelId="sentence-lang-label"
                        label="Example language"
                        value={sentenceLang}
                        onChange={(event) =>
                          setSentenceLang(
                            event.target.value as typeof sentenceLang,
                          )
                        }
                      >
                        {Object.entries(SENTENCE_LANGUAGE_LABELS).map(
                          ([value, label]) => (
                            <MenuItem key={value} value={value}>
                              {label}
                            </MenuItem>
                          ),
                        )}
                      </Select>
                    </FormControl>

                    <FormControl fullWidth>
                      <InputLabel id="translation-lang-label">
                        Translation language
                      </InputLabel>
                      <Select
                        labelId="translation-lang-label"
                        label="Translation language"
                        value={translationLang}
                        onChange={(event) =>
                          setTranslationLang(
                            event.target.value as typeof translationLang,
                          )
                        }
                      >
                        {Object.entries(TRANSLATION_LANGUAGE_LABELS).map(
                          ([value, label]) => (
                            <MenuItem key={value} value={value}>
                              {label}
                            </MenuItem>
                          ),
                        )}
                      </Select>
                    </FormControl>

                    <FormControl fullWidth>
                      <InputLabel id="difficulty-label">
                        Language level
                      </InputLabel>
                      <Select
                        labelId="difficulty-label"
                        label="Language level"
                        value={difficulty}
                        onChange={(event) =>
                          setDifficulty(event.target.value as DifficultyLevel)
                        }
                      >
                        {DIFFICULTY_LEVELS.map((level) => (
                          <MenuItem key={level} value={level}>
                            {DIFFICULTY_LABELS[level]}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Stack>
                </Paper>

                <Paper
                  sx={{
                    p: { xs: 2.5, md: 3 },
                    backgroundColor: alpha("#f59e0b", 0.04),
                    borderColor: alpha("#f59e0b", 0.22),
                  }}
                >
                  <Stack spacing={2}>
                    <Typography
                      className="mono"
                      variant="body2"
                      sx={{ color: "text.secondary" }}
                    >
                      {parsedWords.length} words ·{" "}
                      {SENTENCE_LANGUAGE_LABELS[sentenceLang]} →{" "}
                      {TRANSLATION_LANGUAGE_LABELS[translationLang]} ·{" "}
                      {DIFFICULTY_LABELS[difficulty]}
                    </Typography>
                    <Button
                      variant="contained"
                      size="large"
                      fullWidth
                      onClick={handleGenerateDeck}
                      disabled={parsedWords.length === 0 || isSubmitting}
                    >
                      {isSubmitting ? (
                        <CircularProgress size={20} color="inherit" />
                      ) : (
                        "Generate Deck"
                      )}
                    </Button>
                  </Stack>
                </Paper>
              </Stack>
            </Box>
          )}

          {viewState === "PROCESSING" && (
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: {
                  xs: "1fr",
                  lg: "minmax(0, 0.9fr) minmax(340px, 1.1fr)",
                },
                gap: 3,
                alignItems: "start",
              }}
            >
              <Paper sx={{ p: { xs: 2.5, md: 4 } }}>
                <Stack spacing={3}>
                  <Stack
                    direction="row"
                    justifyContent="space-between"
                    alignItems="center"
                  >
                    <Typography
                      variant="h6"
                      sx={{
                        color: taskStatus
                          ? TASK_STATUS_COLORS[taskStatus]
                          : undefined,
                      }}
                    >
                      {taskStatus
                        ? TASK_STATUS_LABELS[taskStatus]
                        : "Queued"}
                    </Typography>
                    {hasStartedProcessing && (
                      <CircularProgress size={20} color="inherit" />
                    )}
                  </Stack>

                  <Typography
                    variant="h1"
                    sx={{ fontSize: { xs: "3.5rem", md: "5rem" }, lineHeight: 1 }}
                  >
                    {roundedProgress}
                    <Box
                      component="span"
                      sx={{
                        color: "primary.main",
                        fontSize: "0.5em",
                      }}
                    >
                      %
                    </Box>
                  </Typography>

                  <LinearProgress
                    variant="determinate"
                    value={processingProgress}
                  />

                  <Box
                    sx={{
                      display: "grid",
                      gridTemplateColumns: {
                        xs: "repeat(2, minmax(0, 1fr))",
                        sm: "repeat(4, minmax(0, 1fr))",
                      },
                      gap: 1.5,
                    }}
                  >
                    <CountTile
                      label="Done"
                      value={doneItems}
                      color="#10b981"
                    />
                    <CountTile
                      label="Running"
                      value={processingItems}
                      color="#2563eb"
                    />
                    <CountTile
                      label="Queued"
                      value={pendingItems}
                      color="#94a3b8"
                    />
                    <CountTile
                      label="Failed"
                      value={errorItems}
                      color="#e11d48"
                    />
                  </Box>
                </Stack>
              </Paper>

              <Paper sx={{ p: { xs: 2.5, md: 3 } }}>
                <Stack spacing={2}>
                  <Stack
                    direction="row"
                    justifyContent="space-between"
                    alignItems="center"
                  >
                    <Stack direction="row" spacing={1.5} alignItems="center">
                      <Box
                        sx={{
                          width: 10,
                          height: 10,
                          borderRadius: "50%",
                          backgroundColor: "info.main",
                        }}
                      />
                      <Typography variant="h6">Queue</Typography>
                    </Stack>
                    <Typography
                      className="mono"
                      variant="body2"
                      sx={{ color: "text.secondary" }}
                    >
                      {doneItems}/{totalItems} done
                    </Typography>
                  </Stack>
                  <Stack
                    spacing={1}
                    sx={{
                      maxHeight: { xs: "none", xl: 520 },
                      overflowY: "auto",
                      pr: 0.5,
                    }}
                  >
                    {items.map((item, index) => (
                      <WordStatusCard
                        key={`${item.raw_word}-${index}`}
                        item={item}
                      />
                    ))}
                  </Stack>
                </Stack>
              </Paper>
            </Box>
          )}

          {viewState === "DONE" && (
            <>
              <Paper
                sx={{
                  p: { xs: 3, md: 4 },
                  textAlign: "center",
                  backgroundColor: alpha("#10b981", 0.03),
                  borderColor: alpha("#10b981", 0.22),
                }}
              >
                <Stack spacing={2} alignItems="center">
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      borderRadius: "50%",
                      backgroundColor: "success.main",
                      color: "#ffffff",
                      display: "grid",
                      placeItems: "center",
                    }}
                  >
                    <DownloadIcon />
                  </Box>
                  <Typography variant="h4">Deck ready</Typography>
                  <Typography variant="body1" sx={{ color: "text.secondary" }}>
                    {successfulCards} cards generated
                    {isPartiallyDone && " · some words failed"}.
                  </Typography>
                  {isPartiallyDone && (
                    <Alert severity="warning">
                      Some words failed during processing.
                    </Alert>
                  )}
                  <Stack
                    direction={{ xs: "column", sm: "row" }}
                    spacing={1.5}
                    sx={{ mt: 2 }}
                  >
                    <Button
                      variant="contained"
                      size="large"
                      onClick={handleDownloadDeck}
                      disabled={isDownloading || !taskId}
                    >
                      {isDownloading ? (
                        <CircularProgress size={20} color="inherit" />
                      ) : (
                        "Download .apkg"
                      )}
                    </Button>
                    <Button
                      variant="outlined"
                      size="large"
                      onClick={handleCreateAnother}
                    >
                      Create another
                    </Button>
                  </Stack>
                </Stack>
              </Paper>

              <Paper sx={{ p: { xs: 2.5, md: 3 } }}>
                <Stack spacing={2}>
                  <Stack
                    direction="row"
                    justifyContent="space-between"
                    alignItems="center"
                  >
                    <Stack direction="row" spacing={1.5} alignItems="center">
                      <Box
                        sx={{
                          width: 10,
                          height: 10,
                          borderRadius: "50%",
                          backgroundColor: "success.main",
                        }}
                      />
                      <Typography variant="h6">Words</Typography>
                    </Stack>
                    <Typography
                      variant="body2"
                      sx={{ color: "text.secondary" }}
                    >
                      {doneItems} done · {errorItems} failed
                    </Typography>
                  </Stack>
                  <Stack
                    spacing={1}
                    sx={{ maxHeight: 440, overflowY: "auto", pr: 0.5 }}
                  >
                    {items.map((item, index) => (
                      <WordStatusCard
                        key={`${item.raw_word}-${index}`}
                        item={item}
                      />
                    ))}
                  </Stack>
                </Stack>
              </Paper>
            </>
          )}

          {taskHistory.length > 0 && (
            <Paper sx={{ p: { xs: 2.5, md: 3 } }}>
              <Stack spacing={2}>
                <Stack direction="row" spacing={1.5} alignItems="center">
                  <Box
                    sx={{
                      width: 10,
                      height: 10,
                      borderRadius: "50%",
                      backgroundColor: "warning.main",
                    }}
                  />
                  <Typography variant="h6">Previous decks</Typography>
                </Stack>
                <Stack spacing={0}>
                  {taskHistory.map((task) => (
                    <Stack
                      key={task.id}
                      direction="row"
                      spacing={2}
                      alignItems="center"
                      justifyContent="space-between"
                      sx={{
                        py: 1.25,
                        borderBottom: "1px solid",
                        borderColor: "divider",
                        "&:last-of-type": { borderBottom: "none" },
                      }}
                    >
                      <Stack direction="row" spacing={2} alignItems="center">
                        <Typography className="mono" variant="body2">
                          #{task.id.slice(0, 8)}
                        </Typography>
                        <Typography
                          variant="body2"
                          sx={{ color: "text.secondary" }}
                        >
                          {task.total_items} words
                        </Typography>
                      </Stack>
                      <Stack direction="row" spacing={1.5} alignItems="center">
                        <Typography
                          variant="body2"
                          sx={{
                            color: TASK_STATUS_COLORS[task.status],
                            fontWeight: 600,
                          }}
                        >
                          {TASK_STATUS_LABELS[task.status]}
                        </Typography>
                        {(task.status === "DONE" ||
                          task.status === "PARTIALLY_DONE") && (
                          <Button
                            variant="outlined"
                            size="small"
                            onClick={() => handleHistoryDownload(task.id)}
                          >
                            Download
                          </Button>
                        )}
                      </Stack>
                    </Stack>
                  ))}
                </Stack>
              </Stack>
            </Paper>
          )}
        </Stack>
      </Container>
    </Box>
  );
}

export default AppPage;
