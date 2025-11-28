import Image from "next/image";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Info,
  BookOpen,
  Cpu,
  BarChart3,
  Target,
  ExternalLink,
  GraduationCap,
} from "lucide-react";
import { references } from "./references";

export default function AboutPage() {
  const commercialRefs = references.filter((r) => r.category === "commercial");
  const technicalRefs = references.filter((r) => r.category === "technical");
  const researchRefs = references.filter((r) => r.category === "research");

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-5xl mx-auto space-y-12">
        {/* Header Section */}
        <div className="text-center space-y-6">
          <Badge className="mb-4" variant="secondary">
            STATS 507 Final Project
          </Badge>
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
            Describe My Environment
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto">
            An end-to-end accessibility tool using computer vision and large
            language models to provide real-time, contextual scene descriptions
            for visually impaired users.
          </p>
          <div className="flex justify-center gap-4 text-sm text-muted-foreground">
            <span>Student: Akhil Nishad</span>
            <span>•</span>
            <span>UMID: 38818750</span>
            <span>•</span>
            <span>Uniquename: akhilnis</span>
          </div>
        </div>

        <Separator />

        {/* Abstract / Overview */}
        <section className="space-y-6">
          <div className="flex items-center gap-2 text-2xl font-bold">
            <Info className="w-6 h-6 text-blue-500" />
            <h2>Overview & Background</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="space-y-4 text-lg text-muted-foreground leading-relaxed">
              <p>
                Millions of blind and low-vision (BLV) individuals struggle to
                independently understand their visual surroundings in real-time.
                While traditional accessibility tools like magnification and
                screen readers exist, they often fail to provide the rich,
                contextual descriptions needed to navigate dynamic environments
                safely.
              </p>
              <p>
                This project builds an end-to-end accessibility application that
                combines modern object detection (YOLO11) with vision-language
                models (BLIP) and large language models (Llama 3.2) to
                automatically detect objects, understand scenes, and generate
                descriptive audio narrations in real-time.
              </p>
            </div>
            <Card className="bg-muted/50">
              <CardHeader>
                <CardTitle>Core Objectives</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex gap-2">
                    <span className="text-blue-500 font-bold">•</span>
                    <span>
                      Solve the &quot;context gap&quot; in existing
                      accessibility tools.
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-blue-500 font-bold">•</span>
                    <span>
                      Demonstrate practical application of dual-loop AI
                      architecture.
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-blue-500 font-bold">•</span>
                    <span>
                      Validate real-time feasibility on consumer hardware (Mac
                      M4) as a proxy for future wearable deployment.
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-blue-500 font-bold">•</span>
                    <span>
                      Showcase full-stack ML engineering from model to frontend.
                    </span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Technical Approach */}
        <section className="space-y-6">
          <div className="flex items-center gap-2 text-2xl font-bold">
            <Cpu className="w-6 h-6 text-green-500" />
            <h2>Technical Approach</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>The Dual-Loop Architecture</CardTitle>
                <CardDescription>
                  Mimicking human cognitive processing
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="relative aspect-video w-full overflow-hidden rounded-lg border bg-muted">
                  <Image
                    src="/about/pipeline_latency.jpg"
                    alt="Pipeline Latency and Architecture"
                    fill
                    className="object-contain"
                  />
                </div>
                <div className="mt-4 grid md:grid-cols-2 gap-4">
                  <div className="p-4 bg-red-50 dark:bg-red-950/20 rounded-lg border border-red-100 dark:border-red-900/50">
                    <h3 className="font-bold text-red-600 dark:text-red-400 mb-2">
                      1. Reflex Loop (Fast)
                    </h3>
                    <p className="text-sm">
                      <strong>Goal:</strong> Safety & Collision Avoidance
                      <br />
                      <strong>Model:</strong> YOLO11n (Object Detection)
                      <br />
                      <strong>Latency:</strong> ~35ms (30 FPS)
                      <br />
                      <strong>Action:</strong> Immediate tracking of moving
                      objects and hazard warnings.
                    </p>
                  </div>
                  <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-100 dark:border-blue-900/50">
                    <h3 className="font-bold text-blue-600 dark:text-blue-400 mb-2">
                      2. Cognitive Loop (Slow)
                    </h3>
                    <p className="text-sm">
                      <strong>Goal:</strong> Context & Understanding
                      <br />
                      <strong>Models:</strong> BLIP (Captioning) + Llama 3.2
                      (Narration)
                      <br />
                      <strong>Latency:</strong> ~200ms - 2s (On-Demand)
                      <br />
                      <strong>Action:</strong> Generates rich, descriptive
                      narratives of the scene.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Data Understanding</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="relative aspect-square w-full overflow-hidden rounded-lg border bg-muted">
                  <Image
                    src="/about/coco_dataset_stats.png"
                    alt="COCO Dataset Statistics"
                    fill
                    className="object-contain"
                  />
                </div>
                <p className="text-sm text-muted-foreground">
                  Analysis of the COCO dataset reveals highly diverse, cluttered
                  environments ideal for accessibility tasks. However,
                  small-object detection remains a challenge in complex scenes.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Benchmarks</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="relative aspect-square w-full overflow-hidden rounded-lg border bg-muted">
                  <Image
                    src="/about/yolo_benchmark.png"
                    alt="YOLO Benchmark Results"
                    fill
                    className="object-contain"
                  />
                </div>
                <p className="text-sm text-muted-foreground">
                  Our initial benchmarks confirmed that YOLO11n achieves the
                  target &gt;20 FPS on consumer hardware (MacBook Pro M4),
                  validating the feasibility of real-time edge processing.
                </p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Results & Conclusion */}
        <section className="space-y-6">
          <div className="flex items-center gap-2 text-2xl font-bold">
            <BarChart3 className="w-6 h-6 text-orange-500" />
            <h2>Preliminary Results</h2>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Detection</CardTitle>
                <CardDescription>YOLO11n</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between border-b pb-2">
                  <span>Latency</span>
                  <span className="font-mono font-bold">~34.7 ms</span>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <span>Throughput</span>
                  <span className="font-mono font-bold">28.8 FPS</span>
                </div>
                <div className="flex justify-between">
                  <span>Memory</span>
                  <span className="font-mono font-bold">~2 GB</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Captioning</CardTitle>
                <CardDescription>BLIP</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between border-b pb-2">
                  <span>Latency</span>
                  <span className="font-mono font-bold">~158.7 ms</span>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <span>Throughput</span>
                  <span className="font-mono font-bold">6.3 FPS</span>
                </div>
                <div className="flex justify-between">
                  <span>Memory</span>
                  <span className="font-mono font-bold">~1.5 GB</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Total Pipeline</CardTitle>
                <CardDescription>End-to-End</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between border-b pb-2">
                  <span>Latency</span>
                  <span className="font-mono font-bold">194.4 ms</span>
                </div>
                <div className="flex justify-between border-b pb-2">
                  <span>Target</span>
                  <span className="font-mono font-bold">&lt; 500 ms</span>
                </div>
                <div className="flex justify-between">
                  <span>Status</span>
                  <span className="font-mono text-green-500 font-bold">
                    EXCEEDED
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card className="bg-primary/5 border-primary/20">
            <CardHeader>
              <CardTitle>Conclusion</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-lg">
                The preliminary results confirm that a local, privacy-focused
                accessibility tool is viable on modern consumer hardware. By
                splitting the architecture into a fast reflex loop and a slower
                cognitive loop, we successfully balance immediate safety needs
                with rich environmental understanding, achieving a total
                pipeline latency of under 200ms—less than half of our original
                500ms target.
              </p>
            </CardContent>
          </Card>
        </section>

        {/* Literature Review */}
        <section className="space-y-6">
          <div className="flex items-center gap-2 text-2xl font-bold">
            <BookOpen className="w-6 h-6 text-purple-500" />
            <h2>Literature Review</h2>
          </div>

          <Tabs defaultValue="commercial" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="commercial">Commercial Solutions</TabsTrigger>
              <TabsTrigger value="technical">Core Technology</TabsTrigger>
              <TabsTrigger value="research">Related Research</TabsTrigger>
            </TabsList>
            
            <TabsContent value="commercial" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>State of the Market</CardTitle>
                  <CardDescription>
                    Existing tools and their limitations
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-4">
                    {commercialRefs.map((ref) => (
                      <a
                        key={ref.id}
                        href={ref.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-4 border rounded-lg relative group hover:border-primary transition-colors cursor-pointer"
                      >
                        <div className="flex justify-between items-start">
                          <h3 className="font-semibold text-lg mb-2">
                            {ref.title} ({ref.year})
                          </h3>
                          <ExternalLink className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                        </div>
                        <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                          {ref.talking_points.map((point, idx) => (
                            <li key={idx}>{point}</li>
                          ))}
                        </ul>
                      </a>
                    ))}
                  </div>
                  <Alert>
                    <Target className="h-4 w-4" />
                    <AlertTitle>The Gap</AlertTitle>
                    <AlertDescription>
                      There is currently no open-source, end-to-end solution
                      combining real-time object detection, scene understanding,
                      and customizable AI narration for general accessibility
                      use cases.
                    </AlertDescription>
                  </Alert>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="technical" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>Core Technologies</CardTitle>
                  <CardDescription>
                    The foundational models enabling this project
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <ul className="space-y-4">
                    {technicalRefs.map((ref) => (
                      <li key={ref.id} className="block">
                        <a
                          href={ref.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block p-4 bg-muted/30 rounded-lg relative group hover:bg-muted/50 transition-colors cursor-pointer"
                        >
                          <div className="flex justify-between items-start">
                            <div className="font-semibold">
                              {ref.title}
                            </div>
                            <ExternalLink className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                          </div>
                          <div className="text-sm text-muted-foreground mt-2 space-y-1">
                             {ref.talking_points.map((point, idx) => (
                                <p key={idx}>• {point}</p>
                             ))}
                          </div>
                        </a>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="research" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>Academic Context</CardTitle>
                  <CardDescription>
                    Recent research papers and studies relevant to this work
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-4">
                    {researchRefs.map((ref) => (
                      <a
                        key={ref.id}
                        href={ref.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-4 border rounded-lg relative group hover:border-primary transition-colors cursor-pointer"
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex flex-col">
                            <h3 className="font-semibold text-lg">
                              {ref.title}
                            </h3>
                            <span className="text-xs text-muted-foreground mb-2 uppercase tracking-wider font-bold">
                              {ref.type} • {ref.year}
                            </span>
                          </div>
                          <ExternalLink className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                        </div>
                         <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1 mt-2">
                          {ref.talking_points.map((point, idx) => (
                            <li key={idx}>{point}</li>
                          ))}
                        </ul>
                      </a>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </section>
      </div>
    </div>
  );
}
