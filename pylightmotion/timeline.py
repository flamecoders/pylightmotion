# timeline.py

from .bezier import bezier_progress

def parse_timeline(timeline):
    """
    Parse the timeline and organize frames with their respective assets and effects.
    :param timeline: List of dictionaries describing the timeline structure.
    :return: A list of frames, each containing assets to be rendered.
    """
    min_vid_len = 0
    max_vid_len = max([line["end"] for line in timeline])
    parsed_frames = [[] for _ in range(max_vid_len)]

    for line in timeline:
        if not line["start"] >= min_vid_len:
            raise Exception("Misformatted timeline item:", line)

        parsed_frames_map = {}
        parsed_effects_map = {}

        if "effects" in line:
            for eff in line["effects"]:
                if (eff["start"] < line["start"]) or (eff["end"] > line["end"]):
                    raise Exception("Misformatted effect timeline for item:", line)

                for eff_index in range(eff["start"], eff["end"] + 1):
                    eff_name = eff["name"]
                    eff_val = None
                    keyframes_curve = eff["curve"]
                    if keyframes_curve == "const":
                        eff_val = eff["startVal"]
                    elif keyframes_curve == "linear":
                        t = 1.0 / (eff["end"] - eff["start"]) * (eff_index - eff["start"])
                        eff_val = eff["startVal"] + (eff["endVal"] - eff["startVal"]) * t
                    elif keyframes_curve == "bezier":
                        p1x, p1y, p2x, p2y = eff["cts"]
                        t = 1.0 / (eff["end"] - eff["start"]) * (eff_index - eff["start"])
                        eff_val = eff["startVal"] + (eff["endVal"] - eff["startVal"]) * bezier_progress(p1x, p1y, p2x, p2y, t)
                    else:
                        raise Exception("Invalid keyframe curve type.")

                    if eff_index in parsed_effects_map:
                        parsed_effects_map[eff_index][eff_name] = eff_val
                    else:
                        parsed_effects_map[eff_index] = {eff_name: eff_val}

        for frame_index in range(line["start"], line["end"] + 1):
            parsed_frame = {
                "src": line["src"],
                "pos": line["pos"],
                "scale": line["scale"],
            }
            parsed_frames_map[frame_index] = parsed_frame

        # Finalizing
        for idx, item in parsed_frames_map.items():
            if idx in parsed_effects_map:
                item = item | parsed_effects_map[idx]
            parsed_frames[idx - 1].append(item)

    return parsed_frames
