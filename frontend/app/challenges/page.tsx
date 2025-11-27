"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Clock, Lightbulb, TrendingUp } from "lucide-react";

export default function ChallengesPage() {
  const challenges = [
    {
      title: "Monocular Depth & Motion",
      category: "Computer Vision",
      description:
        "Using a single camera makes accurate depth perception and relative motion detection highly unreliable. Small movements (like waving a hand) can cause significant bounding box changes, falsely triggering 'approaching' alerts.",
      solution:
        "Currently mitigated by filtering insignificant movements (only tracking extremely significant bounding box changes). Future integration of stereo cameras, LiDAR, or depth-estimation AI (MiDaS) required for true 3D mapping.",
      status: "In Progress",
    },
    {
      title: "Stream Freeze on Generation",
      category: "Performance",
      description:
        "When manually triggering 'Generate Now', the video feed and processed output momentarily freeze or lag. This is likely due to the blocking nature of the inference request or network latency spikes during heavy data transmission.",
      solution:
        "Optimizing the WebSocket handling to be non-blocking and investigating if the backend inference is blocking the main thread. Future move to WebWorkers for frontend processing.",
      status: "In Progress",
    },
    {
      title: "Pretrained Model Limitations",
      category: "AI Models",
      description:
        "We are currently using off-the-shelf pretrained models (YOLO, BLIP) without fine-tuning, limiting their ability to recognize specific hazards or unique environmental contexts relevant to the blind.",
      solution:
        "Building a custom dataset of hazard scenarios and fine-tuning the models to specialize in obstacle detection and navigation assistance.",
      status: "In Progress",
    },
    {
      title: "VLM Hallucinations (BLIP)",
      category: "AI Accuracy",
      description:
        "The scene description model (BLIP) frequently hallucinates details that aren't present (e.g., seeing mirrors or people where there are none) due to lack of temporal context.",
      solution:
        "Refining prompt engineering (implemented), adding verification loops with object detection data, and exploring more stable VLMs like Llava or GPT-4o-mini.",
      status: "In Progress",
    },
    {
      title: "Robotic Text-to-Speech",
      category: "User Experience",
      description:
        "The current system TTS output is flat and robotic, failing to convey the urgency of hazards or the natural tone of a friendly assistant.",
      solution:
        "Integration of emotive TTS engines (e.g., ElevenLabs or OpenAI TTS) to provide more natural, context-aware audio feedback.",
      status: "In Progress",
    },
    {
      title: "Acceleration Estimation",
      category: "Tracking",
      description:
        "Relying solely on 2D bounding box changes to estimate acceleration is noisy and unreliable for predicting potential collisions.",
      solution:
        "Implementing Kalman filters for smoother state estimation and fusing IMU data (if available on wearable hardware) with visual tracking.",
      status: "In Progress",
    },
    {
      title: "Pipeline Optimization",
      category: "System Architecture",
      description:
        "While functional, the current pipeline relies on standard techniques. Advanced optimization methods for edge deployment haven't been fully explored due to time constraints.",
      solution:
        "Investigating model quantization (INT8), TensorRT optimization, and true parallel processing to maximize frame rates on edge devices.",
      status: "In Progress",
    },
    {
      title: "Demo Latency",
      category: "Performance",
      description:
        "The current client-server architecture over WebSocket introduces network latency that wouldn't exist in a production edge device.",
      solution:
        "The final product is designed to run locally on-device (e.g., NVIDIA Jetson), eliminating network round-trips and drastically reducing latency.",
      status: "Planned",
    },
    {
      title: "Object Detection Latency",
      category: "Performance",
      description:
        "Initial real-time processing of high-resolution video feeds created significant computational overhead.",
      solution:
        "Implemented YOLOv11 nano model for faster inference and optimized frame processing pipeline with WebSocket streaming.",
      status: "Solved",
    },
    {
      title: "Multiple Object Tracking",
      category: "Tracking",
      description:
        "Keeping track of specific objects across frames when they are occluded or moving fast.",
      solution:
        "Using ByteTrack algorithm to associate detections across frames based on motion prediction.",
      status: "Solved",
    },
    {
      title: "Audio Feedback Overload",
      category: "User Experience",
      description:
        "Constant narration and alerts can be overwhelming for the user.",
      solution:
        "Implemented a priority system for audio alerts, suppressing low-priority information during critical moments.",
      status: "Solved",
    },
  ];

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 max-w-5xl">
      <div className="mb-12">
        <h1 className="text-4xl font-bold tracking-tight mb-4">
          Project Challenges & Roadmap
        </h1>
        <p className="text-xl text-muted-foreground">
          A transparent look at the technical hurdles we face, our current
          limitations, and how we&apos;re solving them to build a robust
          assistive tool.
        </p>
      </div>

      <div className="grid gap-6">
        {challenges.map((challenge, index) => (
          <Card
            key={index}
            className={`border-l-4 ${challenge.status === "Solved" ? "border-l-green-500" : "border-l-amber-500"} shadow-sm`}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge
                      variant="outline"
                      className="font-mono text-xs uppercase tracking-wider"
                    >
                      {challenge.category}
                    </Badge>
                    {challenge.status === "Solved" ? (
                      <Badge
                        variant="secondary"
                        className="bg-green-100 text-green-800 hover:bg-green-100 dark:bg-green-900/30 dark:text-green-400"
                      >
                        <CheckCircle2 className="w-3 h-3 mr-1" /> Solved
                      </Badge>
                    ) : challenge.status === "Planned" ? (
                      <Badge
                        variant="secondary"
                        className="bg-blue-100 text-blue-800 hover:bg-blue-100 dark:bg-blue-900/30 dark:text-blue-400"
                      >
                        <TrendingUp className="w-3 h-3 mr-1" /> Planned
                      </Badge>
                    ) : (
                      <Badge
                        variant="secondary"
                        className="bg-amber-100 text-amber-800 hover:bg-amber-100 dark:bg-amber-900/30 dark:text-amber-400"
                      >
                        <Clock className="w-3 h-3 mr-1" /> In Progress
                      </Badge>
                    )}
                  </div>
                  <CardTitle className="text-2xl">{challenge.title}</CardTitle>
                </div>
              </div>
              <CardDescription className="text-base mt-2 leading-relaxed">
                {challenge.description}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-muted/30 p-4 rounded-lg flex gap-3 border border-border/50">
                <Lightbulb className="w-5 h-5 text-primary shrink-0 mt-1" />
                <div>
                  <span className="font-semibold block mb-1 text-sm uppercase tracking-wide text-primary">
                    Proposed Solution
                  </span>
                  <p className="text-sm text-muted-foreground">
                    {challenge.solution}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
