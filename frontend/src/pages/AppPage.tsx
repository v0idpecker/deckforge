import { type ReactNode, useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Container,
  FormControlLabel,
  FormControl,
  InputLabel,
  LinearProgress,
  List,
  ListItem,
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
} from "../types/decks";

type ViewState = "INPUT" | "PROCESSING" | "DONE";

const TERMINAL_TASK_STATUSES = new Set<DeckTaskStatusValue>([
  "DONE",
  "PARTIALLY_DONE",
]);

const STAGE_LABELS: Record<Exclude<DeckItemStageValue, null>, string> = {
  INIT: "Starting...",
  NORMILIZED: "Normalized",
  CONTEXT_GENERATED: "Context ready",
  DONE: "Done",
};

const HISTORY_STATUS_STYLES: Record<
  DeckTaskStatusValue,
  { label: string; background: string; color: string }
> = {
  PENDING: { label: "Pending", background: "#F0F0F0", color: "#888" },
  PROCESSING: {
    label: "Processing...",
    background: "#EBF5EE",
    color: "#2D6A4F",
  },
  DONE: { label: "Done", background: "#EBF5EE", color: "#2D6A4F" },
  PARTIALLY_DONE: { label: "Partial", background: "#FEF9EC", color: "#92610A" },
};

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

function getItemStatusColor(status: DeckItemStatusValue): string {
  if (status === "DONE") {
    return "#2D6A4F";
  }

  if (status === "ERROR") {
    return "#C0392B";
  }

  if (status === "PROCESSING") {
    return "#2D6A4F";
  }

  return "#7A8A80";
}

function StatusMarker({ status }: { status: DeckItemStatusValue }) {
  return (
    <Box
      sx={{
        width: 8,
        height: 8,
        borderRadius: "50%",
        backgroundColor: getItemStatusColor(status),
        flexShrink: 0,
      }}
    />
  );
}

function getRowLabel(item: DeckTaskItemStatus): string {
  if (item.status === "PROCESSING") {
    return getProcessingSubtitle(item.stage);
  }

  if (item.status === "DONE") {
    return "Done";
  }

  if (item.status === "ERROR") {
    return "Failed";
  }

  return "Pending";
}

