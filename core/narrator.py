# core/narrator.py
from collections import Counter
from core.types import SceneAnalysis


class Narrator:
    def generate_description(self, scene: SceneAnalysis) -> str:
        """
        Synthesizes object data and captions into a natural language description.
        """
        if not scene.detections:
            return f"I don't see any specific objects, but the scene looks like {scene.caption}."

        # 1. Summarize Counts (e.g., "3 persons, 1 bus")
        counts = Counter([d.label for d in scene.detections])
        object_summary = ", ".join(
            [
                f"{count} {label}{'s' if count > 1 else ''}"
                for label, count in counts.items()
            ]
        )

        # 2. Analyze Spatial Layout (Simple Logic)
        # We look at the first detection (highest confidence) to give immediate warning
        main_obj = scene.detections[0]

        # Calculate center of the box to determine Left/Center/Right
        img_center_x = 320  # Assuming 640x640 image, middle is 320
        box_center_x = (main_obj.box[0] + main_obj.box[2]) / 2

        if box_center_x < img_center_x - 100:
            position = "on your left"
        elif box_center_x > img_center_x + 100:
            position = "on your right"
        else:
            position = "directly ahead"

        # 3. Fusion Template
        # "I see [Objects]. [Main Object] is [Position]. Context: [Caption]"
        text = (
            f"I see {object_summary}. "
            f"The {main_obj.label} is {position}. "
            f"Overall, it looks like {scene.caption}."
        )

        return text
