"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useEffect, useState } from "react";
import type { StatusResponse } from "@/lib/types";
import { Activity, Cpu, CheckCircle2, XCircle } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface StatusPanelProps {
  detectionCount?: number;
}

export function StatusPanel({ detectionCount = 0 }: StatusPanelProps) {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Debug: Log when detectionCount changes
  useEffect(() => {
    console.log("StatusPanel: detectionCount prop changed", {
      detectionCount,
      type: typeof detectionCount,
    });
  }, [detectionCount]);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch(`${API_URL}/api/status`);
        if (response.ok) {
          const data: StatusResponse = await response.json();
          setStatus(data);
        }
      } catch (err) {
        console.error("Status fetch error:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="w-5 h-5" />
          System Status
        </CardTitle>
        <CardDescription>Backend service status and model information</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {isLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
        ) : status ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Initialized</span>
              {status.initialized ? (
                <Badge variant="default" className="bg-green-500">
                  <CheckCircle2 className="w-3 h-3 mr-1" />
                  Ready
                </Badge>
              ) : (
                <Badge variant="secondary">
                  <XCircle className="w-3 h-3 mr-1" />
                  Not Ready
                </Badge>
              )}
            </div>

            <div className="space-y-2 pt-2 border-t">
              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-2">
                  <Cpu className="w-4 h-4" />
                  YOLO
                </span>
                <Badge variant={status.models.yolo === "loaded" ? "default" : "secondary"}>
                  {status.models.yolo}
                </Badge>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-2">
                  <Cpu className="w-4 h-4" />
                  BLIP
                </span>
                <Badge variant={status.models.blip === "loaded" ? "default" : "secondary"}>
                  {status.models.blip}
                </Badge>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-2">
                  <Cpu className="w-4 h-4" />
                  Ollama
                </span>
                <Badge variant={status.models.ollama === "available" ? "default" : "secondary"}>
                  {status.models.ollama}
                </Badge>
              </div>
            </div>

            <div className="pt-2 border-t">
              <div className="flex items-center justify-between text-sm">
                <span>GPU</span>
                <Badge variant={status.gpu.available ? "default" : "secondary"}>
                  {status.gpu.available ? status.gpu.type : "Not Available"}
                </Badge>
              </div>
            </div>

            <div className="pt-2 border-t">
              <div className="text-sm">
                <span className="font-medium">Active Detections: </span>
                <span className="font-semibold text-primary">{detectionCount}</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-sm text-destructive">Failed to fetch status</div>
        )}
      </CardContent>
    </Card>
  );
}

