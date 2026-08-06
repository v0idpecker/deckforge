import { type ReactNode, useEffect, useMemo, useState } from "react";
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

const HISTORY_STATUS_STYLES: Record<
  DeckTaskStatusValue,
  { label: string; background: string; color: string }
> = {
  PENDING: {
    label: "Pending",
    background: alpha("#171312", 0.06),
    color: "#5f5347",
  },
  PROCESSING: {
    label: "Processing",
    background: alpha("#2358ff", 0.12),
    color: "#1739ad",
  },
  DONE: {
    label: "Done",
    background: alpha("#2d8f5c", 0.14),
    color: "#1d673f",
  },
  PARTIALLY_DONE: {
    label: "Partial",
    background: alpha("#f4c94f", 0.32),
    color: "#8d5f00",
  },
};

const TASK_STATUS_META: Record<
  DeckTaskStatusValue,
  { label: string; description: string; accent: string }
> = {
  PENDING: {
    label: "Queued",
    description: "The request exists, but work has not started yet.",
    accent: "#f4c94f",
  },
  PROCESSING: {
    label: "Active",
    description: "DeckForge is building contexts and translations right now.",
    accent: "#2358ff",
  },
  DONE: {
    label: "Ready",
    description: "The package is complete and ready for download.",
    accent: "#2d8f5c",
  },
  PARTIALLY_DONE: {
    label: "Ready With Gaps",
    description: "The package is ready, but some words did not finish cleanly.",
    accent: "#f4c94f",
  },
};

const ITEM_STATUS_META: Record<
  DeckItemStatusValue,
  { label: string; accent: string; background: string }
> = {
  PENDING: {
    label: "Pending",
    accent: "#5f5347",
    background: alpha("#171312", 0.06),
  },
  PROCESSING: {
    label: "Processing",
    accent: "#1739ad",
    background: alpha("#2358ff", 0.1),
  },
  DONE: {
    label: "Done",
    accent: "#1d673f",
    background: alpha("#2d8f5c", 0.12),
  },
  ERROR: {
    label: "Failed",
    accent: "#9f2e1f",
    background: alpha("#d6452f", 0.12),
  },
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

  return ITEM_STATUS_META[item.status].label;
}

function SectionStamp({
  children,
  accent = "text.secondary",
}: {
  children: ReactNode;
  accent?: string;
}) {
  return (
    <Typography variant="overline" sx={{ color: accent }}>
      {children}
    </Typography>
  );
}

function GlyphBadge({
  children,
  accent = "var(--signal-yellow)",
}: {
  children: ReactNode;
  accent?: string;
}) {
  return (
    <Paper
      sx={{
        width: 68,
        height: 68,
        borderRadius: "50%",
        display: "grid",
        placeItems: "center",
        backgroundColor: accent,
        flexShrink: 0,
      }}
    >
      {children}
    </Paper>
  );
}

function MetricTile({
  label,
  value,
  detail,
  accent,
}: {
  label: string;
  value: string;
  detail?: string;
  accent: string;
}) {
  return (
    <Paper
      sx={{
        p: 2,
        borderRadius: 4,
        minHeight: 132,
        backgroundColor: alpha("#ffffff", 0.58),
      }}
    >
      <SectionStamp accent="text.secondary">{label}</SectionStamp>
      <Typography
        variant="h4"
        sx={{
          mt: 1.25,
          color: accent,
          fontSize: { xs: "2rem", md: "2.5rem" },
        }}
      >
        {value}
      </Typography>
      {detail && (
        <Typography variant="body2" sx={{ mt: 0.75, color: "text.secondary" }}>
          {detail}
        </Typography>
      )}
    </Paper>
  );
}

function StatusPill({
  label,
  background,
  color,
}: {
  label: string;
  background: string;
  color: string;
}) {
  return (
    <Box
      className="mono"
      sx={{
        px: 1.2,
        py: 0.7,
        borderRadius: 999,
        border: "1.5px solid rgba(23, 19, 18, 0.85)",
        backgroundColor: background,
        color,
        fontSize: 12,
        display: "inline-flex",
        alignItems: "center",
      }}
    >
      {label}
    </Box>
  );
}

