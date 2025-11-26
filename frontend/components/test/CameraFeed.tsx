"use client";

import { useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCamera } from "@/hooks/useCamera";
import { Button } from "@/components/ui/button";
import { Power, PowerOff } from "lucide-react";

interface CameraFeedProps {
  onFrameCapture?: (frameBase64: string) => void;
  onVideoDimensionsChange?: (width: number, height: number) => void;
  videoRef?: React.RefObject<HTMLVideoElement>;
  isWebSocketConnected: boolean;
  onConnect: () => void;
  onDisconnect: () => void;
  onSendFrame: (frame: string) => void;
  mode?: "default" | "compact";
}

export function CameraFeed({ 
  onFrameCapture, 
  onVideoDimensionsChange, 
  videoRef: externalVideoRef,
  isWebSocketConnected,
  onConnect,
  onDisconnect,
  onSendFrame,
  mode = "default"
}: CameraFeedProps) {
  const { videoRef: internalVideoRef, isActive, hasPermission, error, startCamera, stopCamera, captureFrame } = useCamera();
  
  // Callback ref to set both internal and external refs
  const setVideoRef = (node: HTMLVideoElement | null) => {
    // Always set internal ref (used by useCamera hook)
    (internalVideoRef as React.MutableRefObject<HTMLVideoElement | null>).current = node;
    // Also set external ref if provided (used by ComparisonView)
    if (externalVideoRef) {
      (externalVideoRef as React.MutableRefObject<HTMLVideoElement | null>).current = node;
    }
  };
  
  const frameIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Handle frame capture
  useEffect(() => {
    // Clear existing interval first
    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current);
      frameIntervalRef.current = null;
    }

    if (isActive && isWebSocketConnected) {
      // Wait a bit for video to be ready before starting frame capture
      const startFrameCapture = () => {
        if (!isActive || !isWebSocketConnected) return;

        if (internalVideoRef.current && internalVideoRef.current.readyState >= 2) {
          // Capture and send frames at ~10 FPS (reduced for performance)
          frameIntervalRef.current = setInterval(() => {
            // Double check active state inside interval
            if (!isActive || !isWebSocketConnected) {
              if (frameIntervalRef.current) clearInterval(frameIntervalRef.current);
              return;
            }

            const frame = captureFrame();
            if (frame) {
              onSendFrame(frame);
              onFrameCapture?.(frame);
            }
          }, 100); // ~10 FPS - adjust as needed
        } else {
          // Retry after a short delay
          setTimeout(startFrameCapture, 200);
        }
      };
      
      startFrameCapture();
    }

    return () => {
      if (frameIntervalRef.current) {
        clearInterval(frameIntervalRef.current);
        frameIntervalRef.current = null;
      }
    };
  }, [isActive, isWebSocketConnected, captureFrame, onSendFrame, onFrameCapture, internalVideoRef]);

  // Handle WebSocket connection based on camera state
  useEffect(() => {
    if (isActive && !isWebSocketConnected) {
      onConnect();
    } else if (!isActive && isWebSocketConnected) {
      onDisconnect();
    }
  }, [isActive, isWebSocketConnected, onConnect, onDisconnect]);

  return (
    <Card className="overflow-hidden border-border shadow-sm">
      <div className={`relative bg-muted/20 ${mode === "compact" ? "h-0" : "aspect-video"}`}>
        {!hasPermission && hasPermission !== null && mode !== "compact" && (
          <div className="absolute inset-0 flex items-center justify-center text-muted-foreground">
            <div className="text-center space-y-2">
              <p className="font-medium">Camera permission denied</p>
              <p className="text-xs">{error}</p>
            </div>
          </div>
        )}
        
        {hasPermission === null && mode !== "compact" && (
          <div className="absolute inset-0 flex items-center justify-center">
            <Skeleton className="w-full h-full" />
          </div>
        )}

        <video
          ref={setVideoRef}
          autoPlay={isActive}
          playsInline
          muted
          className={`w-full h-full object-cover ${(!isActive || mode === "compact") ? "hidden" : ""}`}
          style={{ backgroundColor: "black" }}
          onLoadedMetadata={(e) => onVideoDimensionsChange?.(e.currentTarget.videoWidth, e.currentTarget.videoHeight)}
        />

        {isActive && mode !== "compact" && (
          <div className="absolute top-3 left-3 flex gap-2">
             <div className={`w-2 h-2 rounded-full mt-1.5 ${isWebSocketConnected ? "bg-green-500" : "bg-red-500"}`} />
          </div>
        )}
      </div>

      <div className="p-4 flex justify-between items-center bg-card">
        <div className="flex items-center gap-3">
           <div className={`w-2 h-2 rounded-full ${isActive ? "bg-green-500" : "bg-muted-foreground/30"}`} />
           <span className="text-sm font-medium">
            {isActive ? "Camera Active" : "Camera Standby"}
           </span>
        </div>
        <div>
          {!isActive ? (
            <Button
              onClick={startCamera}
              variant="default"
              size="sm"
              className="gap-2"
            >
              <Power className="w-4 h-4" /> Start Feed
            </Button>
          ) : (
            <Button
              onClick={stopCamera}
              variant="destructive"
              size="sm"
              className="gap-2"
            >
              <PowerOff className="w-4 h-4" /> Stop Feed
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
}