function DecorativeIcon({ children }: { children: ReactNode }) {
  return (
    <Box
      sx={{
        width: 44,
        height: 44,
        color: "#2D6A4F",
        opacity: 0.8,
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {children}
    </Box>
  );
}

function AppPage() {
  const [hasToken, setHasToken] = useState(false);
  const [viewState, setViewState] = useState<ViewState>("INPUT");
  const [wordsInput, setWordsInput] = useState("");

  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskStatus, setTaskStatus] = useState<DeckTaskStatusValue | null>(
    null,
  );
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

        const message =
          cause instanceof Error ? cause.message : "Unknown error";
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
  const successfulCards =
    items.length > 0
      ? doneItems
      : taskStatus === "DONE"
        ? submittedWords.length
        : doneItems;
  const processingProgress =
    totalItems > 0 ? (doneItems / totalItems) * 100 : 0;
  const hasStartedProcessing =
    taskStatus === "PROCESSING" ||
    items.some((item) => item.status !== "PENDING");
  const cardSx = {
    width: "100%",
    maxWidth: 480,
    mx: "auto",
    p: { xs: 2.5, sm: 3.5 },
  };

  if (!hasToken) {
    return null;
  }

  return (
    <Container maxWidth="md" sx={{ py: { xs: 3, sm: 6 } }}>
      <Stack spacing={3.5}>
        <Box
          sx={{
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            gap: 2,
            flexWrap: "wrap",
          }}
        >
          <Box>
            <Typography
              variant="overline"
              sx={{ color: "text.secondary", letterSpacing: "0.08em" }}
            >
              DeckForge
            </Typography>
            <Typography variant="h4" component="h1" sx={{ mt: 0.5 }}>
              Anki deck builder
            </Typography>
            <Typography
              variant="body1"
              color="text.secondary"
              sx={{ mt: 1.5, maxWidth: 620 }}
            >
              Paste a list of words, track processing progress, and download
              your generated deck.
            </Typography>
          </Box>
          {hasToken && (
            <Button
              variant="text"
              size="small"
              onClick={handleSignOut}
              sx={{
                textTransform: "none",
                color: "text.secondary",
                mt: 0.5,
                px: 0.5,
                "&:hover": {
                  backgroundColor: "transparent",
                  color: "text.primary",
                },
              }}
            >
              Sign out
            </Button>
          )}
        </Box>

        {error && (
          <Alert
            severity="error"
            sx={{
              backgroundColor: "#FDECEA",
              color: "#1A1F1C",
              border: "1px solid #F3D8D4",
            }}
          >
            {error}
          </Alert>
        )}

        {viewState === "INPUT" && (
          <>
            <Paper sx={cardSx}>
              <Stack spacing={2.5}>
                <DecorativeIcon>
                  <SvgIcon sx={{ fontSize: 44 }} viewBox="0 0 24 24">
                    <path d="M21 4c0-1.1-.9-2-2-2H9C7.9 2 7 2.9 7 4v14c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V4zm-2 14H9V4h10v14zM5 6H3v16c0 1.1.9 2 2 2h12v-2H5V6z" />
                  </SvgIcon>
                </DecorativeIcon>
                <TextField
                  label="Words"
                  placeholder="apple\nrun\nlearn"
                  multiline
                  minRows={3}
                  maxRows={8}
                  fullWidth
                  value={wordsInput}
                  onChange={(event) => setWordsInput(event.target.value)}
                  InputProps={{
                    sx: {
                      fontFamily: '"DM Mono", ui-monospace, monospace',
                      fontSize: 14,
                      lineHeight: 1.7,
                    },
                  }}
                />

                <Box>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{
                      mb: 1,
                      fontFamily: '"DM Mono", ui-monospace, monospace',
                    }}
                  >
                    Parsed words ({parsedWords.length})
                  </Typography>
                  {parsedWords.length === 0 ? (
                    <Typography variant="body2" color="text.secondary">
                      No words yet.
                    </Typography>
                  ) : (
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
                </Box>

                <Box
                  sx={{
                    borderTop: "1px solid var(--border)",
                    pt: 2,
                  }}
                >
                  <Stack spacing={2}>
                    <Box>
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
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ ml: 4.5, mt: 0.5 }}
                      >
                        Lemmatizes each word before processing (e.g. {"running"}{" "}
                        {"\u2192"} {"run"}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography
                        variant="body2"
                        sx={{ fontWeight: 600, mb: 1 }}
                      >
                        Cards per word: {cardsPerWord}
                      </Typography>
                      <Slider
                        min={1}
                        max={5}
                        step={1}
                        value={cardsPerWord}
                        onChange={(_, value) =>
                          setCardsPerWord(value as number)
                        }
                      />
                    </Box>
                    <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
                      <FormControl fullWidth size="small">
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
                          <MenuItem value="english">English</MenuItem>
                          <MenuItem value="german">German</MenuItem>
                          <MenuItem value="spanish">Spanish</MenuItem>
                          <MenuItem value="french">French</MenuItem>
                          <MenuItem value="italian">Italian</MenuItem>
                        </Select>
                      </FormControl>
                      <FormControl fullWidth size="small">
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
                          <MenuItem value="russian">Russian</MenuItem>
                          <MenuItem value="english">English</MenuItem>
                          <MenuItem value="german">German</MenuItem>
                          <MenuItem value="spanish">Spanish</MenuItem>
                          <MenuItem value="french">French</MenuItem>
                        </Select>
                      </FormControl>
                    </Stack>
                  </Stack>
                </Box>

                <Box>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={handleGenerateDeck}
                    disabled={parsedWords.length === 0 || isSubmitting}
                  >
                    {isSubmitting ? (
                      <CircularProgress size={18} color="inherit" />
                    ) : (
                      "Generate Deck"
                    )}
                  </Button>
                </Box>
              </Stack>
            </Paper>

            {taskHistory.length > 0 && (
              <Box>
                <Typography
                  variant="overline"
                  sx={{
                    color: "text.secondary",
                    letterSpacing: "0.08em",
                    fontFamily: '"DM Mono", ui-monospace, monospace',
                  }}
                >
                  My Decks
                </Typography>
                <Stack spacing={0.5} sx={{ mt: 1 }}>
                  {taskHistory.map((task) => {
                    const statusStyle = HISTORY_STATUS_STYLES[task.status] ?? {
                      label: task.status,
                      background: "#F0F0F0",
                      color: "#888",
                    };
                    const canDownload =
                      task.status === "DONE" ||
                      task.status === "PARTIALLY_DONE";

                    return (
                      <Box
                        key={task.id}
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 2,
                          px: 1.5,
                          py: 1,
                          borderRadius: 2,
                          transition: "background-color 0.2s ease",
                          "&:hover": {
                            backgroundColor: "var(--accent-light)",
                          },
                        }}
                      >
                        <Typography variant="body2" color="text.secondary">
                          {task.total_items} words
                        </Typography>
                        <Box
                          sx={{
                            ml: "auto",
                            display: "flex",
                            alignItems: "center",
                            gap: 1.5,
                          }}
                        >
                          <Box
                            sx={{
                              px: 1.1,
                              py: 0.35,
                              borderRadius: 999,
                              backgroundColor: statusStyle.background,
                              color: statusStyle.color,
                              fontSize: 12,
                              fontWeight: 500,
                              whiteSpace: "nowrap",
                            }}
                          >
                            {statusStyle.label}
                          </Box>
                          {canDownload && (
                            <Button
                              variant="text"
                              size="small"
                              onClick={() => handleHistoryDownload(task.id)}
                              sx={{
                                textTransform: "none",
                                color: "text.secondary",
                                px: 0.5,
                                "&:hover": {
                                  backgroundColor: "transparent",
                                  color: "text.primary",
                                },
                              }}
                            >
                              Download
                            </Button>
                          )}
                        </Box>
                      </Box>
                    );
                  })}
                </Stack>
              </Box>
            )}
          </>
        )}

        {viewState === "PROCESSING" && (
          <Paper sx={cardSx}>
            <Stack spacing={2.5}>
              <DecorativeIcon>
                {hasStartedProcessing ? (
                  <CircularProgress size={24} sx={{ color: "#2D6A4F" }} />
                ) : (
                  <SvgIcon sx={{ fontSize: 44 }} viewBox="0 0 24 24">
                    <path d="M11 21h-1l1-7H7.5a.5.5 0 0 1-.41-.79L13 4h1l-1 7h3.5a.5.5 0 0 1 .41.79L11 21z" />
                  </SvgIcon>
                )}
              </DecorativeIcon>
              <Typography variant="h6">Processing your words...</Typography>

              <Box>
                <LinearProgress
                  variant="determinate"
                  value={processingProgress}
                  sx={{
                    height: 8,
                    borderRadius: 999,
                    backgroundColor: "#E8EAE4",
                    "& .MuiLinearProgress-bar": {
                      backgroundColor: "#2D6A4F",
                      transition: "transform 0.25s ease",
                    },
                  }}
                />
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mt: 0.75 }}
                >
                  {doneItems}/{totalItems}
                </Typography>
              </Box>

              <List disablePadding>
                {items.map((item, index) => (
                  <ListItem
                    key={`${item.raw_word}-${index}`}
                    disableGutters
                    sx={{
                      py: 1,
                      px: 1.25,
                      borderRadius: 2,
                      mb: 0.5,
                      transition: "background-color 0.2s ease",
                      "&:hover": {
                        backgroundColor: "#EBF5EE",
                      },
                    }}
                  >
                    <Stack direction="row" spacing={1.25} alignItems="center">
                      <StatusMarker status={item.status} />
                      <Typography
                        sx={{
                          fontFamily: '"DM Mono", ui-monospace, monospace',
                          fontSize: 14,
                        }}
                      >
                        {item.raw_word}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                          fontFamily: '"DM Mono", ui-monospace, monospace',
                          fontSize: 12,
                        }}
                      >
                        {getRowLabel(item)}
                      </Typography>
                    </Stack>
                  </ListItem>
                ))}
              </List>
            </Stack>
          </Paper>
        )}

        {viewState === "DONE" && (
          <Paper sx={cardSx}>
            <Stack spacing={0}>
              <DecorativeIcon>
                <SvgIcon sx={{ fontSize: 44 }} viewBox="0 0 24 24">
                  <path d="M20 6h-3V4c0-1.1-.9-2-2-2H4C2.9 2 2 2.9 2 4v13c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2v-2h3c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-5 11H4V4h11v13zm6-4h-4V8h3c.55 0 1 .45 1 1v4zm-9.29-1.29-2.42-2.42-1.41 1.41L11 14.83l4.12-4.12-1.41-1.41z" />
                </SvgIcon>
              </DecorativeIcon>
              <Typography component="h2" variant="h6" sx={{ mt: 2.5 }}>
                Your deck is ready
              </Typography>

              <Typography
                sx={{
                  fontSize: 14,
                  color: "text.secondary",
                  mb: 2.5,
                }}
              >
                {successfulCards} cards ready to import
              </Typography>

              {isPartiallyDone && (
                <Alert
                  severity="warning"
                  sx={{
                    alignSelf: "flex-start",
                    width: "fit-content",
                    maxWidth: "100%",
                    backgroundColor: "#FFF7E8",
                    border: "1px solid #F1E4C2",
                    color: "#1A1F1C",
                    mb: 2.5,
                  }}
                >
                  Deck is ready, but some words failed during processing.
                </Alert>
              )}

              <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5}>
                <Button
                  variant="contained"
                  size="large"
                  onClick={handleDownloadDeck}
                  disabled={isDownloading || !taskId}
                >
                  {isDownloading ? (
                    <CircularProgress size={18} color="inherit" />
                  ) : (
                    "Download Deck"
                  )}
                </Button>
                <Button
                  variant="text"
                  size="large"
                  onClick={handleCreateAnother}
                  sx={{
                    color: "text.secondary",
                    fontWeight: 400,
                    px: 0,
                    "&:hover": {
                      backgroundColor: "transparent",
                      color: "text.primary",
                    },
                  }}
                >
                  Create another
                </Button>
              </Stack>
            </Stack>
          </Paper>
        )}
      </Stack>
    </Container>
  );
}

export default AppPage;
