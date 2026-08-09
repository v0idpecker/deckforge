export type DeckTaskStatusValue =
  | "PENDING"
  | "PROCESSING"
  | "DONE"
  | "PARTIALLY_DONE";

export type DeckItemStatusValue = "PENDING" | "PROCESSING" | "DONE" | "ERROR";

export type DeckItemStageValue =
  | "INIT"
  | "NORMILIZED"
  | "CONTEXT_GENERATED"
  | "DONE"
  | null;

export type DifficultyLevel = "A1" | "A2" | "B1" | "B2" | "C1" | "C2";

export type DeckTaskCreateRequest = {
  words: string[];
  options: {
    normalization: boolean;
    limit: number;
    sentence_lang: "english" | "german" | "spanish" | "french" | "italian";
    translation_lang: "russian" | "english" | "german" | "spanish" | "french";
    difficulty: DifficultyLevel;
  };
};

export type DeckTaskCreateResponse = {
  task_id: string;
};

export type DeckTaskItemStatus = {
  raw_word: string;
  status: DeckItemStatusValue;
  stage: DeckItemStageValue;
};

export type DeckTaskStatusResponse = {
  status: DeckTaskStatusValue;
  items: DeckTaskItemStatus[];
};

export type DeckTaskHistoryItem = {
  id: string;
  status: DeckTaskStatusValue;
  total_items: number;
};

export type DeckCard = {
  id: string;
  word: string;
  sentence: string;
  translation: string;
};

export type DeckCardsResponse = {
  task_id: string;
  suggested_deck_name: string;
  cards: DeckCard[];
};

export type EditableCard = {
  card: DeckCard;
  selected: boolean;
  sentence: string;
  translation: string;
};
