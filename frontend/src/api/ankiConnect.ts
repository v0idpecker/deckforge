const ANKI_BASE_URL = "http://127.0.0.1:8765";

import type { CardFormat } from "../types/decks";

const BASIC_MODEL_NAME = "DeckForge Context";
const CLOZE_MODEL_NAME = "DeckForge Cloze";

const MODEL_CSS = `.card {
  font-family: Arial, sans-serif;
  font-size: 22px;
  text-align: center;
  color: #1a1c1e;
  background-color: #f3f5f7;
  padding: 24px;
}
.sentence {
  font-size: 26px;
  line-height: 1.4;
  margin-bottom: 16px;
}
.target-word {
  font-weight: 700;
  color: #0d9488;
}
.translation {
  color: #555;
}
.nightMode .card {
  color: #e4e6e8;
  background-color: #1a1c1e;
}
.nightMode .translation {
  color: #a8abae;
}
.nightMode .target-word {
  color: #2dd4bf;
}`;

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
 * Идемпотентно гарантирует наличие модели для выбранного формата карточек
 * («DeckForge Context» — basic, «DeckForge Cloze» — cloze). createModel не
 * идемпотентен (падает, если модель уже есть), поэтому сначала проверяем
 * modelNames. Имена и шаблоны зеркалят genanki-модели бэкенда.
 */
export async function ensureDeckForgeModel(cardFormat: CardFormat): Promise<void> {
  const modelNames = await ankiRequest<string[]>("modelNames");

  if (cardFormat === "cloze") {
    if (modelNames.includes(CLOZE_MODEL_NAME)) {
      return;
    }
    await ankiRequest<void>("createModel", {
      modelName: CLOZE_MODEL_NAME,
      inOrderFields: ["Sentence", "Translation"],
      css: MODEL_CSS,
      isCloze: true,
      cardTemplates: [
        {
          Name: "Cloze",
          Front: '<div class="sentence">{{cloze:Sentence}}</div>',
          Back: '{{cloze:Sentence}}<hr id="answer"><div class="translation">{{Translation}}</div>',
        },
      ],
    });
    return;
  }

  if (modelNames.includes(BASIC_MODEL_NAME)) {
    return;
  }

  await ankiRequest<void>("createModel", {
    modelName: BASIC_MODEL_NAME,
    inOrderFields: ["Sentence", "Translation"],
    css: MODEL_CSS,
    isCloze: false,
    cardTemplates: [
      {
        Name: "Card 1",
        Front: '<div class="sentence">{{Sentence}}</div>',
        Back: '{{FrontSide}}<hr id="answer"><div class="translation">{{Translation}}</div>',
      },
    ],
  });
}

export function escapeHtml(text: string): string {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

/**
 * TS-зеркало highlight_sentence бэкенда: экранирование обеих строк,
 * первое вхождение формы case-insensitive, оригинальный регистр сохраняется.
 */
export function highlightSentence(sentence: string, form: string | null): string {
  const escaped = escapeHtml(sentence);
  if (!form || form.trim() === "") {
    return escaped;
  }
  const escapedForm = escapeHtml(form.trim());
  if (escapedForm === "") {
    return escaped;
  }
  const pattern = new RegExp(escapedForm.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i");
  const match = escaped.match(pattern);
  if (!match || match.index === undefined) {
    return escaped;
  }
  const wrapped = `<span class="target-word">${match[0]}</span>`;
  return escaped.slice(0, match.index) + wrapped + escaped.slice(match.index + match[0].length);
}

/**
 * Отправляет отобранные карточки одним батчем addNotes.
 * Принимает только то, что реально нужно AnkiConnect — пары текст/перевод:
 * отредактированные карточки больше не являются DeckCard в строгом смысле.
 * cardFormat определяет, к какой модели привязываются заметки.
 * result — массив id добавленных заметок (number) или null (не добавлена,
 * обычно точный дубликат по первому полю).
 */
export async function pushCardsToAnki(
  deckName: string,
  cards: Array<{ sentence: string; translation: string }>,
  cardFormat: CardFormat = "basic",
): Promise<{ sent: number; skipped: number }> {
  const notes = cards.map((card) => ({
    deckName,
    modelName: cardFormat === "cloze" ? CLOZE_MODEL_NAME : BASIC_MODEL_NAME,
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
