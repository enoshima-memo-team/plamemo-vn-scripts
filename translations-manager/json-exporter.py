# Made for ENOSHIMA MEMO TEAM. https://github.com/enoshima-memo-team
# By:
# - QuitoTactico - https://github.com/QuitoTactico
# - dvdantunes   - https://github.com/dvdantunes

# This script extracts translations from JSON files exported from the game engine.
# It extracts the English and Japanese translations and merges them into a single JSON file.
# The output file contains the English and Japanese translations, with an empty Spanish translation, ready for use on the CROWDIN platform.

# For any questions, visit https://github.com/enoshima-memo-team/plamemo-vn-scripts/blob/develop/README.md#contact-us

import re, json, os, argparse
from typing import Optional

import tkinter as tk
from tkinter import filedialog, messagebox

ENGLISH_TAG = "en"
JAPANESE_TAG = "ja"
SPANISH_TAG = "es-ES"


class SceneMismatchError(Exception):
    """Exception raised for mismatched scenes in input files."""

    pass


# ============================== DEPRECATED =============================


@DeprecationWarning
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


@DeprecationWarning
def output_file_namer(
    input_file_path_en: str, input_file_path_ja: str
) -> Optional[str]:
    """
    Generates the output file name based on the input file names.
    If the input files are from the same scene, in `'pm<scene_id>.txt.scn.m.json'` format, the output file name will be `'extracted<scene_id>.json'`.
    - It can recognize if the input files are from different scenes to say ERROR.
    - Otherwise, if the input files don't match the filename format, it will open a file dialog to save the file with a custom title.
    """
    pattern = r"pm(\d{2}_\d{2})\.txt\.scn\.m\.json"
    match_en = re.search(pattern, input_file_path_en)
    match_ja = re.search(pattern, input_file_path_ja)

    if match_en and match_ja:
        if match_en.group(1) == match_ja.group(1):
            default_filename = f"extracted{match_en.group(1)}.json"
        else:
            raise SceneMismatchError("The selected files are from different scenes.")
    elif match_en:
        default_filename = f"extracted{match_en.group(1)}.json"
    elif match_ja:
        default_filename = f"extracted{match_ja.group(1)}.json"
    else:
        default_filename = "extracted.json"

    return filedialog.asksaveasfilename(
        title="Save file as",
        defaultextension=".json",
        initialfile=default_filename,
        filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
    )


# ============================== UTIL ====================================


def input_folder_selector(language: str = None) -> str:
    """
    Opens a folder dialog to select a folder and returns the selected folder path.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory(
        title=(
            f"Select the folder containing {language.upper()} JSON files"
            if language
            else "Select a folder"
        )
    )
    return folder_path


def output_folder_selector() -> str:
    """
    Opens a folder dialog to select a folder for saving output files.
    Returns the selected folder path.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory(
        title="Select the folder to save OUTPUT files"
    )
    return folder_path


def get_file_pairs(folder_en: str, folder_ja: str) -> list[dict]:
    """
    Matches files with the same name in the English and Japanese folders.
    Returns a list of dictionaries with matched file paths.
    Files without a match will still be included with a None value for the missing counterpart.
    """
    files_en = {f for f in os.listdir(folder_en) if f.endswith(".json")}
    files_ja = {f for f in os.listdir(folder_ja) if f.endswith(".json")}

    all_files = files_en | files_ja  # Union of all filenames
    file_pairs = []

    for file_name in all_files:
        file_pairs.append(
            {
                ENGLISH_TAG: (
                    os.path.join(folder_en, file_name)
                    if file_name in files_en
                    else None
                ),
                JAPANESE_TAG: (
                    os.path.join(folder_ja, file_name)
                    if file_name in files_ja
                    else None
                ),
            }
        )

    return file_pairs


def load_data(input_file_path: str) -> dict:
    """
    Loads the JSON file from the specified path.
    """
    with open(input_file_path, "r", encoding="utf-8") as f:
        return json.load(f)


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


# ============================== MAIN FUNCTIONS ====================================


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
            context = "japanese context"
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


