import { useEffect, useState } from "react";
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import {
  AnkiConnectError,
  ankiPing,
  ensureDeckForgeModel,
  listAnkiDecks,
  probeAnkiReachable,
  pushCardsToAnki,
} from "../api/ankiConnect";
import { getDeckCards } from "../api/decks";
import type { DeckCard } from "../types/decks";

const CREATE_NEW_OPTION = "＋ Create new deck…";

type DialogState =
  | "loading"
  | "unreachable"
  | "cors_blocked"
  | "anki_error"
  | "choose_deck"
  | "sending"
  | "success"
  | "partial"
  | "error";

type ResultInfo = {
  deckName: string;
  sent: number;
  skipped: number;
};

type Props = {
  open: boolean;
  taskId: string | null;
  onClose: () => void;
};

function unreachableHelp(): string {
  return [
    "Make sure Anki Desktop is running and the AnkiConnect add-on is installed and enabled.",
    "AnkiConnect listens on 127.0.0.1:8765 — nothing else should occupy that port.",
  ].join(" ");
}

/**
 * Определяет тип сбоя без setState (безопасно вызывать из эффекта).
 * TypeError от fetch бывает и когда Anki выключен, и когда CORS блокирует
 * origin, поэтому дополнительно делаем no-cors-пробу живости сервера.
 */
async function classifyFailure(
  cause: unknown,
): Promise<"unreachable" | "cors_blocked" | "anki_error" | "error"> {
  if (cause instanceof TypeError) {
    const reachable = await probeAnkiReachable();
    return reachable ? "cors_blocked" : "unreachable";
  }

  if (cause instanceof AnkiConnectError) {
    return "anki_error";
  }

  return "error";
}

