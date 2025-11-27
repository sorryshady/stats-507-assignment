"use client";

import { useEffect, useRef, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Layers, Monitor } from "lucide-react";
import type { Detection, Hazard } from "@/lib/types";

interface ComparisonViewProps {
  originalVideoRef: React.RefObject<HTMLVideoElement | null>;
  annotatedFrame?: string;
  detections: Detection[];
  hazards: Hazard[];
}

export function ComparisonView({
  originalVideoRef,
  annotatedFrame,
  detections,
}: ComparisonViewProps) {
  const comparisonVideoRef = useRef<HTMLVideoElement>(null);
  const currentStreamIdRef = useRef<string | null>(null);

  // Generate stable key and image source without using Date.now() in render
  const { imageSrc, imageKey } = useMemo(() => {
    if (annotatedFrame && annotatedFrame.length > 0) {
      const src = annotatedFrame.startsWith("data:")
        ? annotatedFrame
        : `data:image/jpeg;base64,${annotatedFrame}`;
      return {
        imageSrc: src,
        imageKey: `annotated-${detections.length}-${annotatedFrame.substring(0, 20)}`,
      };
    }
    return {
      imageSrc: null,
      imageKey: `annotated-${detections.length}-none`,
    };
  }, [annotatedFrame, detections.length]);

  // Clone the stream to the comparison video element
  useEffect(() => {
    // Poll for the stream availability since ref changes don't trigger re-renders
    const checkStream = () => {
      const originalVideo = originalVideoRef.current;
      const comparisonVideo = comparisonVideoRef.current;

      if (originalVideo && comparisonVideo && originalVideo.srcObject) {
        const stream = originalVideo.srcObject as MediaStream;

        // Check if we already have this stream assigned (by ID) to avoid unnecessary cloning/reassigning
        if (currentStreamIdRef.current !== stream.id) {
          // Clone the stream tracks
          const clonedStream = new MediaStream();
          stream.getVideoTracks().forEach((track) => {
            clonedStream.addTrack(track.clone());
          });
          comparisonVideo.srcObject = clonedStream;
          currentStreamIdRef.current = stream.id;
          comparisonVideo.play().catch(console.error);
        }
      } else if (comparisonVideo && comparisonVideo.srcObject) {
        // Cleanup if original stream is gone
        const stream = comparisonVideo.srcObject as MediaStream;
        stream.getTracks().forEach((track) => track.stop());
        comparisonVideo.srcObject = null;
        currentStreamIdRef.current = null;
      }
    };

    const intervalId = setInterval(checkStream, 1000); // Check every second
    checkStream(); // Check immediately

    return () => clearInterval(intervalId);
  }, [originalVideoRef]);

  return (
    <Card className="border-border shadow-sm">
      <CardHeader className="pb-3 border-b">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <Monitor className="w-5 h-5" />
            Live Analysis
          </CardTitle>
          <Badge variant="outline" className="font-mono">
            {detections.length} Objects
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="pt-4">
        <Tabs defaultValue="side-by-side" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-4">
            <TabsTrigger value="side-by-side">Split View</TabsTrigger>
            <TabsTrigger value="overlay">Overlay View</TabsTrigger>
          </TabsList>

          <TabsContent value="side-by-side" className="space-y-4 mt-0">
            <div className="grid grid-cols-2 gap-4">
              {/* Original Feed */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Raw Input
                  </span>
                </div>
                <div className="relative aspect-video bg-black rounded-sm overflow-hidden border border-border/50">
                  <video
                    ref={comparisonVideoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>

              {/* Processed View */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Processed Output
                  </span>
                </div>
                <div className="relative aspect-video bg-black rounded-sm overflow-hidden border border-border/50">
                  {imageSrc ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      key={imageKey}
                      src={imageSrc}
                      alt="Annotated frame"
                      className="w-full h-full object-cover"
                    />
                  ) : detections.length > 0 ? (
                    <div className="w-full h-full flex items-center justify-center bg-muted/10">
                      <div className="text-center">
                        <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                        <p className="text-xs text-muted-foreground">
                          Processing...
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-muted/10">
                      <span className="text-xs text-muted-foreground">
                        Waiting for detections...
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="overlay" className="mt-0">
            <div className="relative aspect-video bg-black rounded-sm overflow-hidden border border-border/50">
              <video
                ref={originalVideoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover"
              />
              {annotatedFrame && (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={`data:image/jpeg;base64,${annotatedFrame}`}
                  alt="Annotated overlay"
                  className="absolute top-0 left-0 w-full h-full object-cover pointer-events-none"
                />
              )}
            </div>
            <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
              <Layers className="w-3 h-3" />
              <span>Composite view active</span>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
