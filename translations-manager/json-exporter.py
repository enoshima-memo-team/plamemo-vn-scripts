# Made for ENOSHIMA MEMO TEAM. https://github.com/enoshima-memo-team
# By:
# - QuitoTactico - https://github.com/QuitoTactico
# - DvDantunes   - https://github.com/dvdantunes

# This script extracts translations from JSON files exported from the game engine.
# It extracts the English and Japanese translations and merges them into a single JSON file.
# The output file contains the English and Japanese translations, with an empty Spanish translation, ready for use on the CROWDIN platform.

# For any questions, visit https://github.com/enoshima-memo-team/plamemo-vn-scripts/blob/develop/README.md#contact-us

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


def output_file_namer(
    input_file_path_en: str, input_file_path_jp: str
) -> Optional[str]:
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
            "character:{}".format(character),
            "scene-type:default",
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
            custom_data = "character:{}".format(character)

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
            "scene-type:selection",
            "scene-label:{}".format(scene_label),
            "scene-title:{}".format(scene_title),
            "scene-target:{}".format(scene_target),
        ]

        texts[identifier] = {
            "text": text_group["text"],
            "translations": {},
        }

        # Exclude context properties in simplified format
        if not simplified:
            context = "jap context"
            custom_data = "character:{}".format("pending")

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
    global_labels = ["filename:{}".format(filename)]

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
            try:
                # Try to add Japanese translation
                jp_text = (
                    translations_jp["texts"]
                    .get(scene_label, {})
                    .get(identifier, {})
                    .get("text", "")
                )
                text_data["translations"]["jp-JP"] = {
                    "text": jp_text,
                    "status": "approved",
                }
                # Add empty Spanish translation
                text_data["translations"]["es-ES"] = {
                    "text": "",
                    "status": "untranslated",
                }
                # Add Japanese context
                text_data["context"] = "Original Text: " + jp_text
            except:
                # If there's no Japanese translation (because it's original content, for example), add a message to the context
                text_data["translations"]["jp-JP"] = {
                    "text": "(Original content of the english version, there's no japanese source).",
                    "status": "approved",
                }
                # Add empty Spanish translation
                text_data["translations"]["es-ES"] = {
                    "text": "",
                    "status": "untranslated",
                }
                # Add Japanese context saying there's no source
                text_data[
                    "context"
                ] = "Original content of the english version, there's no japanese source."

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

#               ?#########G5###5###########J77G#################PB###########~
#             :G&BB#####BB7BB#BG##########5!?G#######P###########5#####BB###&5
#            7##GG######Y?~PY#BB#########B7?B###BB##BB###########GG#####G###&!
#          .P#BG#######B!!~?7G#B#########Y?B###GJ##5B############BG##B##B####.
#         7##B#########J!7!7!?PB########B?B###G?GB5JP###B########BB##B######5
#       .5#B#######B##Y7!77!!7!B########5B##BP55GG&PYB#BB########PP##BB#P##&~
#      ~GBB#######PB#Y77!777!?JG########B##BB#PB&@@BJPBB#GB####B#B5G#BB#G##B
#     ?GB########GB#Y777!7777B#B#########BPGP7YPGG##YJP#P?####B&&&B5#BBGB#&J
#   :5B########BB##J777!7777?&&B#######B5!!JJ~.^#G7?BYG5!5####&&&&@YBBGG###:
#  ~B########BPB#B?7777!77777&&G####P##BP#J?7?!J@@@#GPY!?B##5Y!?P7PP5GGG##B
#:5#########PJG#G77777777777!Y&G####5G#5&@G555B@@@@##&GJB#&5Y?^B@P^7?BBG##5
##########BY7PBG777777777777!!J5##PBB?#5&&&&&&@@&&&&&&BB&&&7JB&@@G!?B#PB#&7
#########P775PG7777777777777!77?##YY#555B@&&&&&&&&&&&&&&&&&##&@@#?5##BJ###:
#######BJ77YPP?777777777777!7777##J!5G55J&&&&&&&&&&&&&&&&&&&&&&&5YG##PJ##B
######5777?G5?777777777777!!777!B#?7~BP###&&&&&&&&&&&&&&&&&&&#GJ?7B##?J##P
####G?7777GG?7777777!777?JJYJ777GB77~PY5#&&&&&&&&&&&&&&&&&@&#5777?##B.7#&J
##BY77777JG?77777!77JPBB#@@@&#5?5B77!YY?J5B&&@&&&&&&&&&&&&BP#P!77Y#&Y .B&J
# P?777777YJ77!!?5G#&&@@@&&@@@@&BPG7!!YJJJJJYPB#&&@&&&&&#&&BY#G!77P#B!  7&Y
# 77777777777!P#&@@&&&&&&&&&@@@@&#P7!7Y7?JJJJJJJY5GG5P&&&&&@#PG777BBP:   7B
# 77777777!7!#@&&&&&&&&&&&&&@@@@&&P7!7J!JJJJJJJJJJY5P#@&&&&&#PP77J#75     ^~
# 7777777!77B@&&&&&&&&&&&&&&@@@@&&B7!GBJJJJJJJJJJJYP#&&&&&&&G#Y77PJ^!
# 7777777~7P@&&&&&&&&&&&&&&&&@@@@B#7!G&&GYJJJJJJJJJ&&&&&&&&P?#?7?Y !
# 777777!!?&&&&&&&&&&&&&&&&&&@@@@#&B~G&&&#G5JJJJJJG@#B5&@&57?P77Y7 :   ENOSHIMA
# 777777~!G@&&&&&&&&&&&&&&&&&@@@@B&@5G@&&&&&&BP555&&JJB@&J7777!7BP.      MEMO
# 777777~?&&&&&&&&&&&&&&&&&&&@@@@B&&&&&&&&&&&@@@&5&PY#@#?~77~~?B&G       TEAM
# 77777!~5@&&&&&&&&&&&&&&&P&&@@@@B&&&&&&&&&&&&#GYJ5?5@#77~~!^~G###~