export function SendToAnkiDialog({ open, taskId, onClose }: Props) {
  const [state, setState] = useState<DialogState>("loading");
  const [decks, setDecks] = useState<string[]>([]);
  const [cards, setCards] = useState<DeckCard[]>([]);
  const [suggestedDeckName, setSuggestedDeckName] = useState("");
  const [selectedDeck, setSelectedDeck] = useState<string | null>(null);
  const [creatingNew, setCreatingNew] = useState(false);
  const [newDeckName, setNewDeckName] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [result, setResult] = useState<ResultInfo | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const [copied, setCopied] = useState(false);

  const origin = window.location.origin;

  useEffect(() => {
    if (!open || !taskId) {
      return;
    }

    let cancelled = false;

    const run = async () => {
      setState("loading");
      setDecks([]);
      setCards([]);
      setSuggestedDeckName("");
      setSelectedDeck(null);
      setCreatingNew(false);
      setNewDeckName("");
      setErrorMsg(null);
      setResult(null);

      try {
        const alive = await ankiPing();
        if (cancelled) {
          return;
        }

        if (!alive) {
          setErrorMsg("AnkiConnect responded with an unexpected result.");
          setState("anki_error");
          return;
        }

        const [deckNames, cardsResponse] = await Promise.all([
          listAnkiDecks(),
          getDeckCards(taskId),
        ]);
        if (cancelled) {
          return;
        }

        setDecks(deckNames);
        setCards(cardsResponse.cards);
        setSuggestedDeckName(cardsResponse.suggested_deck_name);

        // Единственная неидемпотентная операция держится отдельно от push-флоу:
        // её сбой не должен блокировать отправку (если модели реально нет,
        // addNotes вернёт понятную ошибку).
        try {
          await ensureDeckForgeModel();
        } catch {
          // ignore — non-blocking by design
        }
        if (cancelled) {
          return;
        }

        setState("choose_deck");
      } catch (cause) {
        if (cancelled) {
          return;
        }

        const next = await classifyFailure(cause);
        if (next === "anki_error" || next === "error") {
          setErrorMsg(
            cause instanceof Error ? cause.message : "Unknown error",
          );
        }
        setState(next);
      }
    };

    void run();

    return () => {
      cancelled = true;
    };
  }, [open, taskId, reloadKey]);

  const handleRetry = () => {
    setReloadKey((key) => key + 1);
  };

  const handleSend = async () => {
    const deckName = creatingNew ? newDeckName.trim() : selectedDeck;

    if (!deckName || cards.length === 0) {
      return;
    }

    setState("sending");
    setErrorMsg(null);

    try {
      const { sent, skipped } = await pushCardsToAnki(deckName, cards);
      setResult({ deckName, sent, skipped });
      setState(skipped === 0 ? "success" : "partial");
    } catch (cause) {
      const next = await classifyFailure(cause);
      if (next === "anki_error" || next === "error") {
        setErrorMsg(cause instanceof Error ? cause.message : "Unknown error");
      }
      setState(next);
    }
  };

  const canSend = creatingNew
    ? newDeckName.trim().length > 0
    : selectedDeck !== null;

  const handleDeckChange = (value: string | null) => {
    if (value === CREATE_NEW_OPTION) {
      setCreatingNew(true);
      setSelectedDeck(null);
      setNewDeckName(suggestedDeckName);
      return;
    }

    setCreatingNew(false);
    setSelectedDeck(value);
  };

  const handleCopyOrigin = async () => {
    try {
      await navigator.clipboard.writeText(origin);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard может быть недоступен — игнорируем
    }
  };

  const renderBody = () => {
    switch (state) {
      case "loading":
        return (
          <Stack spacing={2} alignItems="center" sx={{ py: 3 }}>
            <CircularProgress size={28} />
            <Typography variant="body2" sx={{ color: "text.secondary" }}>
              Checking AnkiConnect…
            </Typography>
          </Stack>
        );

      case "unreachable":
        return (
          <Stack spacing={2}>
            <Alert severity="error">
              Cannot reach AnkiConnect on{" "}
              <span className="mono">127.0.0.1:8765</span>.
            </Alert>
            <Typography variant="body2" sx={{ color: "text.secondary" }}>
              {unreachableHelp()}
            </Typography>
          </Stack>
        );

      case "cors_blocked":
        return (
          <Stack spacing={1.5}>
            <Alert severity="warning">
              AnkiConnect is running, but it is blocking this site's origin.
            </Alert>
            <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
              <Typography
                className="mono"
                sx={{
                  flex: 1,
                  fontSize: 12,
                  px: 1.25,
                  py: 0.75,
                  borderRadius: 1,
                  backgroundColor: "#f3f4f6",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
                title={origin}
              >
                {origin}
              </Typography>
              <Button
                size="small"
                variant="outlined"
                onClick={handleCopyOrigin}
                sx={{ flexShrink: 0 }}
              >
                {copied ? "Copied" : "Copy"}
              </Button>
            </Box>
            <Typography variant="body2" sx={{ color: "text.secondary" }}>
              Add this origin to the add-on's <span className="mono">webCorsOriginList</span>{" "}
              (Tools → Add-ons → AnkiConnect → Config), or set{" "}
              <span className="mono">ignoreOriginList</span> to{" "}
              <span className="mono">["*"]</span>.
            </Typography>
            <Typography variant="body2" sx={{ color: "text.secondary" }}>
              Python and curl don't enforce CORS, which is why the API works
              there but the browser blocks it here.
            </Typography>
          </Stack>
        );

      case "anki_error":
        return (
          <Stack spacing={2}>
            <Alert severity="error">
              AnkiConnect returned an error: {errorMsg}
            </Alert>
            <Typography variant="body2" sx={{ color: "text.secondary" }}>
              {unreachableHelp()}
            </Typography>
          </Stack>
        );

      case "choose_deck":
        return (
          <Stack spacing={2}>
            <Typography variant="body2" sx={{ color: "text.secondary" }}>
              {cards.length} cards will be sent to the selected deck.
            </Typography>
            <Autocomplete
              options={[...decks, CREATE_NEW_OPTION]}
              value={selectedDeck}
              onChange={(_, value) => handleDeckChange(value)}
              renderInput={(params) => (
                <TextField {...params} label="Deck" placeholder="Pick a deck…" />
              )}
            />
            {creatingNew && (
              <TextField
                label="New deck name"
                value={newDeckName}
                onChange={(event) => setNewDeckName(event.target.value)}
                fullWidth
              />
            )}
          </Stack>
        );

      case "sending":
        return (
          <Stack spacing={2} alignItems="center" sx={{ py: 3 }}>
            <CircularProgress size={28} />
            <Typography variant="body2" sx={{ color: "text.secondary" }}>
              Sending {cards.length} cards to “
              {creatingNew ? newDeckName.trim() : selectedDeck}”…
            </Typography>
          </Stack>
        );

      case "success":
        return (
          <Alert severity="success">
            {result?.sent ?? cards.length} cards added to “{result?.deckName}”.
          </Alert>
        );

      case "partial":
        return (
          <Alert severity="warning">
            {result?.sent ?? 0} cards added, {result?.skipped ?? 0} skipped
            (duplicates already in Anki).
          </Alert>
        );

      case "error":
        return <Alert severity="error">Unexpected error: {errorMsg}</Alert>;
    }
  };

  const renderActions = () => {
    switch (state) {
      case "choose_deck":
        return (
          <>
            <Button onClick={onClose}>Cancel</Button>
            <Button variant="contained" onClick={handleSend} disabled={!canSend}>
              Send to Anki
            </Button>
          </>
        );

      case "sending":
        return (
          <Button variant="contained" disabled>
            Sending…
          </Button>
        );

      case "success":
      case "partial":
        return (
          <Button variant="contained" onClick={onClose}>
            Close
          </Button>
        );

      case "unreachable":
      case "cors_blocked":
      case "anki_error":
      case "error":
        return (
          <>
            <Button onClick={onClose}>Close</Button>
            <Button variant="contained" onClick={handleRetry}>
              Retry
            </Button>
          </>
        );

      case "loading":
        return null;
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Send to Anki</DialogTitle>
      <DialogContent>
        <Box sx={{ py: 0.5 }}>{renderBody()}</Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>{renderActions()}</DialogActions>
    </Dialog>
  );
}
