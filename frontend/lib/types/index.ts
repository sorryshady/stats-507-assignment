// API Response Types
export interface Detection {
  track_id: number;
  class_name: string;
  confidence: number;
  box: [number, number, number, number]; // [x1, y1, x2, y2]
  center: [number, number];
  area: number;
}

export interface Hazard {
  object_id: number;
  class_name: string;
  priority: "high" | "medium" | "low";
  reason: string;
  box: [number, number, number, number];
}

export interface DetectionResponse {
  detections: Detection[];
  hazards: Hazard[];
  frame_id: number;
  timestamp: number;
  annotated_frame?: string; // Base64 encoded annotated frame from backend
}

export interface NarrationResponse {
  narration: string;
  scene_description: string;
  object_movements: string[];
  processing_time_ms: number;
}

export interface StatusResponse {
  initialized: boolean;
  models: {
    yolo: string;
    blip: string;
    ollama: string;
  };
  gpu: {
    available: boolean;
    type: string;
  };
}

