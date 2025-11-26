"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Sparkles } from "lucide-react";
import { useState, useImperativeHandle, forwardRef } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface NarrationPanelRef {
  generateNarration: (frameBase64: string) => void;
}

export const NarrationPanel = forwardRef<NarrationPanelRef>((props, ref) => {
  const [narration, setNarration] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sceneDescription, setSceneDescription] = useState<string | null>(null);

  const generateNarration = async (frameBase64: string) => {
    setIsLoading(true);
    setError(null);
    setNarration(null);
    setSceneDescription(null);

    try {
      const response = await fetch(`${API_URL}/api/narration`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ frame: frameBase64 }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setNarration(data.narration || "No narration generated");
      setSceneDescription(data.scene_description || "");
    } catch (err) {
      console.error("Narration error:", err);
      setError(err instanceof Error ? err.message : "Failed to generate narration");
    } finally {
      setIsLoading(false);
    }
  };

  useImperativeHandle(ref, () => ({
    generateNarration,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-5 h-5" />
          AI Narration
        </CardTitle>
        <CardDescription>
          Generate natural language description of the current scene
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {isLoading && (
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        )}

        {error && (
          <div className="p-4 bg-destructive/10 border border-destructive rounded-md text-destructive text-sm">
            {error}
          </div>
        )}

        {narration && (
          <div className="space-y-4">
            <div className="p-4 bg-muted rounded-md">
              <p className="text-sm font-medium mb-2">Narration:</p>
              <p className="text-base">{narration}</p>
            </div>
            
            {sceneDescription && (
              <div className="p-4 bg-muted/50 rounded-md">
                <p className="text-sm font-medium mb-2">Scene Description:</p>
                <p className="text-sm text-muted-foreground">{sceneDescription}</p>
              </div>
            )}
          </div>
        )}

        {!narration && !isLoading && (
          <p className="text-sm text-muted-foreground text-center py-4">
            Click "Generate Narration" to get an AI-powered description of the current scene
          </p>
        )}
      </CardContent>
    </Card>
  );
});

NarrationPanel.displayName = "NarrationPanel";

export function NarrationButton({ 
  onGenerate, 
  disabled 
}: { 
  onGenerate: () => void; 
  disabled?: boolean;
}) {
  return (
    <Button 
      onClick={onGenerate} 
      disabled={disabled}
      className="w-full"
    >
      <Sparkles className="w-4 h-4 mr-2" />
      Generate Narration
    </Button>
  );
}

