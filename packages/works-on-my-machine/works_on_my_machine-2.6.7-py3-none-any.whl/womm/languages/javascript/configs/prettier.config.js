// Prettier configuration for JavaScript/TypeScript projects
module.exports = {
  // Print width (line length)
  printWidth: 80,

  // Tab width
  tabWidth: 2,

  // Use tabs instead of spaces
  useTabs: false,

  // Add semicolons at the end of statements
  semi: true,

  // Use single quotes instead of double quotes
  singleQuote: true,

  // Quote props in objects only when needed
  quoteProps: 'as-needed',

  // Use single quotes in JSX
  jsxSingleQuote: true,

  // Trailing commas
  trailingComma: 'es5',

  // Spaces between brackets in object literals
  bracketSpacing: true,

  // Put the `>` of a multi-line JSX element at the end of the last line
  bracketSameLine: false,

  // Arrow function parentheses
  arrowParens: 'avoid',

  // Range formatting (entire file)
  rangeStart: 0,
  rangeEnd: Infinity,

  // Parser (auto-detect)
  parser: undefined,

  // File path (for parser inference)
  filepath: undefined,

  // Require pragma
  requirePragma: false,

  // Insert pragma
  insertPragma: false,

  // Prose wrap
  proseWrap: 'preserve',

  // HTML whitespace sensitivity
  htmlWhitespaceSensitivity: 'css',

  // Vue files script and style tags indentation
  vueIndentScriptAndStyle: false,

  // Line ending
  endOfLine: 'lf',

  // Embedded language formatting
  embeddedLanguageFormatting: 'auto',

  // Single attribute per line in HTML, Vue and JSX
  singleAttributePerLine: false,
};