const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  })

  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}`

    try {
      const payload = (await response.json()) as { detail?: string }
      if (payload.detail) {
        errorMessage = payload.detail
      }
    } catch {
      // Ignore json parsing errors for non-json responses.
    }

    throw new ApiError(errorMessage, response.status)
  }

  return (await response.json()) as T
}

export function buildApiUrl(path: string): string {
  return `${API_BASE_URL}${path}`
}
