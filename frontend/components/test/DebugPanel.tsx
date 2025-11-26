"use client";

import { useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useWebSocket } from "@/hooks/useWebSocket";

export function DebugPanel() {
  const { isConnected, detections, error } = useWebSocket();
  
  // Debug: Log when detections change
  useEffect(() => {
    if (detections) {
      console.log("DebugPanel: Detections updated", {
        count: detections.detections.length,
        frameId: detections.frame_id,
      });
    }
  }, [detections]);

  return (
    <Card className="bg-muted/50">
      <CardHeader>
        <CardTitle className="text-sm">Debug Info</CardTitle>
        <CardDescription className="text-xs">WebSocket connection status</CardDescription>
      </CardHeader>
      <CardContent className="space-y-2 text-xs">
        <div className="flex justify-between">
          <span>Connection:</span>
          <Badge variant={isConnected ? "default" : "destructive"}>
            {isConnected ? "Connected" : "Disconnected"}
          </Badge>
        </div>
        {error && (
          <div className="text-destructive">
            Error: {error}
          </div>
        )}
        {detections && (
          <>
            <div className="flex justify-between">
              <span>Frame ID:</span>
              <span>{detections.frame_id}</span>
            </div>
            <div className="flex justify-between">
              <span>Detections:</span>
              <span>{detections.detections.length}</span>
            </div>
            <div className="flex justify-between">
              <span>Hazards:</span>
              <span>{detections.hazards.length}</span>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}

