import { Autocomplete, Stack, TextField, Typography } from "@mui/material";

export const CREATE_NEW_OPTION = "＋ Create new deck…";

type DestinationStepProps = {
  decks: string[];
  selectedDeck: string | null;
  creatingNew: boolean;
  newDeckName: string;
  cardCount: number;
  onDeckChange: (value: string | null) => void;
  onNewDeckNameChange: (value: string) => void;
};

export function DestinationStep({
  decks,
  selectedDeck,
  creatingNew,
  newDeckName,
  cardCount,
  onDeckChange,
  onNewDeckNameChange,
}: DestinationStepProps) {
  return (
    <Stack spacing={2}>
      <Typography variant="body2" sx={{ color: "text.secondary" }}>
        {cardCount} cards will be sent to the selected deck.
      </Typography>
      <Autocomplete
        options={[...decks, CREATE_NEW_OPTION]}
        value={selectedDeck}
        onChange={(_, value) => onDeckChange(value)}
        renderInput={(params) => (
          <TextField {...params} label="Deck" placeholder="Pick a deck…" />
        )}
      />
      {creatingNew && (
        <TextField
          label="New deck name"
          value={newDeckName}
          onChange={(event) => onNewDeckNameChange(event.target.value)}
          fullWidth
        />
      )}
    </Stack>
  );
}
