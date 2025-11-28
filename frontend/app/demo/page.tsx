import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import Link from "next/link";
import { Play, ExternalLink, AlertTriangle, Github, Mail } from "lucide-react";

export default function DemoPage() {
  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold">Demo Videos</h1>
          <p className="text-xl text-muted-foreground">
            See the system in action or try it yourself
          </p>
        </div>

        {/* Deployment / Testing Notice */}
        <Alert variant="warning" className="bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800">
          <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400" />
          <AlertTitle className="text-amber-800 dark:text-amber-300 font-semibold mb-2">
            Important Note on Live Testing
          </AlertTitle>
          <AlertDescription className="text-amber-700 dark:text-amber-400/90 space-y-2">
            <p>
              This project requires a powerful backend (running YOLO11 + Llama 3.2) which is currently hosted locally
              on a MacBook Pro M4 to demonstrate edge-device capabilities.
            </p>
            <p className="font-medium">
              The live interactive demo below will only work if the backend server is currently online.
            </p>
          </AlertDescription>
        </Alert>

        <div className="grid md:grid-cols-2 gap-6">
          <Card>
             <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Github className="w-5 h-5" />
                Option A: Run Locally
              </CardTitle>
              <CardDescription>Best performance & privacy</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                To experience the full system with real-time latency, clone the repository and run the backend on your own machine.
              </p>
              <Button variant="outline" className="w-full" asChild>
                <a href="https://github.com/akhilnis/final-project" target="_blank" rel="noopener noreferrer">
                  View Source Code
                </a>
              </Button>
            </CardContent>
          </Card>

          <Card>
             <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="w-5 h-5" />
                Option B: Request Live Demo
              </CardTitle>
              <CardDescription>Remote testing session</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                I can temporarily expose my local server via a secure tunnel for evaluation purposes. Contact me to schedule a time.
              </p>
              <Button variant="outline" className="w-full" asChild>
                <a href="mailto:akhilnis@umich.edu">
                  Contact Developer
                </a>
              </Button>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Interactive Demo</CardTitle>
            <CardDescription>
              Experience the system live with your own camera
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              The best way to experience Describe My Environment is to try it yourself! Use the
              interactive test page to see real-time object detection, tracking, and AI narration
              powered by your camera feed.
            </p>
            <Link href="/test">
              <Button size="lg" className="w-full sm:w-auto">
                <Play className="w-4 h-4 mr-2" />
                Try Interactive Demo
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Video Demonstrations</CardTitle>
            <CardDescription>
              Watch recorded demonstrations of key features
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <h3 className="font-semibold">Real-Time Object Detection</h3>
              <p className="text-sm text-muted-foreground">
                See how the system detects and tracks multiple objects simultaneously with
                bounding boxes and confidence scores.
              </p>
              <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
                <p className="text-muted-foreground">Video placeholder - Add your demo video here</p>
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="font-semibold">Hazard Detection & Alerts</h3>
              <p className="text-sm text-muted-foreground">
                Watch how the system identifies approaching hazards and provides real-time alerts.
              </p>
              <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
                <p className="text-muted-foreground">Video placeholder - Add your demo video here</p>
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="font-semibold">AI Narration</h3>
              <p className="text-sm text-muted-foreground">
                Experience natural language scene descriptions generated by the AI system.
              </p>
              <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
                <p className="text-muted-foreground">Video placeholder - Add your demo video here</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Getting Started</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <ol className="list-decimal list-inside space-y-2 text-muted-foreground">
              <li>Make sure the backend server is running on port 8000</li>
              <li>Ensure Ollama is running with Llama 3.2 3B model</li>
              <li>Navigate to the Test page</li>
              <li>Click "Start Camera" and grant permission</li>
              <li>Watch real-time detections and try the narration feature</li>
            </ol>
            <Link href="/test">
              <Button variant="outline" className="w-full sm:w-auto">
                <ExternalLink className="w-4 h-4 mr-2" />
                Go to Test Page
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

