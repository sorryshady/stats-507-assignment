from core.types import SceneAnalysis


class Narrator:
    def generate_description(self, scene: SceneAnalysis) -> str:
        if not scene.detections:
            return f"The scene is mostly clear. It looks like {scene.caption}."

        # 1. Analyze Main Subject (Largest Box = Closest)
        # Sort by Area (width * height)
        sorted_objs = sorted(
            scene.detections,
            key=lambda x: (x.box[2] - x.box[0]) * (x.box[3] - x.box[1]),
            reverse=True,
        )
        main_obj = sorted_objs[0]

        # 2. Determine Spatial Position of Main Subject
        img_center = 320  # Assuming 640 width
        obj_center = (main_obj.box[0] + main_obj.box[2]) / 2

        if obj_center < img_center - 150:
            pos = "to your left"
        elif obj_center > img_center + 150:
            pos = "to your right"
        else:
            pos = "directly in front of you"

        # 3. Check for Crowds (Heuristic)
        people_count = sum(1 for d in scene.detections if d.label == "person")

        # 4. Construct the Narrative
        intro = ""
        if main_obj.label == "person":
            if people_count > 1:
                intro = f"There is a group of {people_count} people {pos}."
            else:
                intro = f"There is a person {pos}."
        else:
            intro = f"There is a {main_obj.label} {pos}."

        # 5. Add Context from BLIP, but make it flow
        # We strip "a " or "an " from the start of the caption to blend it
        clean_caption = scene.caption.replace(
            "arafed ", ""
        ).strip()  # 'arafed' is a common BLIP artifact

        return f"{intro} The general scene appears to be {clean_caption}."
