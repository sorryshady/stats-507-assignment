"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useEffect, useState } from "react";
import type { StatusResponse } from "@/lib/types";
import { Activity, CheckCircle2, XCircle, Cpu, Server } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface StatusPanelProps {
  detectionCount?: number;
}

export function StatusPanel({ detectionCount = 0 }: StatusPanelProps) {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

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
    <Card className="border-border shadow-sm">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Server className="w-5 h-5" />
          System Status
        </CardTitle>
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
              <span className="text-sm font-medium">Backend Service</span>
              {status.initialized ? (
                <div className="flex items-center text-green-600 text-sm font-medium">
                    <div className="w-2 h-2 rounded-full bg-green-500 mr-2" />
                    Ready
                </div>
              ) : (
                <div className="flex items-center text-destructive text-sm font-medium">
                    <div className="w-2 h-2 rounded-full bg-destructive mr-2" />
                    Not Ready
                </div>
              )}
            </div>

            <div className="space-y-2 pt-3 border-t">
              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-2 text-muted-foreground">
                  YOLO Model
                </span>
                <span className={`text-xs font-mono px-2 py-0.5 rounded ${status.models.yolo === "loaded" ? "bg-muted text-foreground" : "bg-destructive/10 text-destructive"}`}>
                    {status.models.yolo.toUpperCase()}
                </span>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-2 text-muted-foreground">
                  BLIP Model
                </span>
                 <span className={`text-xs font-mono px-2 py-0.5 rounded ${status.models.blip === "loaded" ? "bg-muted text-foreground" : "bg-destructive/10 text-destructive"}`}>
                    {status.models.blip.toUpperCase()}
                </span>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-2 text-muted-foreground">
                  Ollama
                </span>
                 <span className={`text-xs font-mono px-2 py-0.5 rounded ${status.models.ollama === "available" ? "bg-muted text-foreground" : "bg-destructive/10 text-destructive"}`}>
                    {status.models.ollama.toUpperCase()}
                </span>
              </div>
            </div>

            <div className="pt-3 border-t">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Hardware Acceleration</span>
                <Badge variant={status.gpu.available ? "outline" : "secondary"}>
                  {status.gpu.available ? status.gpu.type : "CPU Only"}
                </Badge>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-sm text-destructive text-center py-2">Service Unavailable</div>
        )}
      </CardContent>
    </Card>
  );
}
