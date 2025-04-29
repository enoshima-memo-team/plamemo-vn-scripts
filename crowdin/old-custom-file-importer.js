/**
 * Crowdin - Custom file importer
 *
 * @see https://store.crowdin.com/cff
 * @see https://support.crowdin.com/developer/crowdin-apps-module-custom-file-format/#strings-array-structure
 */

/**
 * Available and already defined "env" variables
 *
 * - strings: A global variable, an empty array where your code should populate
 *     Crowdin string objects.
 * - content: Contains the source file content in UTF-8 encoding.
 * - error: Set this variable to a string if your code encounters an
 *     error and cannot form the strings array.
 * - fileName: The name of the source file (e.g., 'source-file.json').
 * - filePath: The file path within the Crowdin project (e.g., '/main/source-file.json').
 * - fileId: The unique ID for the file in Crowdin.
 * - targetLanguages: An array of objects containing details about each target language.
 */

const contentObj = JSON.parse(content);

for (const scene of Object.values(contentObj['texts'])) {
  for (const textId in scene) {

    const item = scene[textId];
    const stringObj = {
      identifier: textId,
      text: item.text,
      context: item.context,
      labels: item.labels,
      isHidden: item.isHidden || false,

      // Max 4k of custom data
      customData: item.customData
    };


    // If importing translations
    if (ourTargetLanguages.length > 0) {

      stringObj.translations = {};
      for (const lang of ourTargetLanguages) {

        // Continue if target translation doesn't exist
        if (!Object.keys(item.translations).includes(lang.id)) {
          continue;
        }

        stringObj.translations[lang.id] = {
          text: item.text,
          status: item.status || 'untranslated' // Default status
        };
      }
    }

    strings.push(stringObj);
  }
}
