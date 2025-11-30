"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import Link from "next/link";
import { Play, AlertTriangle, Github, Info } from "lucide-react";
import Image from "next/image";

export default function DemoPage() {
  const [video1Error, setVideo1Error] = useState(false);
  const [video2Error, setVideo2Error] = useState(false);
  const [video3Error, setVideo3Error] = useState(false);
  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold">Demo Videos</h1>
          <p className="text-xl text-muted-foreground">
            See the system in action or try it yourself
          </p>
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
              The best way to experience Describe My Environment is to try it
              yourself! The interactive test page allows you to see real-time
              object detection, tracking, and AI narration powered by your
              camera feed.
            </p>
            <Alert
              variant="warning"
              className="bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800"
            >
              <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400" />
              <AlertTitle className="text-amber-800 dark:text-amber-300 font-semibold">
                Local Setup Required
              </AlertTitle>
              <AlertDescription className="text-amber-700 dark:text-amber-400/90">
                Due to the computational requirements of real-time AI
                processing, the interactive test page is only available when
                running the application locally. Clone the repository and follow
                the setup instructions to try it yourself.
              </AlertDescription>
            </Alert>
            <div className="flex flex-col sm:flex-row gap-3">
              <Button size="lg" className="w-full sm:w-auto" asChild>
                <a
                  href="https://github.com/sorryshady/stats-507-assignment"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Github className="w-4 h-4 mr-2" />
                  View Source Code
                </a>
              </Button>
              {process.env.NODE_ENV === "development" && (
                <Link href="/test">
                  <Button
                    size="lg"
                    variant="outline"
                    className="w-full sm:w-auto"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Try Interactive Demo
                  </Button>
                </Link>
              )}
            </div>
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
            <Alert className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
              <Info className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              <AlertTitle className="text-blue-800 dark:text-blue-300 font-semibold">
                Video Capture Setup
              </AlertTitle>
              <AlertDescription className="text-blue-700 dark:text-blue-400/90">
                <p>
                  These videos were captured using an iPhone 17 Pro as the
                  camera input while running the pipeline. To use your iPhone as
                  a camera, you can change the corresponding{" "}
                  <code className="bg-blue-100 dark:bg-blue-900 px-1 py-0.5 rounded text-xs">
                    CAMERA_DEVICE_ID
                  </code>{" "}
                  value in{" "}
                  <code className="bg-blue-100 dark:bg-blue-900 px-1 py-0.5 rounded text-xs">
                    config.py
                  </code>
                  .
                </p>
              </AlertDescription>
            </Alert>
            <div className="space-y-2">
              <h3 className="font-semibold">Real-Time Object Detection</h3>
              <p className="text-sm text-muted-foreground">
                See how the system detects and tracks multiple objects
                simultaneously with bounding boxes and confidence scores.
              </p>
              <div className="aspect-video bg-muted rounded-lg flex items-center justify-center overflow-hidden">
                {video1Error ? (
                  <Image
                    src="/multi_detection.jpg"
                    alt="Real-Time Object Detection"
                    width={1000}
                    height={1000}
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <video
                    loop
                    muted
                    controls={false}
                    autoPlay
                    playsInline
                    preload="metadata"
                    onError={() => setVideo1Error(true)}
                    className="w-full h-full object-contain"
                  >
                    <source
                      src="https://oq2yl4ptfo.ufs.sh/f/a33X8THVEOZY4IvGt8yaAnUPqdLmJGV3S6I0j7kgOfoh4uBy"
                      type="video/mp4"
                    />
                  </video>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="font-semibold">Hazard Detection & Alerts</h3>
              <p className="text-sm text-muted-foreground">
                Watch how the system identifies approaching hazards and provides
                real-time alerts.
              </p>
              <Alert
                variant="warning"
                className="bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800 mb-6"
              >
                <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400" />
                <AlertTitle className="text-amber-800 dark:text-amber-300 font-semibold">
                  Hazard Detection Conditions
                </AlertTitle>
                <AlertDescription className="text-amber-700 dark:text-amber-400/90">
                  <p>
                    This demonstration showcases how hazard detection would work
                    in the future. Hazards are detected when objects are{" "}
                    <strong className="inline">expanding</strong> (getting
                    closer){" "}
                    <strong className="inline">
                      and moving toward the center
                    </strong>{" "}
                    of the frame. Due to limitations in relative motion
                    tracking, stationary objects may sometimes trigger false
                    warnings.
                  </p>
                </AlertDescription>
              </Alert>
              <div className="aspect-video bg-muted rounded-lg flex items-center justify-center overflow-hidden">
                {video2Error ? (
                  <Image
                    src="/hazard_detection.jpg"
                    alt="Hazard Detection & Alerts"
                    width={1000}
                    height={1000}
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <video
                    loop
                    muted
                    controls={false}
                    autoPlay
                    playsInline
                    preload="metadata"
                    onError={() => setVideo2Error(true)}
                    className="w-full h-full object-contain"
                  >
                    <source
                      src="https://oq2yl4ptfo.ufs.sh/f/a33X8THVEOZYOMrrno1K4oj9BqVdefYZ5IGah7UwR6CtNWsv"
                      type="video/mp4"
                    />
                  </video>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="font-semibold">AI Narration</h3>
              <p className="text-sm text-muted-foreground">
                Experience natural language scene descriptions generated by the
                AI system.
              </p>
              <div className="aspect-video bg-muted rounded-lg flex items-center justify-center overflow-hidden">
                {video3Error ? (
                  <Image
                    src="/analysis.jpg"
                    alt="AI Narration"
                    width={1000}
                    height={1000}
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <video
                    loop
                    muted
                    controls={false}
                    autoPlay
                    playsInline
                    preload="metadata"
                    onError={() => setVideo3Error(true)}
                    className="w-full h-full object-contain"
                  >
                    <source
                      src="https://oq2yl4ptfo.ufs.sh/f/a33X8THVEOZYpxxXvB29GgyTb4HWvNUYSeiKB0rjdsnZ9El2"
                      type="video/mp4"
                    />
                  </video>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Getting Started (Local Setup)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground mb-4">
              To run the interactive test page locally:
            </p>
            <ol className="list-decimal list-inside space-y-2 text-muted-foreground">
              <li>Clone the repository from GitHub</li>
              <li>
                Set up Python virtual environment and install backend
                dependencies
              </li>
              <li>Start the backend server on port 8000</li>
              <li>Ensure Ollama is running with Llama 3.2 3B model</li>
              <li>
                Run{" "}
                <code className="bg-muted px-2 py-1 rounded text-xs">
                  npm run dev
                </code>{" "}
                in the frontend directory
              </li>
              <li>
                Navigate to the Test page and click &quot;Start Camera&quot;
              </li>
              <li>Watch real-time detections and try the narration feature</li>
            </ol>
            <Button variant="outline" className="w-full sm:w-auto" asChild>
              <a
                href="https://github.com/sorryshady/stats-507-assignment"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Github className="w-4 h-4 mr-2" />
                View Source Code & Setup Instructions
              </a>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
