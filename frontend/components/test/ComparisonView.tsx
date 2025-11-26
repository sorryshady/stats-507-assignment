"use client";

import { useEffect, useRef, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface ComparisonViewProps {
  originalVideoRef: React.RefObject<HTMLVideoElement>;
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

  // Debug: Log props changes
  useEffect(() => {
    console.log("ComparisonView props updated:", {
      hasAnnotatedFrame: !!annotatedFrame,
      annotatedFrameLength: annotatedFrame?.length || 0,
      detectionsCount: detections.length,
      hazardsCount: hazards.length,
    });
  }, [annotatedFrame, detections.length, hazards.length]);

  // Update image source when annotated frame changes
  useEffect(() => {
    if (annotatedFrame && annotatedFrame.length > 0) {
      console.log("ComparisonView: Annotated frame received", {
        length: annotatedFrame.length,
        firstChars: annotatedFrame.substring(0, 50),
        hasDataPrefix: annotatedFrame.startsWith('data:'),
      });
      
      // Ensure proper data URL format
      const src = annotatedFrame.startsWith('data:') 
        ? annotatedFrame 
        : `data:image/jpeg;base64,${annotatedFrame}`;
      
      setImageSrc(src);
      console.log("ComparisonView: Image src set, length:", src.length);
    } else {
      console.log("ComparisonView: No annotated frame, clearing imageSrc");
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
        console.log("✅ Comparison video stopped");
      }
    }
  }, [originalVideoRef, originalVideoRef.current?.srcObject]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Camera Feed Comparison</CardTitle>
        <CardDescription>
          Side-by-side view of original feed vs AI-processed view
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="side-by-side" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="side-by-side">Side by Side</TabsTrigger>
            <TabsTrigger value="overlay">Overlay</TabsTrigger>
          </TabsList>
          
          <TabsContent value="side-by-side" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {/* Original Feed */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-sm">Original Feed</h3>
                  <Badge variant="outline">Live</Badge>
                </div>
                <div className="relative aspect-video bg-black rounded-lg overflow-hidden">
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
                  <h3 className="font-semibold text-sm">AI Processed</h3>
                  <Badge variant="default">
                    {detections.length} objects
                  </Badge>
                </div>
                <div className="relative aspect-video bg-black rounded-lg overflow-hidden">
                  {imageSrc ? (
                    <img
                      key={`annotated-${detections.length}-${Date.now()}`}
                      src={imageSrc}
                      alt="Annotated frame"
                      className="w-full h-full object-cover"
                      onLoad={() => {
                        console.log("✅ Annotated frame image loaded successfully");
                      }}
                      onError={(e) => {
                        console.error("❌ Failed to load annotated frame image");
                        console.error("Image src length:", imageSrc?.length);
                        console.error("First 100 chars:", imageSrc?.substring(0, 100));
                        console.error("Image element:", e.currentTarget);
                        setImageSrc(null); // Clear on error
                      }}
                    />
                  ) : detections.length > 0 ? (
                    <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                      <div className="text-center">
                        <p className="text-sm">Processing frame...</p>
                        <p className="text-xs mt-2">
                          {detections.length} detection(s) received
                        </p>
                        <p className="text-xs mt-1 text-yellow-500">
                          Waiting for annotated frame from backend
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                      <div className="text-center">
                        <p className="text-sm">Waiting for processed frame...</p>
                        <p className="text-xs mt-2">No detections yet</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="overlay" className="space-y-4">
            <div className="relative aspect-video bg-black rounded-lg overflow-hidden">
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
                  className="absolute top-0 left-0 w-full h-full object-cover opacity-50 pointer-events-none"
                />
              )}
            </div>
            <div className="text-sm text-muted-foreground">
              Overlay mode: Original feed with processed annotations at 50% opacity
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

