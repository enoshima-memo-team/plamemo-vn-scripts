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

/**
 * Forced languages are required when Crowdin doesn't send
 * the `targetLanguages` array when uploading the generated
 * .json files
 */
const useForcedLanguages = true;
const forcedTargetLanguages = [
  {id: 'en'},
  {id: 'ja'},
  {id: 'es-ES'},
];

/**
 * For adding the whole string data in the
 * 'context' field of each string
 */
const enableDebugContext = false;


/**
 * Build the data for a string to be translated in Crowdin
 *
 * Set `enableDebugContext` as true if you want to set the whole
 * string data in its `context` field
 *
 * @returns   Data for the string with the expected Crowdin fields
 */
const buidlstringObjData = function(item, itemId) {
  const stringObj = {
    identifier: itemId,
    text: item.text,
    labels: item.labels,
    isHidden: item.isHidden || false,

    // Context, normally original lang context
    context: item.context,

    // Max 4k of custom data
    customData: item.customData,

    // Translations per lang
    translations: {}
  };


  // If importing translations
  const languages = (!useForcedLanguages ? targetLanguages : forcedTargetLanguages) || [];

  // Error if no languages set
  if (languages.length === 0) {
    throw new Error('Error: languages list is empty');
  }

  // Add translations
  let contexTranslations = {};
  if (languages.length > 0) {

    stringObj.translations = {};
    for (const lang of languages) {

      // Continue if target translation doesn't exist
      if (!Object.keys(item.translations).includes(lang.id)) {
        continue;
      }

      const translation = item.translations[lang.id];
      stringObj.translations[lang.id] = {
        text: translation.text,
        status: translation.status || 'untranslated' // Default status
      };

      contexTranslations[lang.id] = stringObj.translations[lang.id];
    }
  }

  // Indirectly debug sending data to "context" entry
  if (enableDebugContext) {
    // replace the context with only translations and original item
    contexTranslations['item'] = item;
    stringObj['context'] = JSON.stringify(contexTranslations);

    // ... or add the whole string data to the context
    // stringObj['context'] = JSON.stringify({
    //   ...stringObj
    //   ...contexTranslations
    // });
  }

  return stringObj;
}


// Get the uploaded source file
const contentObj = JSON.parse(content);

try {
  // Build the string lists
  for (const texts of Object.values(contentObj['texts'])) {
    for (const textId in texts) {
      strings.push(buidlstringObjData(texts[textId], textId));
    }
  }

} catch (e) {
  // Set error variable for Crowdin
  error = e.message || 'Error: error processing strings';
}