function ForgeIcon() {
  return (
    <SvgIcon viewBox="0 0 24 24" sx={{ fontSize: 28 }}>
      <path d="M13 2l-1.7 6H7.5a.5.5 0 0 0-.41.79l3.77 5.39L9 22l7.91-11.21A.5.5 0 0 0 16.5 10h-3.8L14 2h-1z" />
    </SvgIcon>
  );
}

function StackIcon() {
  return (
    <SvgIcon viewBox="0 0 24 24" sx={{ fontSize: 24 }}>
      <path d="M12 2L1 8l11 6 9-4.91V17h2V8L12 2zm0 14L4.74 12 3 12.95 12 18l9-5.05L19.26 12 12 16zm0 4L4.74 16 3 16.95 12 22l9-5.05L19.26 16 12 20z" />
    </SvgIcon>
  );
}

function DownloadIcon() {
  return (
    <SvgIcon viewBox="0 0 24 24" sx={{ fontSize: 24 }}>
      <path d="M5 20h14v-2H5v2zM11 4v8.17L8.41 9.59 7 11l5 5 5-5-1.41-1.41L13 12.17V4h-2z" />
    </SvgIcon>
  );
}

function WordStatusCard({ item }: { item: DeckTaskItemStatus }) {
  const meta = ITEM_STATUS_META[item.status];

  return (
    <Paper
      sx={{
        p: 1.6,
        borderRadius: 4,
        backgroundColor: alpha("#ffffff", 0.56),
      }}
    >
      <Stack direction="row" spacing={1.25} alignItems="flex-start">
        <Box
          sx={{
            width: 12,
            height: 12,
            borderRadius: "50%",
            backgroundColor: meta.accent,
            mt: "6px",
            flexShrink: 0,
          }}
        />
        <Box sx={{ minWidth: 0, flex: 1 }}>
          <Stack
            direction={{ xs: "column", sm: "row" }}
            spacing={1}
            justifyContent="space-between"
            alignItems={{ xs: "flex-start", sm: "center" }}
          >
            <Typography
              className="mono"
              sx={{
                fontSize: 13,
                wordBreak: "break-word",
              }}
            >
              {item.raw_word}
            </Typography>
            <StatusPill
              label={getRowLabel(item)}
              background={meta.background}
              color={meta.accent}
            />
          </Stack>
        </Box>
      </Stack>
    </Paper>
  );
}

