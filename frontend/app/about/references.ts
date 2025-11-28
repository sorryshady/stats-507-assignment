export interface Reference {
  id: string;
  title: string;
  type: string; // e.g., "product", "research paper", "dataset"
  link: string;
  year: string | number;
  talking_points: string[];
  category: "commercial" | "technical" | "research";
}

export const references: Reference[] = [
  // Commercial Solutions (Existing + New)
  {
    id: "seeing_ai_microsoft",
    title: "Microsoft Seeing AI",
    type: "product",
    link: "https://www.microsoft.com/en-us/ai/seeing-ai",
    year: 2017,
    category: "commercial",
    talking_points: [
      "A mobile app using computer vision for object recognition, text reading, and person identification.",
      "Relies on mode-based interactions (short text, document, person, scene) rather than continuous processing.",
      "Proprietary, closed-source ecosystem (recently released on Android).",
    ],
  },
  {
    id: "envision_app",
    title: "Envision App",
    type: "product",
    link: "https://www.letsenvision.com",
    year: 2018,
    category: "commercial",
    talking_points: [
      "Combines OCR, object detection, and smart glasses integration for BLV users.",
      "Subscription-based model with limited customization options.",
      "Highlights the need for open and extensible research prototypes.",
    ],
  },
  {
    id: "google_lookout",
    title: "Google Lookout",
    type: "product",
    link: "https://play.google.com/store/apps/details?id=com.google.android.apps.accessibility.reveal",
    year: 2019,
    category: "commercial",
    talking_points: [
      "Android app using computer vision to identify food labels, text, and objects.",
      "Requires switching specific modes for different tasks.",
      "Android-only ecosystem limitation.",
    ],
  },

  // Technical Advances (Core Tech enabling this project)
  {
    id: "yolo_series",
    title: "YOLO Series (Redmon et al.)",
    type: "core technology",
    link: "https://docs.ultralytics.com/",
    year: "2016-2024",
    category: "technical",
    talking_points: [
      "Real-time object detection achieving >20 FPS.",
      "YOLO11 (2024) improves efficiency with 22% fewer parameters than YOLOv8, crucial for edge deployment.",
      "Serves as the foundation for the 'Reflex Loop' in our architecture.",
    ],
  },
  {
    id: "blip_vlm",
    title: "Vision-Language Models (BLIP/LLaVA)",
    type: "core technology",
    link: "https://github.com/salesforce/BLIP",
    year: 2022,
    category: "technical",
    talking_points: [
      "BLIP (Li et al., 2022) enables high-quality image captioning with ~156ms latency on modern hardware.",
      "Bridges the gap between visual pixel data and semantic language.",
      "Powers the 'Cognitive Loop' for rich scene understanding.",
    ],
  },
  {
    id: "coco_dataset",
    title: "COCO Dataset (Lin et al.)",
    type: "dataset",
    link: "https://cocodataset.org/",
    year: 2014,
    category: "technical",
    talking_points: [
      "Standard benchmark with 330K+ images and 80 object categories.",
      "Provides diverse, cluttered scenes necessary for training robust accessibility models.",
      "Used for benchmarking our detection capabilities.",
    ],
  },

  // Research & Related Work (New References)
  {
    id: "worldscribe_umich",
    title: "Real-time descriptions of surroundings for people who are blind (WorldScribe)",
    type: "news / research highlight",
    link: "https://news.umich.edu/real-time-descriptions-of-surroundings-for-people-who-are-blind/",
    year: 2024,
    category: "research",
    talking_points: [
      "Describes a UMich-developed system (WorldScribe) using YOLO World + GPT-4 for adaptive descriptions.",
      "Highlights scene description as a 'grand challenge' problem requiring rich, context-aware narration.",
      "Supports the move towards combining detection with LLMs, but proposes a lighter-weight, fully local alternative.",
    ],
  },
  {
    id: "lvvm_environment_perception",
    title: "A Large Vision-Language Model based Environment Perception System",
    type: "research paper",
    link: "https://arxiv.org/html/2504.18027v1",
    year: 2024,
    category: "research",
    talking_points: [
      "Proposes an LVLM-based system combining segmentation, depth, and vision-language models.",
      "Uses structured visual inputs to reduce hallucinations.",
      "Includes wearable-style interaction (touch, vibration) which inspires future multimodal feedback.",
    ],
  },
  {
    id: "yolood_obstacle_detection",
    title: "YOLO-OD: Obstacle Detection for Visually Impaired Navigation",
    type: "research paper",
    link: "https://pmc.ncbi.nlm.nih.gov/articles/PMC11645096/",
    year: 2024,
    category: "research",
    talking_points: [
      "Presents a YOLOv8-based architecture adapted for obstacle detection.",
      "Reinforces YOLO-family detectors as a strong baseline for assistive navigation.",
      "Contrasts with our dual-loop design which adds a cognitive layer (captioning + narration) atop detection.",
    ],
  },
  {
    id: "yolov8_assistive_system",
    title: "Empowering the Visually Impaired: YOLOv8-based Object Detection",
    type: "research paper",
    link: "https://www.sciencedirect.com/science/article/pii/S1877050925000055",
    year: 2025,
    category: "research",
    talking_points: [
      "Implements YOLOv8-based detection with auditory feedback.",
      "Validates real-time performance on constrained hardware.",
      "Supports the choice of YOLO11n for real-time accessibility tools.",
    ],
  },
  {
    id: "assistive_tech_survey",
    title: "Assistive systems for visually impaired people: A survey",
    type: "survey paper",
    link: "https://www.sciencedirect.com/science/article/pii/S0925231224010555",
    year: 2024,
    category: "research",
    talking_points: [
      "Comprehensive survey of AI-based assistive systems.",
      "Highlights challenges like latency, robustness, and privacy.",
      "Motivates our dual-loop, edge-friendly, privacy-first design.",
    ],
  },
  {
    id: "scene_description_use_cases",
    title: "Investigating Use Cases of AI-Powered Scene Description Tools",
    type: "research paper",
    link: "https://dl.acm.org/doi/10.1145/3613904.3642211",
    year: 2024,
    category: "research",
    talking_points: [
      "User study investigating how BLV people use scene description tools.",
      "Finds users want both quick task-oriented feedback and rich contextual narratives.",
      "Directly validates the dual-loop design (Reflex vs. Cognitive) based on human needs.",
    ],
  },
];

