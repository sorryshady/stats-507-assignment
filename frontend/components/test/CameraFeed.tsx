"use client";

import { useEffect, useRef, useState } from "react";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCamera } from "@/hooks/useCamera";
import { Button } from "@/components/ui/button";
import {
  Power,
  PowerOff,
  Info,
  AlertTriangle,
  CheckCircle2,
} from "lucide-react";

interface CameraFeedProps {
  onFrameCapture?: (frameBase64: string) => void;
  onVideoDimensionsChange?: (width: number, height: number) => void;
  videoRef?: React.Ref<HTMLVideoElement | null>;
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
  mode = "default",
}: CameraFeedProps) {
  const {
    videoRef: internalVideoRef,
    isActive,
    hasPermission,
    error,
    startCamera,
    stopCamera,
    captureFrame,
  } = useCamera();

  const [showDisclaimer, setShowDisclaimer] = useState(false);

  const handleStartClick = () => {
    setShowDisclaimer(true);
  };

  const handleConfirmStart = () => {
    setShowDisclaimer(false);
    startCamera();
  };

  const handleCancelStart = () => {
    setShowDisclaimer(false);
  };

  // Callback ref to set both internal and external refs
  const setVideoRef = (node: HTMLVideoElement | null) => {
    // Always set internal ref (used by useCamera hook)
    (
      internalVideoRef as React.MutableRefObject<HTMLVideoElement | null>
    ).current = node;
    // Also set external ref if provided (used by ComparisonView)
    if (externalVideoRef) {
      if (typeof externalVideoRef === "function") {
        externalVideoRef(node);
      } else {
        const mutableRef =
          externalVideoRef as React.MutableRefObject<HTMLVideoElement | null>;
        // eslint-disable-next-line
        mutableRef.current = node;
      }
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

        if (
          internalVideoRef.current &&
          internalVideoRef.current.readyState >= 2
        ) {
          // Capture and send frames at ~20 FPS (reduced for performance)
          frameIntervalRef.current = setInterval(() => {
            // Double check active state inside interval
            if (!isActive || !isWebSocketConnected) {
              if (frameIntervalRef.current)
                clearInterval(frameIntervalRef.current);
              return;
            }

            const frame = captureFrame();
            if (frame) {
              onSendFrame(frame);
              onFrameCapture?.(frame);
            }
          }, 50); // ~20 FPS - adjust as needed
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
  }, [
    isActive,
    isWebSocketConnected,
    captureFrame,
    onSendFrame,
    onFrameCapture,
    internalVideoRef,
  ]);

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
      <div
        className={`relative bg-muted/20 ${mode === "compact" ? "h-0" : "aspect-video"}`}
      >
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
          className={`w-full h-full object-cover ${!isActive || mode === "compact" ? "hidden" : ""}`}
          style={{ backgroundColor: "black" }}
          onLoadedMetadata={(e) =>
            onVideoDimensionsChange?.(
              e.currentTarget.videoWidth,
              e.currentTarget.videoHeight,
            )
          }
        />

        {isActive && mode !== "compact" && (
          <div className="absolute top-3 left-3 flex gap-2">
            <div
              className={`w-2 h-2 rounded-full mt-1.5 ${isWebSocketConnected ? "bg-green-500" : "bg-red-500"}`}
            />
          </div>
        )}
      </div>

      <div className="p-4 flex justify-between items-center bg-card">
        <div className="flex items-center gap-3">
          <div
            className={`w-2 h-2 rounded-full ${isActive ? "bg-green-500" : "bg-muted-foreground/30"}`}
          />
          <span className="text-sm font-medium">
            {isActive ? "Camera Active" : "Camera Standby"}
          </span>
        </div>
        <div>
          {!isActive ? (
            <Button
              onClick={handleStartClick}
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

      {showDisclaimer && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <Card className="w-full max-w-lg shadow-2xl border-border bg-card">
            <div className="p-6 space-y-6">
              <div className="flex items-center gap-3 text-amber-500">
                <AlertTriangle className="w-8 h-8" />
                <h3 className="text-lg font-semibold text-foreground">
                  Camera Limitations & Testing Guide
                </h3>
              </div>

              <div className="space-y-4 text-sm text-muted-foreground leading-relaxed">
                <div className="bg-muted/50 p-3 rounded-lg border border-border/50">
                  <p className="font-medium text-foreground mb-1 flex items-center gap-2">
                    <Info className="w-4 h-4" />
                    System Limitations
                  </p>
                  <p>
                    <strong>Webcam:</strong> Standard webcams have a narrow FOV and limited depth perception. Fast movements may cause ghosting.
                  </p>
                  <p className="mt-2">
                    <strong>Audio:</strong> Narration uses your browser&apos;s built-in text-to-speech engine. Voice quality varies by device/browser.
                  </p>
                  <p className="mt-2">
                    <strong>Performance:</strong> Running AI vision models in real-time requires significant processing power. You may experience latency.
                  </p>
                </div>

                <div className="space-y-2">
                  <p className="font-medium text-foreground">
                    Recommended Testing:
                  </p>
                  <ul className="space-y-2">
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 mt-0.5 text-green-500 shrink-0" />
                      <span>
                        Hold an object (phone, bottle) and move it{" "}
                        <strong>slowly</strong>.
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 mt-0.5 text-green-500 shrink-0" />
                      <span>
                        Walk into the frame from a distance (2-3 meters).
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 mt-0.5 text-green-500 shrink-0" />
                      <span>Avoid rapid hand waving close to the camera.</span>
                    </li>
                  </ul>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <Button variant="outline" onClick={handleCancelStart}>
                  Cancel
                </Button>
                <Button onClick={handleConfirmStart} className="gap-2">
                  <Power className="w-4 h-4" />
                  Understood, Start Feed
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </Card>
  );
}
