import concurrent
from models.detector import YOLODetector
from models.captioner import BlipCaptioner
from core.types import SceneAnalysis
from core.narrator import Narrator


class SceneComposer:
    def __init__(self, config: dict):
        model_path = config.get("model_path", "yolo11n.pt")
        conf_thresh = config.get("conf_threshold", 0.5)
        cap_model = config.get("cap_model", "Salesforce/blip-image-captioning-base")
        self.detector = YOLODetector(model_path, conf_threshold=conf_thresh)
        self.captioner = BlipCaptioner(model_path=cap_model)
        self.narrator = Narrator()

    def describe_scene(self, image) -> SceneAnalysis:
        print("=" * 40)
        print("Analyzing scene...")
        print("=" * 40)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_det = executor.submit(self.detector.predict, image)
            future_cap = executor.submit(self.captioner.predict, image)

            # Wait for both to finish
            detections = future_det.result()
            caption = future_cap.result()

        # Create the raw analysis object
        scene_data = SceneAnalysis(detections=detections, caption=caption)

        # Generate the rich text
        final_text = self.narrator.generate_description(scene_data)
        # return SceneAnalysis(detections=detections, caption=caption)
        return {
            "data": scene_data,
            "text": final_text,
        }
