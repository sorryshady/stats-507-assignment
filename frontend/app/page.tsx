"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Eye, Shield, Zap, Brain, ArrowRight } from "lucide-react";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Hero Section */}
      <section className="container mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32">
        <div className="max-w-3xl mx-auto text-center space-y-8">
          <Badge variant="outline" className="mb-4">
            v0.1 Beta
          </Badge>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-foreground">
            See Your World Through AI
          </h1>

          <p className="text-xl md:text-2xl text-muted-foreground leading-relaxed">
            Real-time object detection and narration powered by advanced machine
            learning. Navigate your environment with confidence.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
            <Link href="/test">
              <Button size="lg" className="text-lg px-8 py-4 h-auto">
                Start Testing <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
            <Link href="/demo">
              <Button
                size="lg"
                variant="outline"
                className="text-lg px-8 py-4 h-auto"
              >
                Watch Demo
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t bg-muted/30">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Core Capabilities
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Built for performance, accuracy, and safety.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-card border-border/50 shadow-sm hover:shadow-md transition-shadow">
            <CardHeader>
              <Eye className="w-10 h-10 text-foreground mb-4" />
              <CardTitle>Real-Time Detection</CardTitle>
              <CardDescription>
                Advanced YOLO tracking for instant object recognition.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="bg-card border-border/50 shadow-sm hover:shadow-md transition-shadow">
            <CardHeader>
              <Shield className="w-10 h-10 text-foreground mb-4" />
              <CardTitle>Safety Alerts</CardTitle>
              <CardDescription>
                Proactive proximity warnings for approaching hazards.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="bg-card border-border/50 shadow-sm hover:shadow-md transition-shadow">
            <CardHeader>
              <Brain className="w-10 h-10 text-foreground mb-4" />
              <CardTitle>AI Narration</CardTitle>
              <CardDescription>
                Natural language descriptions powered by Llama 3.2.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="bg-card border-border/50 shadow-sm hover:shadow-md transition-shadow">
            <CardHeader>
              <Zap className="w-10 h-10 text-foreground mb-4" />
              <CardTitle>Low Latency</CardTitle>
              <CardDescription>
                Optimized frame processing for immediate feedback.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-foreground text-background rounded-2xl p-12 text-center max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Experience It?
          </h2>
          <p className="text-xl text-background/80 mb-8 max-w-2xl mx-auto">
            Try the interactive application and explore real-time object
            detection and AI-powered narration.
          </p>
          <Link href="/test">
            <Button
              size="lg"
              variant="secondary"
              className="text-lg px-8 py-4 h-auto"
            >
              Launch Application
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
