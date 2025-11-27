"use client";

import { useState, useRef, useEffect } from "react";
import { CameraFeed } from "@/components/test/CameraFeed";
import { ComparisonView } from "@/components/test/ComparisonView";
import { HazardAlert } from "@/components/test/HazardAlert";
import {
  NarrationPanel,
  NarrationButton,
  type NarrationPanelRef,
} from "@/components/test/NarrationPanel";
import { StatusPanel } from "@/components/test/StatusPanel";
import { DebugPanel } from "@/components/test/DebugPanel";
import { useWebSocket } from "@/hooks/useWebSocket";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ListChecks } from "lucide-react";

export default function TestPage() {
  const { detections, isConnected, error, connect, disconnect, sendFrame } =
    useWebSocket();
  const [currentFrame, setCurrentFrame] = useState<string | null>(null);
  const narrationPanelRef = useRef<NarrationPanelRef>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

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
    <div className="min-h-screen bg-background text-foreground container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            System Diagnostic
          </h1>
          <p className="text-muted-foreground mt-1">
            Real-time verification and testing interface.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge
            variant={isConnected ? "default" : "destructive"}
            className="h-6"
          >
            {isConnected ? "System Online" : "Disconnected"}
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Main Camera Feed Area */}
        <div className="xl:col-span-2 space-y-6">
          <div className="grid gap-6">
            <CameraFeed
              mode="compact"
              videoRef={videoRef}
              onFrameCapture={handleFrameCapture}
              isWebSocketConnected={isConnected}
              onConnect={connect}
              onDisconnect={disconnect}
              onSendFrame={sendFrame}
            />

            <ComparisonView
              originalVideoRef={videoRef}
              annotatedFrame={detections?.annotated_frame}
              detections={detections?.detections || []}
              hazards={detections?.hazards || []}
            />
          </div>

          <HazardAlert hazards={detections?.hazards || []} />

          <Card className="border-border shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg font-semibold flex items-center gap-2">
                <ListChecks className="w-5 h-5" />
                Instructions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ol className="list-decimal list-inside space-y-1 text-sm text-muted-foreground">
                <li>Start the camera feed to initialize the video stream.</li>
                <li>Grant browser permissions if prompted.</li>
                <li>Observe real-time object detection and hazard alerts.</li>
                <li>
                  Use &quot;Generate Narration&quot; to test AI scene
                  understanding.
                </li>
              </ol>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar Controls & Stats */}
        <div className="space-y-6">
          <StatusPanel detectionCount={detections?.detections?.length || 0} />

          <NarrationPanel ref={narrationPanelRef} />

          <Card className="p-4 border-border shadow-sm">
            <NarrationButton
              onGenerate={handleGenerateNarration}
              disabled={!currentFrame}
            />
          </Card>

          <DebugPanel
            isConnected={isConnected}
            detections={detections}
            error={error || null}
          />

          <Card className="border-border shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">
                Session Statistics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Objects</span>
                  <span className="font-mono font-medium">
                    {detections?.detections.length || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Hazards</span>
                  <span className="font-mono font-medium text-destructive">
                    {detections?.hazards.length || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">
                    Frame ID
                  </span>
                  <span className="font-mono font-medium">
                    {detections?.frame_id || "-"}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