function ArchiveCard({
  task,
  onDownload,
}: {
  task: DeckTaskHistoryItem;
  onDownload: (deckId: string) => void;
}) {
  const statusStyle = HISTORY_STATUS_STYLES[task.status] ?? {
    label: task.status,
    background: alpha("#171312", 0.06),
    color: "#5f5347",
  };
  const canDownload =
    task.status === "DONE" || task.status === "PARTIALLY_DONE";

  return (
    <Paper
      sx={{
        p: 2,
        borderRadius: 4,
        backgroundColor: alpha("#ffffff", 0.56),
        display: "flex",
        flexDirection: "column",
        gap: 1.5,
      }}
    >
      <Stack direction="row" spacing={1} justifyContent="space-between">
        <SectionStamp accent="text.secondary">Deck #{task.id.slice(0, 8)}</SectionStamp>
        <StatusPill
          label={statusStyle.label}
          background={statusStyle.background}
          color={statusStyle.color}
        />
      </Stack>
      <Typography variant="h6">{task.total_items} source words</Typography>
      <Typography variant="body2" sx={{ color: "text.secondary" }}>
        Stored in your archive and available for download when processing
        finishes.
      </Typography>
      {canDownload ? (
        <Button
          variant="outlined"
          size="small"
          onClick={() => onDownload(task.id)}
          sx={{ alignSelf: "flex-start" }}
        >
          Download
        </Button>
      ) : (
        <Typography className="mono" sx={{ fontSize: 12, color: "text.secondary" }}>
          download unavailable until completion
        </Typography>
      )}
    </Paper>
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
  const currentStatusMeta = taskStatus ? TASK_STATUS_META[taskStatus] : null;
  const activeWordCount =
    viewState === "INPUT" ? parsedWords.length : submittedWords.length;

  if (!hasToken) {
    return null;
  }

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
          top: { xs: -50, md: 20 },
          right: { xs: -60, md: 120 },
          width: { xs: 180, md: 260 },
          height: { xs: 180, md: 260 },
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(255, 107, 44, 0.28), rgba(255, 107, 44, 0))",
          pointerEvents: "none",
        }}
      />
      <Box
        className="float-slower"
        sx={{
          position: "absolute",
          left: { xs: -70, md: 60 },
          bottom: { xs: 160, md: 40 },
          width: { xs: 220, md: 300 },
          height: { xs: 220, md: 300 },
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(35, 88, 255, 0.22), rgba(35, 88, 255, 0))",
          pointerEvents: "none",
        }}
      />

      <Container maxWidth="xl" sx={{ position: "relative", zIndex: 1 }}>
        <Stack spacing={3}>
          <Paper
            className="poster-surface panel-reveal"
            sx={{
              p: { xs: 2.5, md: 3 },
              borderRadius: { xs: 6, md: 8 },
              background:
                "linear-gradient(145deg, rgba(255,255,255,0.82), rgba(255,247,234,0.94))",
            }}
          >
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: { xs: "1fr", xl: "minmax(0, 1.15fr) minmax(320px, 0.85fr)" },
                gap: 2.5,
                alignItems: "start",
              }}
            >
              <Stack spacing={2.5}>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 2,
                    flexWrap: "wrap",
                    alignItems: "center",
                  }}
                >
                  <Stack direction="row" spacing={1.5} alignItems="center">
                    <GlyphBadge>
                      <ForgeIcon />
                    </GlyphBadge>
                    <Box>
                      <SectionStamp>DeckForge Studio</SectionStamp>
                      <Typography variant="h4" sx={{ mt: 0.35 }}>
                        Word-to-deck workshop
                      </Typography>
                    </Box>
                  </Stack>

                  <Button variant="text" size="small" onClick={handleSignOut}>
                    Sign out
                  </Button>
                </Box>

                <Box>
                  <Typography
                    variant="h2"
                    sx={{
                      fontSize: { xs: "2.8rem", md: "4.8rem" },
                      maxWidth: 860,
                    }}
                  >
                    Same pipeline. Completely rebuilt{" "}
                    <Box component="span" sx={{ color: "primary.main" }}>
                      visual shell.
                    </Box>
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{
                      mt: 1.5,
                      maxWidth: 720,
                      color: "text.secondary",
                      fontSize: { xs: 15, md: 17 },
                    }}
                  >
                    Paste source words, shape generation options, watch the live
                    queue, and pull down the resulting Anki package when the forge
                    finishes.
                  </Typography>
                </Box>
              </Stack>

              <Box
                sx={{
                  display: "grid",
                  gridTemplateColumns: { xs: "repeat(2, minmax(0, 1fr))", sm: "repeat(4, minmax(0, 1fr))", xl: "repeat(2, minmax(0, 1fr))" },
                  gap: 1.5,
                }}
              >
                <MetricTile
                  label="Mode"
                  value={
                    viewState === "INPUT"
                      ? "Draft"
                      : viewState === "PROCESSING"
                        ? "Forge"
                        : "Ready"
                  }
                  detail="Current screen state"
                  accent="var(--signal-blue)"
                />
                <MetricTile
                  label="Word Count"
                  value={String(activeWordCount)}
                  detail="Active list size"
                  accent="var(--signal)"
                />
                <MetricTile
                  label="Archive"
                  value={String(taskHistory.length)}
                  detail="Saved deck tasks"
                  accent="var(--signal-green)"
                />
                <MetricTile
                  label="Output"
                  value={`${cardsPerWord}x`}
                  detail={`${SENTENCE_LANGUAGE_LABELS[sentenceLang]} examples`}
                  accent="var(--signal-yellow)"
                />
              </Box>
            </Box>
          </Paper>

          {error && (
            <Alert
              severity="error"
              sx={{
                backgroundColor: alpha("#f7ddd7", 0.9),
              }}
            >
              {error}
            </Alert>
          )}

          {viewState === "INPUT" && (
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: { xs: "1fr", xl: "minmax(0, 1.1fr) minmax(340px, 0.9fr)" },
                gap: 3,
              }}
            >
              <Paper
                className="poster-surface panel-reveal"
                sx={{
                  p: { xs: 2.5, md: 3.5 },
                  borderRadius: { xs: 6, md: 8 },
                  background:
                    "linear-gradient(180deg, rgba(255,255,255,0.76), rgba(255, 107, 44, 0.08))",
                }}
              >
                <Stack spacing={2.5}>
                  <Stack
                    direction={{ xs: "column", sm: "row" }}
                    spacing={2}
                    justifyContent="space-between"
                    alignItems={{ xs: "flex-start", sm: "center" }}
                  >
                    <Box>
                      <SectionStamp>Input Deck Manifest</SectionStamp>
                      <Typography variant="h4" sx={{ mt: 0.45 }}>
                        Feed the wordlist
                      </Typography>
                    </Box>
                    <StatusPill
                      label={`${parsedWords.length} parsed`}
                      background={alpha("#ff6b2c", 0.14)}
                      color="#b64b17"
                    />
                  </Stack>

                  <TextField
                    label="Source words"
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

                  <Paper
                    sx={{
                      p: 2,
                      borderRadius: 4,
                      backgroundColor: alpha("#ffffff", 0.56),
                    }}
                  >
                    <Stack
                      direction={{ xs: "column", md: "row" }}
                      spacing={1.5}
                      justifyContent="space-between"
                      alignItems={{ xs: "flex-start", md: "center" }}
                    >
                      <Box>
                        <SectionStamp accent="text.secondary">Parsed Inventory</SectionStamp>
                        <Typography variant="body2" sx={{ mt: 0.5, color: "text.secondary" }}>
                          Duplicates are removed before submission. Click a chip to
                          remove it from the draft.
                        </Typography>
                      </Box>
                      <Typography className="mono" sx={{ fontSize: 12, color: "text.secondary" }}>
                        separators: newline / comma
                      </Typography>
                    </Stack>

                    {parsedWords.length === 0 ? (
                      <Typography variant="body2" sx={{ mt: 2, color: "text.secondary" }}>
                        No words parsed yet. Paste anything rough; cleanup happens here.
                      </Typography>
                    ) : (
                      <Stack
                        direction="row"
                        spacing={1}
                        useFlexGap
                        flexWrap="wrap"
                        sx={{ mt: 2 }}
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
                  </Paper>
                </Stack>
              </Paper>

              <Stack spacing={3}>
                <Paper
                  className="poster-surface panel-reveal"
                  sx={{
                    p: { xs: 2.5, md: 3 },
                    borderRadius: { xs: 6, md: 8 },
                    background:
                      "linear-gradient(180deg, rgba(255,255,255,0.8), rgba(35, 88, 255, 0.08))",
                  }}
                >
                  <Stack spacing={2.5}>
                    <Stack direction="row" spacing={1.5} alignItems="center">
                      <GlyphBadge accent="var(--signal-blue)">
                        <StackIcon />
                      </GlyphBadge>
                      <Box>
                        <SectionStamp>Generation Controls</SectionStamp>
                        <Typography variant="h5" sx={{ mt: 0.4 }}>
                          Shape the deck
                        </Typography>
                      </Box>
                    </Stack>

                    <Paper
                      sx={{
                        p: 2,
                        borderRadius: 4,
                        backgroundColor: alpha("#ffffff", 0.54),
                      }}
                    >
                      <FormControlLabel
                        control={
                          <Switch
                            checked={normalizationEnabled}
                            onChange={(event) =>
                              setNormalizationEnabled(event.target.checked)
                            }
                          />
                        }
                        label="Normalize words before lookup"
                      />
                      <Typography
                        variant="body2"
                        sx={{ mt: 0.75, ml: { xs: 0, sm: 5.5 }, color: "text.secondary" }}
                      >
                        Useful for inflected forms such as “running” to “run”.
                      </Typography>
                    </Paper>

                    <Paper
                      sx={{
                        p: 2,
                        borderRadius: 4,
                        backgroundColor: alpha("#ffffff", 0.54),
                      }}
                    >
                      <Stack direction="row" justifyContent="space-between" spacing={1}>
                        <SectionStamp accent="text.secondary">Cards Per Word</SectionStamp>
                        <Typography className="mono" sx={{ fontSize: 12 }}>
                          {cardsPerWord}
                        </Typography>
                      </Stack>
                      <Slider
                        min={1}
                        max={5}
                        step={1}
                        value={cardsPerWord}
                        onChange={(_, value) => setCardsPerWord(value as number)}
                        sx={{ mt: 1.75 }}
                      />
                    </Paper>

                    <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
                      <FormControl fullWidth>
                        <InputLabel id="sentence-lang-label">Example language</InputLabel>
                        <Select
                          labelId="sentence-lang-label"
                          label="Example language"
                          value={sentenceLang}
                          onChange={(event) =>
                            setSentenceLang(event.target.value as typeof sentenceLang)
                          }
                        >
                          <MenuItem value="english">English</MenuItem>
                          <MenuItem value="german">German</MenuItem>
                          <MenuItem value="spanish">Spanish</MenuItem>
                          <MenuItem value="french">French</MenuItem>
                          <MenuItem value="italian">Italian</MenuItem>
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
                          <MenuItem value="russian">Russian</MenuItem>
                          <MenuItem value="english">English</MenuItem>
                          <MenuItem value="german">German</MenuItem>
                          <MenuItem value="spanish">Spanish</MenuItem>
                          <MenuItem value="french">French</MenuItem>
                        </Select>
                      </FormControl>
                    </Stack>

                    <FormControl fullWidth>
                      <InputLabel id="difficulty-label">Language level</InputLabel>
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
                  className="poster-surface panel-reveal"
                  sx={{
                    p: { xs: 2.5, md: 3 },
                    borderRadius: { xs: 6, md: 8 },
                    background:
                      "linear-gradient(180deg, rgba(23,19,18,0.96), rgba(23,19,18,0.92))",
                    color: "#fff7ea",
                  }}
                >
                  <SectionStamp accent="rgba(255, 247, 234, 0.66)">Current Manifest</SectionStamp>
                  <Typography variant="h5" sx={{ mt: 0.6, color: "#fff7ea" }}>
                    Ready to launch
                  </Typography>
                  <Stack spacing={1} sx={{ mt: 2.5 }}>
                    {[
                      `words: ${parsedWords.length}`,
                      `normalization: ${normalizationEnabled ? "enabled" : "disabled"}`,
                      `examples: ${SENTENCE_LANGUAGE_LABELS[sentenceLang]}`,
                      `translations: ${TRANSLATION_LANGUAGE_LABELS[translationLang]}`,
                      `level: ${DIFFICULTY_LABELS[difficulty]}`,
                    ].map((line) => (
                      <Typography
                        key={line}
                        className="mono"
                        sx={{ fontSize: 12, color: "rgba(255, 247, 234, 0.74)" }}
                      >
                        {line}
                      </Typography>
                    ))}
                  </Stack>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={handleGenerateDeck}
                    disabled={parsedWords.length === 0 || isSubmitting}
                    sx={{ mt: 3, minWidth: 220 }}
                  >
                    {isSubmitting ? (
                      <CircularProgress size={18} color="inherit" />
                    ) : (
                      "Generate Deck"
                    )}
                  </Button>
                </Paper>
              </Stack>
            </Box>
          )}

          {viewState === "PROCESSING" && (
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: { xs: "1fr", xl: "minmax(0, 0.95fr) minmax(340px, 1.05fr)" },
                gap: 3,
              }}
            >
              <Paper
                className="poster-surface panel-reveal"
                sx={{
                  p: { xs: 2.5, md: 3.5 },
                  borderRadius: { xs: 6, md: 8 },
                  background:
                    "linear-gradient(180deg, rgba(255,255,255,0.84), rgba(244, 201, 79, 0.16))",
                }}
              >
                <Stack spacing={2.5}>
                  <Stack
                    direction={{ xs: "column", sm: "row" }}
                    spacing={2}
                    justifyContent="space-between"
                    alignItems={{ xs: "flex-start", sm: "center" }}
                  >
                    <Box>
                      <SectionStamp>Forge Status</SectionStamp>
                      <Typography variant="h4" sx={{ mt: 0.4 }}>
                        {currentStatusMeta?.label ?? "Starting"}
                      </Typography>
                    </Box>
                    <GlyphBadge accent={currentStatusMeta?.accent ?? "var(--signal-yellow)"}>
                      {hasStartedProcessing ? <CircularProgress size={28} color="inherit" /> : <ForgeIcon />}
                    </GlyphBadge>
                  </Stack>

                  <Typography variant="body1" sx={{ color: "text.secondary", maxWidth: 540 }}>
                    {currentStatusMeta?.description ??
                      "The task has been submitted and is waiting for the first worker cycle."}
                  </Typography>

                  <Typography
                    variant="h1"
                    sx={{
                      fontSize: { xs: "4rem", md: "6rem" },
                      lineHeight: 0.9,
                    }}
                  >
                    {roundedProgress}
                    <Box component="span" sx={{ color: "primary.main" }}>
                      %
                    </Box>
                  </Typography>

                  <Box>
                    <LinearProgress
                      variant="determinate"
                      value={processingProgress}
                      sx={{
                        "& .MuiLinearProgress-bar": {
                          background:
                            "linear-gradient(90deg, var(--signal), var(--signal-yellow))",
                        },
                      }}
                    />
                    <Stack
                      direction={{ xs: "column", sm: "row" }}
                      spacing={1.5}
                      justifyContent="space-between"
                      sx={{ mt: 1 }}
                    >
                      <Typography className="mono" sx={{ fontSize: 12, color: "text.secondary" }}>
                        {doneItems}/{totalItems} words fully finished
                      </Typography>
                      {taskStatus && (
                        <StatusPill
                          label={TASK_STATUS_META[taskStatus].label}
                          background={alpha(TASK_STATUS_META[taskStatus].accent, 0.18)}
                          color="#171312"
                        />
                      )}
                    </Stack>
                  </Box>

                  <Box
                    sx={{
                      display: "grid",
                      gridTemplateColumns: {
                        xs: "repeat(2, minmax(0, 1fr))",
                        md: "repeat(4, minmax(0, 1fr))",
                      },
                      gap: 1.5,
                    }}
                  >
                    <MetricTile
                      label="Done"
                      value={String(doneItems)}
                      accent="var(--signal-green)"
                    />
                    <MetricTile
                      label="Running"
                      value={String(processingItems)}
                      accent="var(--signal-blue)"
                    />
                    <MetricTile
                      label="Queued"
                      value={String(pendingItems)}
                      accent="var(--signal-yellow)"
                    />
                    <MetricTile
                      label="Failed"
                      value={String(errorItems)}
                      accent="var(--signal-red)"
                    />
                  </Box>
                </Stack>
              </Paper>

              <Paper
                className="poster-surface panel-reveal"
                sx={{
                  p: { xs: 2.5, md: 3 },
                  borderRadius: { xs: 6, md: 8 },
                  background:
                    "linear-gradient(180deg, rgba(255,255,255,0.78), rgba(35, 88, 255, 0.08))",
                }}
              >
                <Stack spacing={2}>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      gap: 2,
                      flexWrap: "wrap",
                      alignItems: "center",
                    }}
                  >
                    <Box>
                      <SectionStamp>Live Queue</SectionStamp>
                      <Typography variant="h5" sx={{ mt: 0.5 }}>
                        Word-by-word ledger
                      </Typography>
                    </Box>
                    <Typography className="mono" sx={{ fontSize: 12, color: "text.secondary" }}>
                      polling every 2.5s
                    </Typography>
                  </Box>
                  <Stack
                    spacing={1.2}
                    sx={{
                      maxHeight: { xs: "none", xl: 620 },
                      overflowY: "auto",
                      pr: { xl: 0.5 },
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
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: { xs: "1fr", xl: "minmax(0, 0.9fr) minmax(340px, 1.1fr)" },
                gap: 3,
              }}
            >
              <Paper
                className="poster-surface panel-reveal"
                sx={{
                  p: { xs: 2.5, md: 3.5 },
                  borderRadius: { xs: 6, md: 8 },
                  background:
                    "linear-gradient(180deg, rgba(255,255,255,0.82), rgba(45, 143, 92, 0.14))",
                }}
              >
                <Stack spacing={2.5}>
                  <Stack
                    direction={{ xs: "column", sm: "row" }}
                    spacing={2}
                    justifyContent="space-between"
                    alignItems={{ xs: "flex-start", sm: "center" }}
                  >
                    <Box>
                      <SectionStamp>Deck Output</SectionStamp>
                      <Typography variant="h4" sx={{ mt: 0.4 }}>
                        Ready for import
                      </Typography>
                    </Box>
                    <GlyphBadge accent="var(--signal-green)">
                      <DownloadIcon />
                    </GlyphBadge>
                  </Stack>

                  <Typography
                    variant="h2"
                    sx={{
                      fontSize: { xs: "3rem", md: "4.4rem" },
                      maxWidth: 520,
                    }}
                  >
                    {successfulCards} cards are boxed and waiting.
                  </Typography>
                  <Typography variant="body1" sx={{ color: "text.secondary", maxWidth: 560 }}>
                    Download the generated `.apkg`, import it into Anki, and start
                    studying immediately.
                  </Typography>

                  {isPartiallyDone && (
                    <Alert
                      severity="warning"
                      sx={{
                        backgroundColor: alpha("#ffefc6", 0.92),
                      }}
                    >
                      Deck is ready, but some words failed during processing.
                    </Alert>
                  )}

                  <Box
                    sx={{
                      display: "grid",
                      gridTemplateColumns: {
                        xs: "repeat(2, minmax(0, 1fr))",
                        md: "repeat(3, minmax(0, 1fr))",
                      },
                      gap: 1.5,
                    }}
                  >
                    <MetricTile
                      label="Succeeded"
                      value={String(doneItems)}
                      accent="var(--signal-green)"
                    />
                    <MetricTile
                      label="Failed"
                      value={String(errorItems)}
                      accent="var(--signal-red)"
                    />
                    <MetricTile
                      label="Submitted"
                      value={String(totalItems)}
                      accent="var(--signal-blue)"
                    />
                  </Box>

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
                    <Button variant="outlined" size="large" onClick={handleCreateAnother}>
                      Create Another
                    </Button>
                  </Stack>
                </Stack>
              </Paper>

              <Paper
                className="poster-surface panel-reveal"
                sx={{
                  p: { xs: 2.5, md: 3 },
                  borderRadius: { xs: 6, md: 8 },
                  background:
                    "linear-gradient(180deg, rgba(255,255,255,0.8), rgba(244, 201, 79, 0.1))",
                }}
              >
                <Stack spacing={2}>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      gap: 2,
                      flexWrap: "wrap",
                      alignItems: "center",
                    }}
                  >
                    <Box>
                      <SectionStamp>Final Ledger</SectionStamp>
                      <Typography variant="h5" sx={{ mt: 0.5 }}>
                        Completion map
                      </Typography>
                    </Box>
                    {taskStatus && (
                      <StatusPill
                        label={TASK_STATUS_META[taskStatus].label}
                        background={alpha(TASK_STATUS_META[taskStatus].accent, 0.18)}
                        color="#171312"
                      />
                    )}
                  </Box>
                  <Stack
                    spacing={1.2}
                    sx={{
                      maxHeight: { xs: "none", xl: 620 },
                      overflowY: "auto",
                      pr: { xl: 0.5 },
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

          {taskHistory.length > 0 && (
            <Paper
              className="poster-surface panel-reveal"
              sx={{
                p: { xs: 2.5, md: 3 },
                borderRadius: { xs: 6, md: 8 },
                background:
                  "linear-gradient(180deg, rgba(255,255,255,0.78), rgba(35, 88, 255, 0.06))",
              }}
            >
              <Stack spacing={2.5}>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 2,
                    flexWrap: "wrap",
                    alignItems: "center",
                  }}
                >
                  <Box>
                    <SectionStamp>Archive</SectionStamp>
                    <Typography variant="h5" sx={{ mt: 0.5 }}>
                      Previous deck runs
                    </Typography>
                  </Box>
                  <Typography className="mono" sx={{ fontSize: 12, color: "text.secondary" }}>
                    {taskHistory.length} saved tasks
                  </Typography>
                </Box>

                <Box
                  sx={{
                    display: "grid",
                    gridTemplateColumns: {
                      xs: "1fr",
                      md: "repeat(2, minmax(0, 1fr))",
                      xl: "repeat(3, minmax(0, 1fr))",
                    },
                    gap: 1.5,
                  }}
                >
                  {taskHistory.map((task) => (
                    <ArchiveCard
                      key={task.id}
                      task={task}
                      onDownload={handleHistoryDownload}
                    />
                  ))}
                </Box>
              </Stack>
            </Paper>
          )}
        </Stack>
      </Container>
    </Box>
  );
}

export default AppPage;
