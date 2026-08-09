import type { DeckCard } from "../types/decks";

const ANKI_BASE_URL = "http://127.0.0.1:8765";

const MODEL_NAME = "DeckForge Basic";

interface AnkiResponse<T> {
  result: T | null;
  error: string | null;
}

export class AnkiConnectError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AnkiConnectError";
  }
}

/**
 * Единый запрос к локальному AnkiConnect.
 * Без auth-заголовков: это не наш бэкенд, Bearer-токен AnkiConnect не знает.
 * Когда Anki выключен или CORS не разрешает origin — fetch падает с TypeError,
 * что на стороне диалога интерпретируется как "unreachable".
 */
async function ankiRequest<T>(action: string, params?: object): Promise<T> {
  const response = await fetch(ANKI_BASE_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, version: 6, params }),
  });

  if (!response.ok) {
    throw new Error(`AnkiConnect HTTP ${response.status}`);
  }

  const payload = (await response.json()) as AnkiResponse<T>;

  if (payload.error) {
    throw new AnkiConnectError(payload.error);
  }

  return payload.result as T;
}

export async function ankiPing(): Promise<boolean> {
  // Не все сборки AnkiConnect знают action "ping" (часть отвечает
  // "unsupported action"), поэтому основной пробой берём "version" —
  // базовый action, поддерживаемый всеми версиями API.
  try {
    const version = await ankiRequest<number>("version");
    return typeof version === "number";
  } catch (cause) {
    if (cause instanceof AnkiConnectError) {
      // Теоретически возможна сборка без "version" — пробуем "ping".
      try {
        const result = await ankiRequest<number>("ping");
        return result === 6;
      } catch {
        return false;
      }
    }
    throw cause; // сеть/CORS — пусть обрабатывает вызывающий код
  }
}

/**
 * Проверка живости сервера в обход CORS. no-cors-запрос резолвится с opaque-
 * ответом, если сервер отвечает (даже когда origin не разрешён), и падает с
 * TypeError, если соединение не установлено. Это позволяет отличить
 * «Anki выключен» от «Anki работает, но origin не в webCorsOriginList» —
 * обычный fetch в обоих случаях падает с TypeError одинаково.
 */
export async function probeAnkiReachable(): Promise<boolean> {
  try {
    await fetch(ANKI_BASE_URL, {
      method: "POST",
      mode: "no-cors",
      headers: { "Content-Type": "text/plain" },
      body: "{}",
    });
    return true;
  } catch {
    return false;
  }
}

export async function listAnkiDecks(): Promise<string[]> {
  return ankiRequest<string[]>("deckNames");
}

/**
 * Идемпотентно гарантирует наличие модели «DeckForge Basic» (поля
 * Sentence/Translation, шаблон как в genanki). createModel не идемпотентен
 * (падает, если модель уже есть), поэтому сначала проверяем modelNames.
 */
export async function ensureDeckForgeModel(): Promise<void> {
  const modelNames = await ankiRequest<string[]>("modelNames");

  if (modelNames.includes(MODEL_NAME)) {
    return;
  }

  await ankiRequest<void>("createModel", {
    modelName: MODEL_NAME,
    inOrderFields: ["Sentence", "Translation"],
    css: "",
    isCloze: false,
    cardTemplates: [
      {
        Name: "Card 1",
        Front: "{{Sentence}}",
        Back: '{{FrontSide}}<hr id="answer">{{Translation}}',
      },
    ],
  });
}

/**
 * Отправляет все карточки одним батчем addNotes.
 * result — массив id добавленных заметок (number) или null (не добавлена,
 * обычно точный дубликат по первому полю).
 */
export async function pushCardsToAnki(
  deckName: string,
  cards: DeckCard[],
): Promise<{ sent: number; skipped: number }> {
  const notes = cards.map((card) => ({
    deckName,
    modelName: MODEL_NAME,
    fields: { Sentence: card.sentence, Translation: card.translation },
    tags: ["deckforge"],
    options: { allowDuplicate: false },
  }));

  const result = await ankiRequest<(number | null)[]>("addNotes", { notes });

  let sent = 0;
  let skipped = 0;

  for (const id of result ?? []) {
    if (typeof id === "number") {
      sent += 1;
    } else {
      skipped += 1;
    }
  }

  return { sent, skipped };
}
