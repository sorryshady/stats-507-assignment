"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import type { DetectionResponse } from "@/lib/types";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/api/ws/camera";

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [detections, setDetections] = useState<DetectionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    try {
      console.log("Attempting to connect to WebSocket:", WS_URL);
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        console.log("✅ WebSocket connected successfully to", WS_URL);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Handle different message types
          if (data.type === "frame_result") {
            // Convert backend response format to frontend format
            const detectionResponse: DetectionResponse = {
              detections: data.detections || [],
              hazards: data.hazards || [],
              frame_id: data.frame_id || 0,
              timestamp: data.timestamp || Date.now() / 1000,
              annotated_frame: data.annotated_frame || undefined,
            };
            setDetections(detectionResponse);
            // Debug log (can be removed later)
            if (detectionResponse.detections.length > 0) {
              console.log(`Received ${detectionResponse.detections.length} detections`, detectionResponse.detections);
            }
          } else if (data.type === "error") {
            console.error("Server error:", data.message);
            setError(data.message || "Server error");
          } else if (data.type === "pong") {
            // Heartbeat response, ignore
            return;
          } else {
            console.warn("Unknown message type:", data.type, data);
          }
        } catch (err) {
          console.error("Failed to parse WebSocket message:", err);
          setError("Failed to parse server response");
        }
      };

      ws.onerror = (err) => {
        console.error("❌ WebSocket error:", err);
        console.error("WebSocket URL:", WS_URL);
        setError(`WebSocket connection error. Is backend running on ${WS_URL}?`);
        setIsConnected(false);
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        console.log("⚠️ WebSocket disconnected", {
          code: event.code,
          reason: event.reason,
          wasClean: event.wasClean,
        });
        
        // Auto-reconnect after 3 seconds if not a clean close
        if (event.code !== 1000) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log("Attempting to reconnect WebSocket...");
            connect();
          }, 3000);
        }
      };
    } catch (err) {
      console.error("Failed to create WebSocket:", err);
      setError("Failed to connect to server");
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const sendFrame = useCallback((frameBase64: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const message = {
        type: "frame",
        data: frameBase64,
        timestamp: Date.now() / 1000, // Current timestamp in seconds
      };
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn("WebSocket not connected, cannot send frame. State:", wsRef.current?.readyState);
    }
  }, []);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    detections,
    error,
    connect,
    disconnect,
    sendFrame,
  };
}

