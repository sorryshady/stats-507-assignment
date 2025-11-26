"use client";

import { useState, useRef, useEffect } from "react";
import { CameraFeed } from "@/components/test/CameraFeed";
import { TrackingOverlay } from "@/components/test/TrackingOverlay";
import { ComparisonView } from "@/components/test/ComparisonView";
import { HazardAlert } from "@/components/test/HazardAlert";
import { NarrationPanel, NarrationButton, type NarrationPanelRef } from "@/components/test/NarrationPanel";
import { StatusPanel } from "@/components/test/StatusPanel";
import { DebugPanel } from "@/components/test/DebugPanel";
import { useWebSocket } from "@/hooks/useWebSocket";
import { Card } from "@/components/ui/card";

export default function TestPage() {
  const { detections, isConnected, error, connect, disconnect, sendFrame } = useWebSocket();
  const [currentFrame, setCurrentFrame] = useState<string | null>(null);
  const [videoDimensions, setVideoDimensions] = useState({ width: 1280, height: 720 });
  const narrationPanelRef = useRef<NarrationPanelRef>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  
  // Debug: Log when detections change
  useEffect(() => {
    const count = detections?.detections?.length || 0;
    console.log("TestPage: detections state changed", {
      detections: detections,
      detectionsIsNull: detections === null,
      detectionsArray: detections?.detections,
      detectionsCount: count,
      frameId: detections?.frame_id,
      hasAnnotatedFrame: !!detections?.annotated_frame,
      annotatedFrameLength: detections?.annotated_frame?.length || 0,
    });
    
    // Force a re-render check
    if (count > 0) {
      console.log("✅ TestPage: Should show", count, "detections in UI");
    }
  }, [detections]);
  
  // Debug: Log connection status changes
  useEffect(() => {
    console.log("WebSocket connection status changed:", isConnected);
  }, [isConnected]);

  const handleFrameCapture = (frameBase64: string) => {
    setCurrentFrame(frameBase64);
  };

  const handleGenerateNarration = async () => {
    if (currentFrame && narrationPanelRef.current) {
      narrationPanelRef.current.generateNarration(currentFrame);
    } else {
      alert("Please start the camera first to capture a frame");
    }
  };

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Interactive Test Page</h1>
        <p className="text-muted-foreground">
          Grant camera permission to experience real-time object detection and AI narration
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Camera Feed */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Camera Controls (Compact Mode) */}
          <CameraFeed 
            mode="compact"
            videoRef={videoRef}
            onFrameCapture={handleFrameCapture}
            onVideoDimensionsChange={(w, h) => setVideoDimensions({ width: w, height: h })}
            isWebSocketConnected={isConnected}
            onConnect={connect}
            onDisconnect={disconnect}
            onSendFrame={sendFrame}
          />

          {/* Comparison View */}
          <ComparisonView
            originalVideoRef={videoRef}
            annotatedFrame={detections?.annotated_frame}
            detections={detections?.detections || []}
            hazards={detections?.hazards || []}
          />

          <HazardAlert hazards={detections?.hazards || []} />

          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">How It Works</h2>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>1. Click "Start Camera" to begin</li>
              <li>2. Grant camera permission when prompted</li>
              <li>3. Objects will be detected and tracked in real-time</li>
              <li>4. Hazards will be highlighted with alerts</li>
              <li>5. Click "Generate Narration" for AI-powered scene descriptions</li>
            </ul>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <StatusPanel detectionCount={detections?.detections?.length || 0} />

          <DebugPanel 
            isConnected={isConnected}
            detections={detections}
            error={error || null}
          />

          <NarrationPanel ref={narrationPanelRef} />

          <Card className="p-4">
            <NarrationButton 
              onGenerate={handleGenerateNarration} 
              disabled={!currentFrame}
            />
          </Card>

          <Card className="p-4">
            <h3 className="font-semibold mb-2">Detection Stats</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Objects Detected:</span>
                <span className="font-medium">{detections?.detections.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Hazards:</span>
                <span className="font-medium text-destructive">
                  {detections?.hazards.length || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Frame ID:</span>
                <span className="font-medium">{detections?.frame_id || "-"}</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

