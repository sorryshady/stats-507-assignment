"use client";

import { useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCamera } from "@/hooks/useCamera";
import { useWebSocket } from "@/hooks/useWebSocket";

interface CameraFeedProps {
  onFrameCapture?: (frameBase64: string) => void;
  onVideoDimensionsChange?: (width: number, height: number) => void;
  videoRef?: React.RefObject<HTMLVideoElement>;
}

export function CameraFeed({ onFrameCapture, onVideoDimensionsChange, videoRef: externalVideoRef }: CameraFeedProps) {
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
  const { isConnected, connect, disconnect, sendFrame } = useWebSocket();
  const frameIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isActive && isConnected) {
      // Wait a bit for video to be ready before starting frame capture
      const startFrameCapture = () => {
        if (internalVideoRef.current && internalVideoRef.current.readyState >= 2) {
          // Capture and send frames at ~10 FPS (reduced for performance)
          frameIntervalRef.current = setInterval(() => {
            const frame = captureFrame();
            if (frame) {
              sendFrame(frame);
              onFrameCapture?.(frame);
            } else {
              // Only log if video exists but isn't ready
              if (internalVideoRef.current && internalVideoRef.current.readyState < 2) {
                console.debug("Frame capture skipped. Video readyState:", internalVideoRef.current.readyState);
              }
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
      }
    };
  }, [isActive, isConnected, captureFrame, sendFrame, onFrameCapture, internalVideoRef]);

  useEffect(() => {
    if (isActive) {
      console.log("Camera active, connecting WebSocket...");
      connect();
    } else {
      console.log("Camera inactive, disconnecting WebSocket...");
      disconnect();
    }
  }, [isActive, connect, disconnect]);

  return (
    <Card className="relative overflow-hidden">
      <div className="relative aspect-video bg-black">
        {!hasPermission && hasPermission !== null && (
          <div className="absolute inset-0 flex items-center justify-center text-white">
            <div className="text-center space-y-4">
              <p className="text-lg">Camera permission denied</p>
              <p className="text-sm text-gray-400">{error}</p>
            </div>
          </div>
        )}
        
        {hasPermission === null && (
          <div className="absolute inset-0 flex items-center justify-center">
            <Skeleton className="w-full h-full" />
          </div>
        )}

        <video
          ref={setVideoRef}
          autoPlay
          playsInline
          muted
          className={`w-full h-full object-cover ${!isActive ? "hidden" : ""}`}
          style={{ backgroundColor: "black" }}
          onLoadedMetadata={(e) => {
              const video = e.currentTarget;
              console.log("✅ Video metadata loaded:", {
                width: video.videoWidth,
                height: video.videoHeight,
                readyState: video.readyState,
                srcObject: video.srcObject ? "present" : "null",
              });
              onVideoDimensionsChange?.(video.videoWidth, video.videoHeight);
            }}
            onLoadedData={(e) => {
              const video = e.currentTarget;
              console.log("✅ Video data loaded:", {
                readyState: video.readyState,
                videoWidth: video.videoWidth,
                videoHeight: video.videoHeight,
              });
            }}
            onCanPlay={(e) => {
              console.log("✅ Video can play:", {
                readyState: e.currentTarget.readyState,
              });
            }}
            onPlay={() => {
              console.log("✅ Video started playing");
            }}
            onError={(e) => {
              const video = e.currentTarget;
              console.error("❌ Video element error:", {
                error: video.error,
                errorCode: video.error?.code,
                errorMessage: video.error?.message,
              });
            }}
          />

        {isActive && (
          <div className="absolute top-4 left-4 flex gap-2">
            <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
              isConnected ? "bg-green-500 text-white" : "bg-red-500 text-white"
            }`}>
              {isConnected ? "Connected" : "Disconnected"}
            </div>
          </div>
        )}
      </div>

      <div className="p-4 flex justify-between items-center">
        <div className="text-sm text-muted-foreground">
          {isActive ? "Camera active" : "Camera inactive"}
        </div>
        <div className="flex gap-2">
          {!isActive ? (
            <button
              onClick={startCamera}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
            >
              Start Camera
            </button>
          ) : (
            <button
              onClick={stopCamera}
              className="px-4 py-2 bg-destructive text-destructive-foreground rounded-md hover:bg-destructive/90 transition-colors"
            >
              Stop Camera
            </button>
          )}
        </div>
      </div>
    </Card>
  );
}

