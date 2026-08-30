import type { AlignmentReport, MasterProfile } from "./types";

const API_BASE_URL =
  (import.meta.env["VITE_API_BASE_URL"] as string | undefined)?.replace(/\/$/, "") ??
  "http://localhost:8000";

export class ApiError extends Error {}

async function post<T>(path: string, form: FormData): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { method: "POST", body: form });
  } catch {
    throw new ApiError(
      `Could not reach the DocAlign analysis service at ${API_BASE_URL}. Start the FastAPI backend and try again.`,
    );
  }
  if (!response.ok) {
    const text = await response.text().catch(() => "");
    throw new ApiError(text || `Analysis failed with status ${response.status}.`);
  }
  return (await response.json()) as T;
}

export function analyzeDocuments(master: File, child: File): Promise<AlignmentReport> {
  const form = new FormData();
  form.append("master", master);
  form.append("child", child);
  return post<AlignmentReport>("/api/analyze", form);
}

export function analyzeMaster(master: File): Promise<MasterProfile> {
  const form = new FormData();
  form.append("master", master);
  return post<MasterProfile>("/api/analyze/master", form);
}

export { API_BASE_URL };
