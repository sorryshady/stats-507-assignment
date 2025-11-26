"use client";

import { useEffect, useRef } from "react";
import type { Detection, Hazard } from "@/lib/types";

interface TrackingOverlayProps {
  detections: Detection[];
  hazards: Hazard[];
  videoWidth: number;
  videoHeight: number;
}

export function TrackingOverlay({
  detections,
  hazards,
  videoWidth,
  videoHeight,
}: TrackingOverlayProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Get container dimensions
    const containerRect = container.getBoundingClientRect();
    const scaleX = containerRect.width / videoWidth;
    const scaleY = containerRect.height / videoHeight;

    // Set canvas size to match container
    canvas.width = containerRect.width;
    canvas.height = containerRect.height;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw detections
    detections.forEach((det) => {
      const [x1, y1, x2, y2] = det.box;
      
      // Scale coordinates to match displayed size
      const scaledX1 = x1 * scaleX;
      const scaledY1 = y1 * scaleY;
      const scaledX2 = x2 * scaleX;
      const scaledY2 = y2 * scaleY;
      
      // Draw bounding box
      ctx.strokeStyle = det.confidence > 0.5 ? "#3b82f6" : "#94a3b8";
      ctx.lineWidth = 2;
      ctx.strokeRect(scaledX1, scaledY1, scaledX2 - scaledX1, scaledY2 - scaledY1);

      // Draw label
      ctx.fillStyle = det.confidence > 0.5 ? "#3b82f6" : "#94a3b8";
      ctx.font = "14px sans-serif";
      const label = `${det.class_name} (${(det.confidence * 100).toFixed(0)}%)`;
      const textMetrics = ctx.measureText(label);
      ctx.fillRect(scaledX1, scaledY1 - 20, textMetrics.width + 8, 20);
      
      ctx.fillStyle = "white";
      ctx.fillText(label, scaledX1 + 4, scaledY1 - 5);

      // Draw center point
      const centerX = det.center[0] * scaleX;
      const centerY = det.center[1] * scaleY;
      ctx.fillStyle = "#3b82f6";
      ctx.beginPath();
      ctx.arc(centerX, centerY, 4, 0, 2 * Math.PI);
      ctx.fill();
    });

    // Draw hazards with red boxes
    hazards.forEach((hazard) => {
      const [x1, y1, x2, y2] = hazard.box;
      
      // Scale coordinates
      const scaledX1 = x1 * scaleX;
      const scaledY1 = y1 * scaleY;
      const scaledX2 = x2 * scaleX;
      const scaledY2 = y2 * scaleY;
      
      // Draw red bounding box
      ctx.strokeStyle = hazard.priority === "high" ? "#ef4444" : "#f59e0b";
      ctx.lineWidth = 3;
      ctx.strokeRect(scaledX1, scaledY1, scaledX2 - scaledX1, scaledY2 - scaledY1);

      // Draw hazard label
      ctx.fillStyle = hazard.priority === "high" ? "#ef4444" : "#f59e0b";
      ctx.font = "bold 16px sans-serif";
      const label = `⚠️ ${hazard.class_name} - ${hazard.priority.toUpperCase()}`;
      const textMetrics = ctx.measureText(label);
      ctx.fillRect(scaledX1, scaledY1 - 25, textMetrics.width + 8, 25);
      
      ctx.fillStyle = "white";
      ctx.fillText(label, scaledX1 + 4, scaledY1 - 8);
    });
  }, [detections, hazards, videoWidth, videoHeight]);

  return (
    <div ref={containerRef} className="absolute inset-0 w-full h-full pointer-events-none">
      <canvas
        ref={canvasRef}
        className="absolute top-0 left-0 w-full h-full"
      />
    </div>
  );
}