def translations_merger(
    translations_en: dict | None, translations_ja: dict | None
) -> dict:
    """
    Merges Japanese translations into the English translations.
    Adds an empty Spanish translation with status 'untranslated'.
    If Japanese or English translation doesn't exist fully or partially, leaves that space blank.
    """
    # Initialize the merged translations with an empty structure
    merged_translations = {"texts": {}}

    # Get the scenes from both translations, defaulting to empty dicts if missing
    scenes_en = translations_en.get("texts", {}) if translations_en else {}
    scenes_ja = translations_ja.get("texts", {}) if translations_ja else {}

    # Combine all scene labels from both translations
    all_scene_labels = set(scenes_en.keys()) | set(scenes_ja.keys())

    for scene_label in all_scene_labels:
        # Get texts for the current scene from both translations
        scene_texts_en = scenes_en.get(scene_label, {})
        scene_texts_ja = scenes_ja.get(scene_label, {})

        # Initialize the merged scene
        merged_scene = {}

        # Combine all identifiers (keys) from both translations
        all_identifiers = set(scene_texts_en.keys()) | set(scene_texts_ja.keys())

        for identifier in all_identifiers:
            # Get text data for the current identifier from both translations
            text_data_en = scene_texts_en.get(identifier, {})
            text_data_ja = scene_texts_ja.get(identifier, {})

            # Extract the English and Japanese texts (default to empty strings if missing)
            en_text = text_data_en.get("text", "(No English source available)")
            ja_text = text_data_ja.get("text", "(No Japanese source available)")

            # Merge the translations
            merged_scene[identifier] = {
                "text": en_text,  # Use English text as the base
                "translations": {
                    JAPANESE_TAG: {
                        "text": ja_text,
                        "status": "approved" if ja_text else "untranslated",
                    },
                    ENGLISH_TAG: {
                        "text": en_text,
                        "status": "approved" if en_text else "untranslated",
                    },
                    SPANISH_TAG: {
                        "text": "",
                        "status": "untranslated",
                    },
                },
                # Add context if Japanese text exists, otherwise provide a default message
                "context": (
                    f"Original Text: {ja_text}"
                    if ja_text
                    else "No Japanese source available, probably it's original content."
                ),
            }

        # Add the merged scene to the merged translations
        merged_translations["texts"][scene_label] = merged_scene

    return merged_translations


# ================================ MAIN ======================================


def main(
    input_folder_path_en=None, input_folder_path_ja=None, output_folder_path=None
) -> Optional[dict]:
    """
    Main function that executes the loading, extraction, and saving of translations.
    """
    try:
        # If folders are not provided via CLI, use folder selectors
        if not input_folder_path_en:
            input_folder_path_en = input_folder_selector("english")
            if not input_folder_path_en:
                raise Exception("You need to select a folder for English files.")

        if not input_folder_path_ja:
            input_folder_path_ja = input_folder_selector("japanese")
            if not input_folder_path_ja:
                raise Exception("You need to select a folder for Japanese files.")

        if not output_folder_path:
            output_folder_path = output_folder_selector()
            if not output_folder_path:
                raise Exception("You need to select a folder for saving output files.")

        # Get file pairs
        file_pairs = get_file_pairs(input_folder_path_en, input_folder_path_ja)
        if not file_pairs:
            raise SceneMismatchError("No matching files found in the selected folders.")

        # Process each file pair
        for file_pair in file_pairs:
            input_file_path_en = file_pair.get(ENGLISH_TAG)
            input_file_path_ja = file_pair.get(JAPANESE_TAG)

            # Generate output file name
            output_file_name = os.path.basename(
                input_file_path_en or input_file_path_ja
            ).replace(".txt.scn.m.json", ".txt_crowdin.json")
            output_file_path_full = os.path.join(output_folder_path, output_file_name)

            simplified = False

            # Load and process data depending on the existing files and data
            if input_file_path_en and input_file_path_ja:
                data_en = load_data(input_file_path_en) if input_file_path_en else {}
                data_ja = load_data(input_file_path_ja) if input_file_path_ja else {}
                extracted_translations_en = extract_translations(data_en, simplified)
                extracted_translations_ja = extract_translations(data_ja, simplified)
                extracted_translations_merged = translations_merger(
                    extracted_translations_en, extracted_translations_ja
                )
            elif not input_file_path_en:  # EN file doesn't exist
                data_ja = load_data(input_file_path_ja) if input_file_path_ja else {}
                extracted_translations_ja = extract_translations(data_ja, simplified)
                extracted_translations_merged = translations_merger(
                    None, extracted_translations_ja
                )
            elif not input_file_path_ja:  # ja file doesn't exist
                data_en = load_data(input_file_path_en) if input_file_path_en else {}
                extracted_translations_en = extract_translations(data_en, simplified)
                extracted_translations_merged = translations_merger(
                    extracted_translations_en, None
                )

            # Save merged translations
            save_extracted_translations(
                extracted_translations_merged, output_file_path_full
            )

        messagebox.showinfo(
            "Success",
            f"Translations extracted successfully for all matched files.",
        )
        return None

    except SceneMismatchError as e:
        messagebox.showerror("Error", str(e))
        return None

    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None


