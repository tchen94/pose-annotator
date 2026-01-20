const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface SaveAnnotationsPayload {
  frame_set_id: string;
  video_id: string;
  orig_width: number;
  orig_height: number;
  render_width: number;
  render_height: number;
  annotations: any;
  last_frame_annotated: number;
  token?: string;
}

export const fetchSessions = async (token?: string) => {
  const url = token
    ? `${API_URL}/annotations/sessions?token=${token}`
    : `${API_URL}/annotations/sessions`;

  const response = await fetch(url);
  if (!response.ok) throw new Error("Failed to fetch sessions");

  const data = await response.json();
  return data.sessions;
};

export const loadSession = async (frameSetId: string, token?: string) => {
  const url = token
    ? `${API_URL}/annotations/load/${frameSetId}?token=${token}`
    : `${API_URL}/annotations/load/${frameSetId}`;

  const response = await fetch(url);
  if (!response.ok) throw new Error("Failed to load session");

  return response.json();
};

export const saveAnnotations = async (payload: SaveAnnotationsPayload) => {
  const response = await fetch(`${API_URL}/annotations/save`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) throw new Error("Failed to save annotations");
  return response.json();
};
