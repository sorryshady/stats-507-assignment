import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Circle, Clock } from "lucide-react";

export default function RoadmapPage() {
  const phases = [
    {
      status: "completed",
      title: "Phase 1: Core Backend",
      description: "FastAPI backend with ML model integration",
      items: [
        "YOLO object detection and tracking",
        "BLIP scene captioning",
        "Llama 3.2 narration generation",
        "WebSocket real-time communication",
        "REST API endpoints",
      ],
    },
    {
      status: "completed",
      title: "Phase 2: Frontend Foundation",
      description: "Next.js 16 frontend with modern UI",
      items: [
        "Interactive test page",
        "Camera feed integration",
        "Real-time tracking overlay",
        "Hazard alerts",
        "Narration panel",
      ],
    },
    {
      status: "completed",
      title: "Phase 3: Polish & Optimization",
      description: "Performance improvements and UI enhancements",
      items: [
        "Mobile responsiveness",
        "Error handling improvements",
        "Performance optimization",
        "Additional UI components",
      ],
    },
    {
      status: "planned",
      title: "Phase 4: Advanced Features",
      description: "Enhanced functionality and capabilities",
      items: [
        "Multi-camera support",
        "Voice output (TTS)",
        "Customizable detection classes",
        "Historical data visualization",
        "Export functionality",
      ],
    },
    {
      status: "planned",
      title: "Phase 5: Wearable Device",
      description: "Hardware integration and edge computing",
      items: [
        "Edge device optimization",
        "Battery life optimization",
        "Hardware integration",
        "Offline mode support",
        "Smartphone companion app",
      ],
    },
  ];

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold">Roadmap</h1>
          <p className="text-xl text-muted-foreground">
            Planned features and development phases
          </p>
        </div>

        <div className="space-y-6">
          {phases.map((phase, idx) => (
            <Card key={idx}>
              <CardHeader>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    {phase.status === "completed" && (
                      <CheckCircle2 className="w-6 h-6 text-green-500" />
                    )}
                    {phase.status === "in-progress" && (
                      <Clock className="w-6 h-6 text-blue-500" />
                    )}
                    {phase.status === "planned" && (
                      <Circle className="w-6 h-6 text-muted-foreground" />
                    )}
                    <CardTitle>{phase.title}</CardTitle>
                  </div>
                  <Badge
                    variant={
                      phase.status === "completed"
                        ? "default"
                        : phase.status === "in-progress"
                          ? "secondary"
                          : "outline"
                    }
                  >
                    {phase.status === "completed"
                      ? "Completed"
                      : phase.status === "in-progress"
                        ? "In Progress"
                        : "Planned"}
                  </Badge>
                </div>
                <CardDescription>{phase.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {phase.items.map((item, itemIdx) => (
                    <li
                      key={itemIdx}
                      className="flex items-start gap-2 text-sm"
                    >
                      <span className="text-muted-foreground">•</span>
                      <span className="text-muted-foreground">{item}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card className="bg-muted/50">
          <CardHeader>
            <CardTitle>Contributing</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              This roadmap is subject to change based on user feedback and
              technical requirements. If you have suggestions or feature
              requests, please reach out!
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
