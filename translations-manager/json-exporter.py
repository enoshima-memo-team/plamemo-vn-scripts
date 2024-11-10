import json

input_file_path = 'pm00_01.txt.scn.m.json'
output_file_path = 'extracted.json'


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
Get texts and details from the scenes

Note: scenes object has the following format:

scenes: [
  {
    label: ''
    texts: [
      [
        'Tsukasa',        # t[0]: character name
        null,
        'Good morning!'   # t[2]: text/dialog
      ]
    ]
  }
]
"""
texts = {}
for s in data['scenes']:
  # ignore if no texts in scenes
  if 'texts' not in s:
    continue

  scene_label = s['label'].strip('*')
  scene_title = s['title']

  # group texts by scene label
  texts[scene_label] = {}

  for i in range(len(s['texts'])):
    t = s['texts'][i]

    # format number with leading zero
    identifier = f'{file_title}-{scene_label}.{i:02d}'
    labels = [
      'scene-label:{}'.format(scene_label),
      'scene-title:{}'.format(scene_title),
      t[0] if t[0] is not None else 'voice-off'     # voice-off when no character available
    ]

    texts[scene_label][identifier] = {
      'text': t[2],
      'labels': global_labels + labels
    }


# Generate the translation file to export
extracted_translations = {
  'filename': filename,
  'labels': global_labels,
  'texts': texts
}


# Save the outputfile
# print(json.dumps(extracted_translations, ensure_ascii=False, indent = 2))
with open(output_file_path, 'wb') as fp:
  fp.write(json.dumps(extracted_translations, ensure_ascii=False, indent = 2).encode("utf8"))