if __name__ == "__main__":
    # Parse CLI arguments
    parser = argparse.ArgumentParser(
        description="Process translation files and extract translations for CROWDIN."
    )
    parser.add_argument(
        "--input-folder-en",
        type=str,
        help="Path to the folder containing English JSON files.",
    )
    parser.add_argument(
        "--input-folder-ja",
        type=str,
        help="Path to the folder containing Japanese JSON files.",
    )
    parser.add_argument(
        "--output-folder",
        type=str,
        help="Path to the folder where output JSON files will be saved.",
    )

    args = parser.parse_args()

    # Validate CLI arguments
    if not args.input_folder_en and not args.input_folder_ja and not args.output_folder:
        parser.print_help()
        print("\nError: No valid arguments provided. Please specify at least one option.")
        exit(1)

    # Call main with CLI arguments
    main(
        input_folder_path_en=args.input_folder_en,
        input_folder_path_ja=args.input_folder_ja,
        output_folder_path=args.output_folder,
    )

#               ?#########G5###5###########J77G#################PB###########~
#             :G&BB#####BB7BB#BG##########5!?G#######P###########5#####BB###&5
#            7##GG######Y?~PY#BB#########B7?B###BB##BB###########GG#####G###&!
#          .P#BG#######B!!~?7G#B#########Y?B###GJ##5B############BG##B##B####.
#         7##B#########J!7!7!?PB########B?B###G?GB5ja###B########BB##B######5
#       .5#B#######B##Y7!77!!7!B########5B##BP55GG&PYB#BB########PP##BB#P##&~
#      ~GBB#######PB#Y77!777!?JG########B##BB#PB&@@BjaBB#GB####B#B5G#BB#G##B
#     ?GB########GB#Y777!7777B#B#########BPGP7YPGG##Yja#P?####B&&&B5#BBGB#&J
#   :5B########BB##J777!7777?&&B#######B5!!JJ~.^#G7?BYG5!5####&&&&@YBBGG###:
#  ~B########BPB#B?7777!77777&&G####P##BP#J?7?!J@@@#GPY!?B##5Y!?P7PP5GGG##B
#:5#########PJG#G77777777777!Y&G####5G#5&@G555B@@@@##&GJB#&5Y?^B@P^7?BBG##5
##########BY7PBG777777777777!!J5##PBB?#5&&&&&&@@&&&&&&BB&&&7JB&@@G!?B#PB#&7
#########P775PG7777777777777!77?##YY#555B@&&&&&&&&&&&&&&&&&##&@@#?5##BJ###:
#######BJ77YPP?777777777777!7777##J!5G55J&&&&&&&&&&&&&&&&&&&&&&&5YG##PJ##B
######5777?G5?777777777777!!777!B#?7~BP###&&&&&&&&&&&&&&&&&&&#GJ?7B##?J##P
####G?7777GG?7777777!777?JJYJ777GB77~PY5#&&&&&&&&&&&&&&&&&@&#5777?##B.7#&J
##BY77777JG?77777!77jaBB#@@@&#5?5B77!YY?J5B&&@&&&&&&&&&&&&BP#P!77Y#&Y .B&J
# P?777777YJ77!!?5G#&&@@@&&@@@@&BPG7!!YJJJJJYPB#&&@&&&&&#&&BY#G!77P#B!  7&Y
# 77777777777!P#&@@&&&&&&&&&@@@@&#P7!7Y7?JJJJJJJY5GG5P&&&&&@#PG777BBP:   7B
# 77777777!7!#@&&&&&&&&&&&&&@@@@&&P7!7J!JJJJJJJJJJY5P#@&&&&&#PP77J#75     ^~
# 7777777!77B@&&&&&&&&&&&&&&@@@@&&B7!GBJJJJJJJJJJJYP#&&&&&&&G#Y77PJ^!
# 7777777~7P@&&&&&&&&&&&&&&&&@@@@B#7!G&&GYJJJJJJJJJ&&&&&&&&P?#?7?Y !
# 777777!!?&&&&&&&&&&&&&&&&&&@@@@#&B~G&&&#G5JJJJJJG@#B5&@&57?P77Y7 :   ENOSHIMA
# 777777~!G@&&&&&&&&&&&&&&&&&@@@@B&@5G@&&&&&&BP555&&JJB@&J7777!7BP.      MEMO
# 777777~?&&&&&&&&&&&&&&&&&&&@@@@B&&&&&&&&&&&@@@&5&PY#@#?~77~~?B&G       TEAM
# 77777!~5@&&&&&&&&&&&&&&&P&&@@@@B&&&&&&&&&&&&#GYJ5?5@#77~~!^~G###~
