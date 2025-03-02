import json
import tkinter as tk
from tkinter import filedialog, messagebox
import re
from typing import Optional


class SceneMismatchError(Exception):
    """Exception raised for mismatched scenes in input files."""

    pass


def input_file_selector(language: str = None) -> str:
    """
    Opens a file dialog to select a file and returns the selected file path.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title=(
            f"Select the {language.upper()} JSON file"
            if language
            else "Select a JSON file"
        ),
        filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
    )
    return file_path


def output_file_namer(input_file_path_en: str, input_file_path_jp: str) -> str:
    """
    Generates the output file name based on the input file names.
    If the input files are from the same scene, in `'pm<scene_id>.txt.scn.m.json'` format, the output file name will be `'extracted<scene_id>.json'`.
    - It can recognize if the input files are from different scenes to say ERROR.
    - Otherwise, if the input files don't match the filename format, it will open a file dialog to save the file with a custom title.
    """
    pattern = r"pm(\d{2}_\d{2})\.txt\.scn\.m\.json"
    match_en = re.search(pattern, input_file_path_en)
    match_jp = re.search(pattern, input_file_path_jp)

    if match_en and match_jp:
        if match_en.group(1) == match_jp.group(1):
            default_filename = f"extracted{match_en.group(1)}.json"
        else:
            raise SceneMismatchError("The selected files are from different scenes.")
    elif match_en:
        default_filename = f"extracted{match_en.group(1)}.json"
    elif match_jp:
        default_filename = f"extracted{match_jp.group(1)}.json"
    else:
        default_filename = "extracted.json"

    return filedialog.asksaveasfilename(
        title="Save file as",
        defaultextension=".json",
        initialfile=default_filename,
        filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
    )


def load_data(input_file_path: str) -> dict:
    """
    Loads the JSON file from the specified path.
    """
    with open(input_file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def getDefaultScenesTexts(
    scene: dict, file_title: str, global_labels: list, simplified: bool
) -> dict:
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
            "scene-label: {}".format(scene_label),
            "scene-title: {}".format(scene_title),
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


def getSelectionScenesTexts(
    scene: dict, file_title: str, global_labels: list, simplified: bool
) -> dict:
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


def extract_translations(data: dict, simplified=False) -> dict:
    """
    Processes the loaded JSON and extracts translations organized by scenes.
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


def translations_merger(translations_en: dict, translations_jp: dict) -> dict:
    """
    Merges Japanese translations into the English translations.
    Adds an empty Spanish translation with status 'untranslated'.
    """
    for scene_label, scene_texts in translations_en["texts"].items():
        for identifier, text_data in scene_texts.items():
            # Add Japanese translation
            jp_text = (
                translations_jp["texts"]
                .get(scene_label, {})
                .get(identifier, {})
                .get("text", "")
            )
            text_data["translations"]["jp-JP"] = {"text": jp_text, "status": "approved"}
            # Add empty Spanish translation
            text_data["translations"]["es-ES"] = {"text": "", "status": "untranslated"}
            # Add Japanese context
            text_data["context"] = "Original Text: " + jp_text

    return translations_en


def save_extracted_translations(
    extracted_translations: dict, output_file_path: str
) -> None:
    """
    Saves the extracted translations dictionary to a JSON file.
    """
    with open(output_file_path, "wb") as fp:
        fp.write(
            json.dumps(extracted_translations, ensure_ascii=False, indent=2).encode(
                "utf8"
            )
        )


# ================================ MAIN ======================================


def main() -> Optional[dict]:
    """
    Main function that executes the loading, extraction, and saving of translations.
    """
    try:
        input_file_path_en = input_file_selector("english")
        input_file_path_jp = input_file_selector("japanese")
        output_file_path = output_file_namer(input_file_path_en, input_file_path_jp)

        if not output_file_path:
            return None

        simplified = False

        data_en = load_data(input_file_path_en)
        data_jp = load_data(input_file_path_jp)
        extracted_translations_en = extract_translations(data_en, simplified)
        extracted_translations_jp = extract_translations(data_jp, simplified)
        extracted_translations_merged = translations_merger(
            extracted_translations_en, extracted_translations_jp
        )
        save_extracted_translations(extracted_translations_merged, output_file_path)
        messagebox.showinfo(
            "Success",
            f"Translations extracted successfully.\nSaved in {output_file_path}",
        )
        return extracted_translations_merged

    except SceneMismatchError as e:
        messagebox.showerror("Error", str(e))
        return None

    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None


if __name__ == "__main__":
    main()
