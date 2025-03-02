import json


def load_data(input_file_path):
    """
    Loads the JSON file from the specified path.
    """
    with open(input_file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def getDefaultScenesTexts(scene, file_title, global_labels, simplified):
    """
    Get texts and details from the Default type scenes

    Note: scene objects has the following format:

    # type 1: default scenes
    ```
    scenes: [
      {
        label: '',
        texts: [
          [
            'Eru',           # t[0]: character name
            'Girl',          # t[1]: apparently the temporary name before revealing the character name
            'Good morning!'  # t[2]: text/dialog
          ]
        ]
      }
    ]
    ```
    """
    texts = {}
    scene_label = scene["label"].strip("*")
    scene_title = scene["title"]

    for i in range(len(scene["texts"])):
        text_group = scene["texts"][i]
        # format number with leading zero
        identifier = f"{file_title}-{scene_label}.{i:02d}"

        # voice-off when no character available
        character = text_group[0] if text_group[0] is not None else "voice-off"

        # checks if temporary name is present (the name before the)
        # e.g: Eru is not revealed as 'Eru', but as 'Girl' when Tsukasa meets her
        before_revealing_name = text_group[1] if text_group[1] is not None else None

        labels = [
            "character: {}".format(character),
            "scene-type: default",
            "scene-label:{}".format(scene_label),
            "scene-title:{}".format(scene_title),
        ]

        if before_revealing_name is not None:
            labels.append("before-revealing-name:{}".format(before_revealing_name))

        texts[identifier] = {
            "character": character,
            "text": text_group[2],
            "translations": {},
        }

        # Exclude context properties in simplified format
        if not simplified:
            context = "jap context"
            custom_data = "character: {}".format(character)

            extend = {
                "isHidden": False,
                "context": context,
                "labels": labels + global_labels,
                "customData": custom_data,
            }
            texts[identifier].update(extend)

    return texts


def getSelectionScenesTexts(scene, file_title, global_labels, simplified):
    """
    Get texts and details from the Selection type scenes

    Note: scene objects has the following format:

    ### type 2: selection scenes
    ```
    scenes: [
      {
        label: '',
        selects: {
          0: {
            target: ''  # target scene label (optional)
            text: ''
          },
          1: {
            target: ''  # target scene label (optional)
            text: ''
          },
        }
      }
    ]
    ```
    """
    texts = {}
    scene_label = scene["label"].strip("*")
    scene_title = scene["title"]

    for i in range(len(scene["selects"])):
        text_group = scene["selects"][i]
        # format number with leading zero
        identifier = f"{file_title}-{scene_label}.{i:02d}"

        # scene target
        scene_target = (
            text_group["target"].strip("*") if "target" in text_group else "none"
        )

        labels = [
            "scene-type: selection",
            "scene-label: {}".format(scene_label),
            "scene-title: {}".format(scene_title),
            "scene-target: {}".format(scene_target),
        ]

        texts[identifier] = {
            "text": text_group["text"],
            "translations": {},
        }

        # Exclude context properties in simplified format
        if not simplified:
            context = "jap context"
            custom_data = "character: {}".format("pending")

            extend = {
                "isHidden": False,
                "context": context,
                "labels": labels + global_labels,
                "customData": custom_data,
            }
            texts[identifier].update(extend)

    return texts


def extract_translations(data, simplified=False):
    """
    Procesa el JSON cargado y extrae las traducciones organizadas por escenas.
    """
    # Common data
    filename = data["name"]
    file_title = filename.split(".")[0]
    global_labels = ["filename: {}".format(filename)]

    texts = {}
    for scene in data["scenes"]:
        scene_label = scene["label"].strip("*")
        # type 1: default scenes
        if "texts" in scene:
            texts[scene_label] = getDefaultScenesTexts(
                scene, file_title, global_labels, simplified
            )
        # type 2: selection scenes
        if "selects" in scene:
            texts[scene_label] = getSelectionScenesTexts(
                scene, file_title, global_labels, simplified
            )

    extracted_translations = {"texts": texts}

    # Exclude context properties in simplified format
    if not simplified:
        extend = {
            "filename": filename,
            "labels": global_labels,
        }
        extracted_translations = {**extend, **extracted_translations}

    return extracted_translations


def save_extracted_translations(extracted_translations, output_file_path):
    """
    Saves the extracted translations dictionary to a JSON file.
    """
    with open(output_file_path, "wb") as fp:
        fp.write(
            json.dumps(extracted_translations, ensure_ascii=False, indent=2).encode(
                "utf8"
            )
        )


def main(input_file_path, output_file_path, simplified=False):
    """
    Main function that executes the loading, extraction, and saving of translations.
    """
    data = load_data(input_file_path)
    extracted_translations = extract_translations(data, simplified)
    save_extracted_translations(extracted_translations, output_file_path)
    return extracted_translations


if __name__ == "__main__":
    # Example paths; can be modified as needed
    input_file_path = "inputs/en/pm00_01.txt.scn.m.json"
    output_file_path = "output/extracted-00.json"
    simplified = False
    main(input_file_path, output_file_path, simplified)
