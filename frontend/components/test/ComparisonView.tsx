"use client";

import { useEffect, useRef, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Layers, Monitor } from "lucide-react";

interface ComparisonViewProps {
  originalVideoRef: React.RefObject<HTMLVideoElement | null>;
  annotatedFrame?: string;
  detections: any[];
  hazards: any[];
}

export function ComparisonView({
  originalVideoRef,
  annotatedFrame,
  detections,
  hazards,
}: ComparisonViewProps) {
  const comparisonVideoRef = useRef<HTMLVideoElement>(null);
  const [imageSrc, setImageSrc] = useState<string | null>(null);

  // Update image source when annotated frame changes
  useEffect(() => {
    if (annotatedFrame && annotatedFrame.length > 0) {
      // Ensure proper data URL format
      const src = annotatedFrame.startsWith('data:') 
        ? annotatedFrame 
        : `data:image/jpeg;base64,${annotatedFrame}`;
      
      setImageSrc(src);
    } else {
      setImageSrc(null);
    }
  }, [annotatedFrame]);

  // Clone the stream to the comparison video element
  useEffect(() => {
    const originalVideo = originalVideoRef.current;
    const comparisonVideo = comparisonVideoRef.current;
    
    if (originalVideo && comparisonVideo && originalVideo.srcObject) {
      const stream = originalVideo.srcObject as MediaStream;
      // Clone the stream tracks
      const clonedStream = new MediaStream();
      stream.getVideoTracks().forEach(track => {
        clonedStream.addTrack(track.clone());
      });
      comparisonVideo.srcObject = clonedStream;
      comparisonVideo.play().catch(console.error);
      
      return () => {
        // Cleanup: stop cloned tracks when component unmounts or stream changes
        if (comparisonVideo.srcObject) {
          const clonedStream = comparisonVideo.srcObject as MediaStream;
          clonedStream.getTracks().forEach(track => track.stop());
          comparisonVideo.srcObject = null;
          comparisonVideo.pause();
        }
      };
    } else if (comparisonVideo && (!originalVideo || !originalVideo.srcObject)) {
      // Stop comparison video if original stream is gone
      if (comparisonVideo.srcObject) {
        const stream = comparisonVideo.srcObject as MediaStream;
        stream.getTracks().forEach(track => track.stop());
        comparisonVideo.srcObject = null;
        comparisonVideo.pause();
      }
    }
  }, [originalVideoRef, originalVideoRef.current?.srcObject]);

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
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Raw Input</span>
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
                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Processed Output</span>
                </div>
                <div className="relative aspect-video bg-black rounded-sm overflow-hidden border border-border/50">
                  {imageSrc ? (
                    <img
                      key={`annotated-${detections.length}-${Date.now()}`}
                      src={imageSrc}
                      alt="Annotated frame"
                      className="w-full h-full object-cover"
                    />
                  ) : detections.length > 0 ? (
                    <div className="w-full h-full flex items-center justify-center bg-muted/10">
                      <div className="text-center">
                        <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                        <p className="text-xs text-muted-foreground">Processing...</p>
                      </div>
                    </div>
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-muted/10">
                       <span className="text-xs text-muted-foreground">Waiting for detections...</span>
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
                <img
                  src={`data:image/jpeg;base64,${annotatedFrame}`}
                  alt="Annotated overlay"
                  className="absolute top-0 left-0 w-full h-full object-cover opacity-60 pointer-events-none"
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
