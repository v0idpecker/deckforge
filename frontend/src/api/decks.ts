import type {
  DeckTaskCreateRequest,
  DeckTaskCreateResponse,
  DeckTaskItemStatus,
  DeckTaskStatusResponse,
} from "../types/decks";
import { ApiError, buildApiUrl, request } from "./client";

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
  });

  if (!response.ok) {
    throw new ApiError(`HTTP ${response.status}`, response.status);
  }

  return {
    blob: await response.blob(),
    filename: getFilenameFromHeaders(response.headers),
  };
}
