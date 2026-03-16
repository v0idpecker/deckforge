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

export type DeckTaskCreateRequest = {
  words: string[];
  options: Record<string, never>;
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
