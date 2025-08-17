// Importer Code
const contentObj = JSON.parse(content);

for (const key in contentObj) {
  const item = contentObj[key];
  const stringObj = {
    identifier: key,
    text: item.message,
    context: item.description || null,  // Optional: Only include context if it's provided
  };

  // If importing translations
  if (targetLanguages.length > 0) {
    stringObj.translations = {};
    for (const lang of targetLanguages) {
      stringObj.translations[lang.id] = {
        text: item.message, // Assuming that the source text is the same as the translated text if not translated
        status: "untranslated" // Default status
      };
    }
  }

  strings.push(stringObj);
}