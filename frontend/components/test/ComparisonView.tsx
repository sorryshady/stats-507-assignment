"use client";

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
                  {originalVideoRef.current ? (
                    <video
                      ref={originalVideoRef}
                      autoPlay
                      playsInline
                      muted
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                      <p className="text-sm">Video feed not available</p>
                    </div>
                  )}
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
                  {annotatedFrame ? (
                    <img
                      src={`data:image/jpeg;base64,${annotatedFrame}`}
                      alt="Annotated frame"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                      <div className="text-center">
                        <p className="text-sm">Waiting for processed frame...</p>
                        <p className="text-xs mt-2">
                          {detections.length > 0
                            ? `${detections.length} detection(s) received`
                            : "No detections yet"}
                        </p>
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

