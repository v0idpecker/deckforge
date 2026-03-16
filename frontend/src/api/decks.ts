import type {
  DeckTaskCreateRequest,
  DeckTaskCreateResponse,
  DeckTaskHistoryItem,
  DeckTaskItemStatus,
  DeckTaskStatusResponse,
} from "../types/decks";
import { ApiError, authHeaders, buildApiUrl, request } from "./client";

export async function createDeckTask(
  payload: DeckTaskCreateRequest,
): Promise<DeckTaskCreateResponse> {
  const rawResponse = await request<unknown>("/decks/", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (typeof rawResponse === "string" && rawResponse.length > 0) {
    return { task_id: rawResponse };
  }

  if (
    typeof rawResponse === "object" &&
    rawResponse !== null &&
    "task_id" in rawResponse &&
    typeof rawResponse.task_id === "string"
  ) {
    return { task_id: rawResponse.task_id };
  }

  throw new ApiError("Invalid create task response format", 500);
}

export async function getDeckTaskStatus(
  taskId: string,
): Promise<DeckTaskStatusResponse> {
  const rawResponse = await request<unknown>(`/decks/${taskId}/status`, {
    method: "GET",
  });

  if (typeof rawResponse === "string") {
    return {
      status: rawResponse,
      items: [],
    } as DeckTaskStatusResponse;
  }

  if (
    typeof rawResponse === "object" &&
    rawResponse !== null &&
    "status" in rawResponse &&
    typeof rawResponse.status === "string"
  ) {
    const responsePayload = rawResponse as {
      status: string;
      items?: unknown;
    };

    const items = Array.isArray(responsePayload.items)
      ? (responsePayload.items as DeckTaskItemStatus[])
      : [];

    return {
      status: responsePayload.status as DeckTaskStatusResponse["status"],
      items,
    };
  }

  throw new ApiError("Invalid task status response format", 500);
}

export async function listDeckTasks(): Promise<DeckTaskHistoryItem[]> {
  const rawResponse = await request<unknown>("/decks/", {
    method: "GET",
  });

  if (!Array.isArray(rawResponse)) {
    throw new ApiError("Invalid deck list response format", 500);
  }

  return rawResponse.map((item) => {
    if (typeof item !== "object" || item === null) {
      throw new ApiError("Invalid deck list response format", 500);
    }

    const payload = item as {
      id?: unknown;
      status?: unknown;
      total_items?: unknown;
    };

    if (
      typeof payload.id !== "string" ||
      typeof payload.status !== "string" ||
      typeof payload.total_items !== "number"
    ) {
      throw new ApiError("Invalid deck list response format", 500);
    }

    return {
      id: payload.id,
      status: payload.status as DeckTaskHistoryItem["status"],
      total_items: payload.total_items,
    };
  });
}

function getFilenameFromHeaders(headers: Headers): string | null {
  const contentDisposition = headers.get("content-disposition");
  if (!contentDisposition) {
    return null;
  }

  const filenameMatch = contentDisposition.match(
    /filename\*?=(?:UTF-8''|")?([^";]+)/i,
  );
  if (!filenameMatch?.[1]) {
    return null;
  }

  return decodeURIComponent(filenameMatch[1].trim());
}

export async function downloadDeckResult(
  taskId: string,
): Promise<{ blob: Blob; filename: string | null }> {
  const response = await fetch(buildApiUrl(`/decks/${taskId}/result`), {
    method: "GET",
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new ApiError(`HTTP ${response.status}`, response.status);
  }

  return {
    blob: await response.blob(),
    filename: getFilenameFromHeaders(response.headers),
  };
}
