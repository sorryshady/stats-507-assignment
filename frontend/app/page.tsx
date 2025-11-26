"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AnimatedBackground } from "@/components/aceternity/AnimatedBackground";
import { TextReveal } from "@/components/aceternity/TextReveal";
import { Spotlight } from "@/components/aceternity/Spotlight";
import { Card3D } from "@/components/aceternity/Card3D";
import { Eye, Shield, Zap, Brain } from "lucide-react";

export default function HomePage() {
  return (
    <div className="relative min-h-screen overflow-hidden">
      <AnimatedBackground />
      <Spotlight className="-top-40 left-0 md:left-60 md:-top-20" />

      {/* Hero Section */}
      <section className="relative z-10 container mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32">
        <div className="text-center space-y-8">
          <Badge variant="secondary" className="mb-4">
            Beta Version
          </Badge>
          
          <TextReveal
            text="See Your World Through AI"
            className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent"
          />
          
          <TextReveal
            text="Real-time object detection and narration powered by advanced machine learning"
            className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto"
            delay={0.5}
          />

          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
            <Link href="/test">
              <Button size="lg" className="text-lg px-8 py-6">
                Try It Now
              </Button>
            </Link>
            <Link href="/demo">
              <Button size="lg" variant="outline" className="text-lg px-8 py-6">
                Watch Demo
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 container mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Powerful Features
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Experience the future of visual assistance technology
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card3D>
            <Card className="h-full">
              <CardHeader>
                <Eye className="w-12 h-12 text-blue-500 mb-4" />
                <CardTitle>Real-Time Detection</CardTitle>
                <CardDescription>
                  Advanced YOLO tracking for instant object recognition
                </CardDescription>
              </CardHeader>
            </Card>
          </Card3D>

          <Card3D>
            <Card className="h-full">
              <CardHeader>
                <Shield className="w-12 h-12 text-purple-500 mb-4" />
                <CardTitle>Safety Alerts</CardTitle>
                <CardDescription>
                  Proximity warnings for approaching hazards
                </CardDescription>
              </CardHeader>
            </Card>
          </Card3D>

          <Card3D>
            <Card className="h-full">
              <CardHeader>
                <Brain className="w-12 h-12 text-pink-500 mb-4" />
                <CardTitle>AI Narration</CardTitle>
                <CardDescription>
                  Natural language descriptions powered by Llama 3.2
                </CardDescription>
              </CardHeader>
            </Card>
          </Card3D>

          <Card3D>
            <Card className="h-full">
              <CardHeader>
                <Zap className="w-12 h-12 text-yellow-500 mb-4" />
                <CardTitle>Low Latency</CardTitle>
                <CardDescription>
                  Optimized for real-time performance
                </CardDescription>
              </CardHeader>
            </Card>
          </Card3D>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 container mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <Card className="bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 border-2">
          <CardContent className="pt-12 pb-12 text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to Experience It?
            </h2>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Grant camera permission and see your environment come to life with AI-powered narration
            </p>
            <Link href="/test">
              <Button size="lg" className="text-lg px-8 py-6">
                Start Testing
              </Button>
            </Link>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
