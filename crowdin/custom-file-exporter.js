/**
 * Crowdin - Custom file exporter
 *
 * @see https://store.crowdin.com/cff
 * @see https://support.crowdin.com/developer/crowdin-apps-module-custom-file-format/#strings-array-structure
 */

/**
 * Available and already defined "env" variables
 *
 * - strings: A global array variable, list of strings that were added to the project
 *    They will contain the transalations texts too
 * - content: Contains the source file content in UTF-8 encoding.
 * - error: Set this variable to a string if your code encounters an
 *     error and cannot form the strings array.
 * - fileName: The name of the source file (e.g., 'source-file.json').
 * - filePath: The file path within the Crowdin project (e.g., '/main/source-file.json').
 * - fileId: The unique ID for the file in Crowdin.
 * - targetLanguages: An array of objects containing details about each target language.
 */


/**
 * Export the Crowdin string list as-is (e.g. as they are
 * currently stored). Used for debugging purposes
 */
const exportAsIsStringList = false;


// Get the original source file as base for the export file
let fileContent = JSON.parse(content);

// Then attach changes + translations
for (const stringObj of strings) {
  const textId = stringObj.identifier;

  // Get scene label where the string belongs
  // related label has the format: 'scene-label:xyz'
  const scene_label = (
    stringObj.labels.find(s => s.startsWith('scene-label')) || 'scene:none'
  ).split(':')[1];
  if (scene_label == 'none') {
    error += `<br>Error: ${textId} doesn't have a 'scene-label' label`;
  }

  // The string should belong to the original file
  if (!(fileContent['texts'][scene_label]
      && fileContent['texts'][scene_label][textId]))
  {
    error += `<br>Error: ${textId} doesn't exist in the original source file`;
    continue;
  }

  // Update common properties
  fileContent['texts'][scene_label][textId] = {
    ...fileContent['texts'][scene_label][textId],
    ...{
      text: stringObj.text,
      context: stringObj.context || '',
      customData: stringObj.customData || '',
      isHidden: stringObj.isHidden || false,
      labels: stringObj.labels.reverse() || [],
    }
  }

  // Check if new changes are valid
  if (fileContent['texts'][scene_label][textId].labels.length === 0) {
    error += `<br>Error: ${textId} doesn't have any labels`;
  }

  // Add translations if exists
  if (stringObj.translations) {

    for (const lang in stringObj.translations) {
      if (stringObj.translations[lang]
        && stringObj.translations[lang].text)
      {
        fileContent['texts'][scene_label][textId]['translations'][lang] = {
          text: stringObj.translations[lang].text,
          status: stringObj.translations[lang].status,
        }
      }
    }
  }
}

// Enable when debugging
if (exportAsIsStringList) {
  fileContent['strings'] = strings;
}

// Overwrite content with the translated content
// Crowdin will generate a file to download with this content
content = JSON.stringify(fileContent, null, 2);
