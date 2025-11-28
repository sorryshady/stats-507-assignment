"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Sparkles,
  Volume2,
  Square,
  Settings2,
} from "lucide-react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { useState, useImperativeHandle, forwardRef, useEffect, useRef } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface NarrationPanelRef {
  generateNarration: (frameBase64: string) => void;
}

export const NarrationPanel = forwardRef<NarrationPanelRef>((props, ref) => {
  const [narration, setNarration] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sceneDescription, setSceneDescription] = useState<string | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  
  // TTS State
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<string>("");
  const [rate, setRate] = useState(1);
  const [pitch, setPitch] = useState(1);
  
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  useEffect(() => {
    // Load voices
    const loadVoices = () => {
      const availableVoices = window.speechSynthesis.getVoices();
      setVoices(availableVoices);
      
      // Try to set a good default if not already set
      if (availableVoices.length > 0 && !selectedVoice) {
        // Preference order: Google US English -> Microsoft Samantha -> System Default
        const preferred = availableVoices.find(v => v.name === "Google US English") ||
                         availableVoices.find(v => v.name === "Samantha") ||
                         availableVoices.find(v => v.lang === "en-US") ||
                         availableVoices[0];
        setSelectedVoice(preferred.name);
      }
    };

    loadVoices();
    
    // Chrome requires this event listener
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    // Cleanup
    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, [selectedVoice]);

  const stopSpeaking = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  const speakNarration = (text: string) => {
    if (!window.speechSynthesis) {
      console.warn("Text-to-speech not supported in this browser");
      return;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utteranceRef.current = utterance;

    // Apply voice settings
    const voice = voices.find(v => v.name === selectedVoice);
    if (voice) utterance.voice = voice;
    utterance.rate = rate;
    utterance.pitch = pitch;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = (e) => {
      console.error("Speech synthesis error:", e);
      setIsSpeaking(false);
    };

    window.speechSynthesis.speak(utterance);
  };

  const generateNarration = async (frameBase64: string) => {
    setIsLoading(true);
    setError(null);
    setNarration(null);
    setSceneDescription(null);
    stopSpeaking(); // Stop any previous speech

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
      const newNarration = data.narration || "No narration generated";
      setNarration(newNarration);
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
    <Card className="border-border shadow-sm">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Sparkles className="w-5 h-5" />
            AI Analysis
          </CardTitle>
          
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <Settings2 className="w-4 h-4" />
                <span className="sr-only">Voice settings</span>
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80">
              <div className="grid gap-4">
                <div className="space-y-2">
                  <h4 className="font-medium leading-none">Voice Settings</h4>
                  <p className="text-sm text-muted-foreground">
                    Customize the narration voice.
                  </p>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="voice">Voice</Label>
                  <Select value={selectedVoice} onValueChange={setSelectedVoice}>
                    <SelectTrigger id="voice" className="w-full">
                      <SelectValue placeholder="Select a voice" />
                    </SelectTrigger>
                    <SelectContent className="max-h-[200px]">
                      {voices.map((voice) => (
                        <SelectItem key={voice.name} value={voice.name}>
                          {voice.name} ({voice.lang})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="rate">Speed</Label>
                    <span className="text-xs text-muted-foreground">{rate}x</span>
                  </div>
                  <Slider
                    id="rate"
                    min={0.5}
                    max={2}
                    step={0.1}
                    value={[rate]}
                    onValueChange={([val]) => setRate(val)}
                  />
                </div>
                <div className="grid gap-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="pitch">Pitch</Label>
                    <span className="text-xs text-muted-foreground">{pitch}</span>
                  </div>
                  <Slider
                    id="pitch"
                    min={0.5}
                    max={2}
                    step={0.1}
                    value={[pitch]}
                    onValueChange={([val]) => setPitch(val)}
                  />
                </div>
              </div>
            </PopoverContent>
          </Popover>
        </div>
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
          <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md text-destructive text-sm">
            {error}
          </div>
        )}

        {narration && (
          <div className="space-y-4">
            <div className="p-3 bg-muted/50 rounded-md border border-border/50 space-y-3">
              <div className="flex items-center justify-between">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Narrative</p>
                {isSpeaking ? (
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="h-6 w-6 p-0 hover:bg-destructive/10 hover:text-destructive"
                    onClick={stopSpeaking}
                    title="Stop speaking"
                  >
                    <Square className="w-3.5 h-3.5 fill-current" />
                  </Button>
                ) : (
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="h-6 w-6 p-0 hover:bg-primary/10 hover:text-primary"
                    onClick={() => speakNarration(narration)}
                    title="Read aloud"
                  >
                    <Volume2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
              <p className="text-sm leading-relaxed">{narration}</p>
            </div>
            
            {sceneDescription && (
              <div className="p-3 bg-muted/30 rounded-md border border-border/50">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">Technical Context</p>
                <p className="text-xs text-muted-foreground leading-relaxed">{sceneDescription}</p>
              </div>
            )}
          </div>
        )}

        {!narration && !isLoading && (
          <div className="text-center py-6 text-muted-foreground text-sm">
            Ready to analyze scene.
          </div>
        )}
      </CardContent>
    </Card>
  );
});
      <CardContent className="space-y-4">
        {isLoading && (
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        )}

        {error && (
          <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md text-destructive text-sm">
            {error}
          </div>
        )}

        {narration && (
          <div className="space-y-4">
            <div className="p-3 bg-muted/50 rounded-md border border-border/50 space-y-3">
              <div className="flex items-center justify-between">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Narrative</p>
                {isSpeaking ? (
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="h-6 w-6 p-0 hover:bg-destructive/10 hover:text-destructive"
                    onClick={stopSpeaking}
                    title="Stop speaking"
                  >
                    <Square className="w-3.5 h-3.5 fill-current" />
                  </Button>
                ) : (
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="h-6 w-6 p-0 hover:bg-primary/10 hover:text-primary"
                    onClick={() => speakNarration(narration)}
                    title="Read aloud"
                  >
                    <Volume2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
              <p className="text-sm leading-relaxed">{narration}</p>
            </div>
            
            {sceneDescription && (
              <div className="p-3 bg-muted/30 rounded-md border border-border/50">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">Technical Context</p>
                <p className="text-xs text-muted-foreground leading-relaxed">{sceneDescription}</p>
              </div>
            )}
          </div>
        )}

        {!narration && !isLoading && (
          <div className="text-center py-6 text-muted-foreground text-sm">
            Ready to analyze scene.
          </div>
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
      variant="secondary"
    >
      <Sparkles className="w-4 h-4 mr-2" />
      Generate Analysis
    </Button>
  );
}
