import json

input_file_path = 'pm00_01.txt.scn.m.json'
output_file_path = 'extracted-00.json'
simplified = False


# Open the json file
with open(input_file_path, 'r') as f:
  data = json.load(f)


# Common data
filename = data['name']
file_title = data['name'].split('.')[0]
texts = data['scenes'][0]['texts']
global_labels = []


# Generate labels
global_labels.extend(
  [
    'filename:{}'.format(filename)
  ]
)


"""
Get texts and details from the Default type scenes

Note: scene objects has the following format:

# type 1: default scenes
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
"""
def getDefaultScenesTexts(scene):
  texts = {}
  scene_label = scene['label'].strip('*')
  scene_title = scene['title']

  for i in range(len(scene['texts'])):
    text_group = scene['texts'][i]

    # format number with leading zero
    identifier = f'{file_title}-{scene_label}.{i:02d}'

    # voice-off when no character available
    character = text_group[0] if text_group[0] is not None else 'voice-off'

    # checks if temporary name is present (the name before the)
    # e.g: Eru is not revealed as 'Eru', but as 'Girl' when Tsukasa meets her
    before_revealing_name = text_group[1] if text_group[1] is not None else None

    labels = [
      character,
      'scene-type:default',
      'scene-label:{}'.format(scene_label),
      'scene-title:{}'.format(scene_title),
    ]

    if before_revealing_name is not None:
      labels.append('before-revealing-name:{}'.format(before_revealing_name))

    texts[identifier] = {
      'character': character,
      'text': text_group[2],
      'translations': {},
    }

    # Exclude context properties in simplified format
    if not simplified:
      context = 'jap context'
      custom_data = 'character: {}'.format(character)

      extend = {
        'isHidden': False,
        'context': context,
        'labels': labels + global_labels,
        'customData': custom_data
      }
      texts[identifier] = {**texts[identifier], **extend}

  return texts


"""
Get texts and details from the Selection type scenes

Note: scene objects has the following format:

# type 2: selection scenes
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
"""
def getSelectionScenesTexts(scene):
  texts = {}
  scene_label = scene['label'].strip('*')
  scene_title = scene['title']

  for i in range(len(scene['selects'])):
    text_group = scene['selects'][i]

    # format number with leading zero
    identifier = f'{file_title}-{scene_label}.{i:02d}'

    # scene target
    scene_target = text_group['target'].strip('*') if 'target' in text_group else 'none'

    labels = [
      'scene-type:selection',
      'scene-label:{}'.format(scene_label),
      'scene-title:{}'.format(scene_title),
      'scene-target:{}'.format(scene_target),
    ]

    texts[identifier] = {
      'text': text_group['text'],
      'translations': {},
    }

    # Exclude context properties in simplified format
    if not simplified:
      context = 'jap context'
      custom_data = 'character: {}'.format('pending')

      extend = {
        'isHidden': False,
        'context': context,
        'labels': labels + global_labels,
        'customData': custom_data
      }
      texts[identifier] = {**texts[identifier], **extend}

  return texts


"""
Get texts and details from the scenes
"""
texts = {}
for s in data['scenes']:
  # group texts by scene label
  scene_label = s['label'].strip('*')

  # type 1: default scenes
  if 'texts' in s:
    texts[scene_label] = getDefaultScenesTexts(s)

  # type 2: selection scenes
  if 'selects' in s:
    texts[scene_label] = getSelectionScenesTexts(s)




# Generate the translation file to export
extracted_translations = {
  'texts': texts
}

# Exclude context properties in simplified format
if not simplified:
  extend = {
    'filename': filename,
    'labels': global_labels,
  }
  extracted_translations = {**extend, **extracted_translations}

# Save the output file
# print(json.dumps(extracted_translations, ensure_ascii=False, indent = 2))
with open(output_file_path, 'wb') as fp:
  fp.write(json.dumps(extracted_translations, ensure_ascii=False, indent = 2).encode("utf8"))
