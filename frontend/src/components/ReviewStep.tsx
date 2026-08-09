import { useMemo, useState } from "react";
import {
  Box,
  Button,
  Checkbox,
  Chip,
  IconButton,
  Paper,
  Stack,
  SvgIcon,
  TextField,
  Typography,
} from "@mui/material";
import type { EditableCard } from "../types/decks";

const PAGE_SIZE = 50;

type CardPatch = Partial<
  Pick<EditableCard, "selected" | "sentence" | "translation">
>;

type ReviewStepProps = {
  cards: EditableCard[];
  onCardChange: (id: string, patch: CardPatch) => void;
  onCardRemove: (id: string) => void;
};

function TrashIcon() {
  return (
    <SvgIcon viewBox="0 0 24 24" sx={{ fontSize: 18 }}>
      <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" />
    </SvgIcon>
  );
}

function ReviewRow({
  card,
  onChange,
  onRemove,
}: {
  card: EditableCard;
  onChange: (patch: CardPatch) => void;
  onRemove: () => void;
}) {
  const sentenceError = card.selected && card.sentence.trim().length === 0;

  return (
    <Paper sx={{ p: 1.5 }}>
      <Stack spacing={1}>
        <Stack
          direction="row"
          alignItems="center"
          justifyContent="space-between"
        >
          <Stack direction="row" spacing={1} alignItems="center">
            <Checkbox
              size="small"
              checked={card.selected}
              onChange={(event) => onChange({ selected: event.target.checked })}
            />
            <Chip label={card.card.word} size="small" />
          </Stack>
          <IconButton
            size="small"
            onClick={onRemove}
            title="Remove this card"
          >
            <TrashIcon />
          </IconButton>
        </Stack>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
          <TextField
            label="Sentence"
            value={card.sentence}
            onChange={(event) => onChange({ sentence: event.target.value })}
            size="small"
            fullWidth
            error={sentenceError}
          />
          <TextField
            label="Translation"
            value={card.translation}
            onChange={(event) => onChange({ translation: event.target.value })}
            size="small"
            fullWidth
          />
        </Stack>
      </Stack>
    </Paper>
  );
}

export function ReviewStep({
  cards,
  onCardChange,
  onCardRemove,
}: ReviewStepProps) {
  const [filter, setFilter] = useState("");
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);

  const selectedCount = cards.filter((card) => card.selected).length;

  // Фильтр применяется ко всему набору, пагинация — к отфильтрованному,
  // иначе «нашёл слово — а оно на странице 4».
  const filtered = useMemo(() => {
    const query = filter.trim().toLowerCase();
    if (!query) {
      return cards;
    }
    return cards.filter((card) =>
      card.card.word.toLowerCase().includes(query),
    );
  }, [cards, filter]);

  const visible = filtered.slice(0, visibleCount);
  const hasMore = filtered.length > visibleCount;

  const handleFilterChange = (value: string) => {
    setFilter(value);
    setVisibleCount(PAGE_SIZE);
  };

  return (
    <Stack spacing={1.5}>
      <Stack
        direction="row"
        justifyContent="space-between"
        alignItems="center"
        gap={1}
        flexWrap="wrap"
      >
        <Typography variant="body2" sx={{ fontWeight: 600 }}>
          {selectedCount} of {cards.length} cards selected
        </Typography>
        <Typography variant="body2" sx={{ color: "text.secondary" }}>
          Changes apply to this send only
        </Typography>
      </Stack>

      <TextField
        label="Filter by word"
        placeholder="e.g. run"
        value={filter}
        onChange={(event) => handleFilterChange(event.target.value)}
        size="small"
        fullWidth
      />

      <Box sx={{ maxHeight: 420, overflowY: "auto", pr: 0.5 }}>
        <Stack spacing={1}>
          {visible.map((card) => (
            <ReviewRow
              key={card.card.id}
              card={card}
              onChange={(patch) => onCardChange(card.card.id, patch)}
              onRemove={() => onCardRemove(card.card.id)}
            />
          ))}
          {visible.length === 0 && (
            <Typography
              variant="body2"
              sx={{ color: "text.secondary", py: 2, textAlign: "center" }}
            >
              No cards match the filter.
            </Typography>
          )}
        </Stack>
      </Box>

      {hasMore && (
        <Button onClick={() => setVisibleCount((count) => count + PAGE_SIZE)}>
          Load more ({filtered.length - visibleCount} remaining)
        </Button>
      )}
    </Stack>
  );
}
