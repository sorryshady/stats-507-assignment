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
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { ListChecks, AlertTriangle, Github } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function TestPage() {
  // Hide test page in production
  if (process.env.NODE_ENV === "production") {
    return (
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-2xl mx-auto text-center space-y-6">
          <Alert variant="warning">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Test Page Unavailable</AlertTitle>
            <AlertDescription>
              The interactive test page is only available in development mode for performance reasons.
              <br />
              <br />
              To use the test page, please run the application locally:
            </AlertDescription>
          </Alert>
          <Card>
            <CardHeader>
              <CardTitle>Run Locally</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <ol className="list-decimal list-inside space-y-2 text-left text-muted-foreground">
                <li>Clone the repository from GitHub</li>
                <li>Set up the backend (see README.md)</li>
                <li>Run <code className="bg-muted px-2 py-1 rounded">npm run dev</code> in the frontend directory</li>
                <li>The test page will be available at <code className="bg-muted px-2 py-1 rounded">/test</code></li>
              </ol>
              <Button asChild className="w-full">
                <a
                  href="https://github.com/sorryshady/stats-507-assignment"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Github className="w-4 h-4 mr-2" />
                  View Source Code
                </a>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }
  const { detections, isConnected, error, connect, disconnect, sendFrame } =
    useWebSocket();
  const [currentFrame, setCurrentFrame] = useState<string | null>(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const narrationPanelRef = useRef<NarrationPanelRef>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Debug: Log connection status changes
  useEffect(() => {
    console.log("WebSocket connection status changed:", isConnected);
  }, [isConnected]);

  // Only show disconnected alert if camera is active AND socket is disconnected
  const showDisconnectAlert = isCameraActive && !isConnected;

  const handleFrameCapture = (frameBase64: string) => {
    setCurrentFrame(frameBase64);
  };

  const handleCameraStateChange = (isActive: boolean) => {
    setIsCameraActive(isActive);
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
      {showDisconnectAlert && (
        <Alert variant="destructive" className="mb-6">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Backend Disconnected</AlertTitle>
          <AlertDescription>
            The backend server is not reachable. To use this demo, you must run the python backend locally.
            <br />
            <a href="/demo" className="font-bold underline hover:text-white/80">Check the Demo page for instructions.</a>
          </AlertDescription>
        </Alert>
      )}

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
            variant={
              isConnected
                ? "default"
                : isCameraActive
                  ? "destructive"
                  : "secondary"
            }
            className="h-6"
          >
            {isConnected
              ? "System Online"
              : isCameraActive
                ? "Connection Failed"
                : "Standby"}
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
              onCameraStateChange={handleCameraStateChange}
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
                  understanding and text-to-speech.
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
