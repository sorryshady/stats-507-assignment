import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Eye, Brain, Shield, Zap } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-4xl mx-auto space-y-12">
        <div className="text-center space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold">About</h1>
          <p className="text-xl text-muted-foreground">
            An AI-powered visual assistant designed to help users understand their environment
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Project Overview</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              Describe My Environment is a beta version of an AI-powered visual assistant that uses
              advanced machine learning models to detect, track, and narrate objects in real-time.
              This project represents a prototype for a future wearable device that could assist
              visually impaired users or provide enhanced situational awareness.
            </p>
            <p className="text-muted-foreground">
              The system combines multiple AI technologies including YOLO object detection, BLIP scene
              captioning, and Llama 3.2 for natural language generation to create a comprehensive
              understanding of the user's environment.
            </p>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <Eye className="w-8 h-8 text-blue-500 mb-2" />
              <CardTitle>Real-Time Detection</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Powered by YOLO11n tracking model for fast and accurate object detection
                at 30 FPS.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Brain className="w-8 h-8 text-purple-500 mb-2" />
              <CardTitle>AI Narration</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Uses Llama 3.2 3B model via Ollama to generate natural language descriptions
                of the scene.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Shield className="w-8 h-8 text-red-500 mb-2" />
              <CardTitle>Safety Features</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Proximity warnings and hazard detection to alert users of approaching objects.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Zap className="w-8 h-8 text-yellow-500 mb-2" />
              <CardTitle>Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Optimized for low latency with dual-loop architecture separating reflex and
                cognitive processing.
              </p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Technology Stack</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              <Badge>Python</Badge>
              <Badge>FastAPI</Badge>
              <Badge>Next.js 16</Badge>
              <Badge>TypeScript</Badge>
              <Badge>YOLO11</Badge>
              <Badge>BLIP</Badge>
              <Badge>Llama 3.2</Badge>
              <Badge>Ollama</Badge>
              <Badge>WebSocket</Badge>
              <Badge>WebRTC</Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Beta Version Notice</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              This is a beta version of the system. Features are subject to change and improvements
              are ongoing. The current implementation serves as a prototype and demonstration of
              the core functionality.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

