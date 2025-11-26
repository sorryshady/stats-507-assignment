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
      
      // Draw minimal corners instead of full box for cleaner look
      const cornerLen = 15;
      const color = det.confidence > 0.5 ? "rgba(59, 130, 246, 0.9)" : "rgba(148, 163, 184, 0.8)";
      
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      
      // Top-left
      ctx.beginPath();
      ctx.moveTo(scaledX1, scaledY1 + cornerLen);
      ctx.lineTo(scaledX1, scaledY1);
      ctx.lineTo(scaledX1 + cornerLen, scaledY1);
      ctx.stroke();

      // Top-right
      ctx.beginPath();
      ctx.moveTo(scaledX2 - cornerLen, scaledY1);
      ctx.lineTo(scaledX2, scaledY1);
      ctx.lineTo(scaledX2, scaledY1 + cornerLen);
      ctx.stroke();

      // Bottom-left
      ctx.beginPath();
      ctx.moveTo(scaledX1, scaledY2 - cornerLen);
      ctx.lineTo(scaledX1, scaledY2);
      ctx.lineTo(scaledX1 + cornerLen, scaledY2);
      ctx.stroke();

      // Bottom-right
      ctx.beginPath();
      ctx.moveTo(scaledX2 - cornerLen, scaledY2);
      ctx.lineTo(scaledX2, scaledY2);
      ctx.lineTo(scaledX2, scaledY2 - cornerLen);
      ctx.stroke();

      // Minimal label
      ctx.fillStyle = color;
      ctx.font = "500 12px Inter, sans-serif";
      const label = `${det.class_name}`;
      const textMetrics = ctx.measureText(label);
      
      // Label background
      ctx.fillRect(scaledX1, scaledY1 - 20, textMetrics.width + 8, 20);
      
      ctx.fillStyle = "white";
      ctx.fillText(label, scaledX1 + 4, scaledY1 - 6);
    });

    // Draw hazards with distinct style
    hazards.forEach((hazard) => {
      const [x1, y1, x2, y2] = hazard.box;
      
      // Scale coordinates
      const scaledX1 = x1 * scaleX;
      const scaledY1 = y1 * scaleY;
      const scaledX2 = x2 * scaleX;
      const scaledY2 = y2 * scaleY;
      
      const color = hazard.priority === "high" ? "rgba(239, 68, 68, 0.9)" : "rgba(245, 158, 11, 0.9)";
      
      // Dashed box for hazards
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      ctx.strokeRect(scaledX1, scaledY1, scaledX2 - scaledX1, scaledY2 - scaledY1);
      ctx.setLineDash([]); // Reset

      // Warning icon / Label
      ctx.fillStyle = color;
      ctx.font = "bold 12px Inter, sans-serif";
      const label = `⚠️ ${hazard.class_name}`;
      const textMetrics = ctx.measureText(label);
      
      ctx.fillRect(scaledX1, scaledY1 - 24, textMetrics.width + 12, 24);
      
      ctx.fillStyle = "white";
      ctx.fillText(label, scaledX1 + 6, scaledY1 - 7);
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
