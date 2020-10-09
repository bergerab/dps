export function nameNeedsIdentifier(name) {
  name = name.trim();
  const illegalChars = ' !@#$%^&*<>?,./][{}\'"\\=+|-~`()';
  for (const illegalChar of illegalChars) {
    if (name.includes(illegalChar)) {
      return true;
    }
  }
  const illegalStartingChars = '1234567890';
  for (const illegalStartingChar of illegalStartingChars) {
    if (name.startsWith(illegalStartingChar)) {
      return true;
    }
  }
  return false;
}
