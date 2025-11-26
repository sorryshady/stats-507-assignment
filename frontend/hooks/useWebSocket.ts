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
  const lastFrameIdRef = useRef<number>(-1);

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
            // Create a new object to ensure React detects the change
            const detectionResponse: DetectionResponse = {
              detections: Array.isArray(data.detections) ? [...data.detections] : [],
              hazards: Array.isArray(data.hazards) ? [...data.hazards] : [],
              frame_id: data.frame_id || 0,
              timestamp: data.timestamp || Date.now() / 1000,
              annotated_frame: data.annotated_frame || undefined,
            };
            
            // Always update state - React will batch rapid updates
            // Use frame_id to track, but always create new object reference
            const shouldUpdate = detectionResponse.frame_id !== lastFrameIdRef.current;
            lastFrameIdRef.current = detectionResponse.frame_id;
            
            if (shouldUpdate) {
              console.log("useWebSocket: Setting detections state", {
                detectionsArray: detectionResponse.detections,
                detectionsCount: detectionResponse.detections.length,
                frameId: detectionResponse.frame_id,
                hasAnnotatedFrame: !!detectionResponse.annotated_frame,
                annotatedFrameLength: detectionResponse.annotated_frame?.length || 0,
              });
            }
            
            // Always create a completely new object to ensure React detects the change
            // Use timestamp to force React to see it as a new value
            setDetections({
              ...detectionResponse,
              detections: [...detectionResponse.detections],
              hazards: [...detectionResponse.hazards],
              _updateTime: Date.now(), // Force React to see as new object
            });
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
        
        // Auto-reconnect after 3 seconds if not a clean close (1000) or no status (1005)
        // Only reconnect if it was an unexpected disconnect (not 1000 or 1005)
        if (event.code !== 1000 && event.code !== 1005) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log("Attempting to reconnect WebSocket...");
            connect();
          }, 3000);
        } else {
          console.log("WebSocket closed normally, not reconnecting");
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
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      // Close with code 1000 (normal closure) to prevent auto-reconnect
      wsRef.current.close(1000, "Client disconnect");
      wsRef.current = null;
    }
    setIsConnected(false);
    // Clear detections and reset frame tracking when disconnecting
    setDetections(null);
    lastFrameIdRef.current = -1;
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

