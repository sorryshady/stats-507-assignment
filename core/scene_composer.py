from models.detector import YOLODetector


class SceneComposer:
    def __init__(self, config: dict):
        model_path = config.get("model_path", "yolo11n.pt")
        conf_thresh = config.get("conf_threshold", 0.5)

        self.detector = YOLODetector(model_path, conf_threshold=conf_thresh)

    def describe_scene(self, image) -> str:
        return self.detector.predict(image)
