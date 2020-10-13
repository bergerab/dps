function nameNeedsIdentifier(name) {
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

function getIdentifier(kpiName, kpiIdentifier) {
  if (kpiIdentifier) {
    return kpiIdentifier;
  }
  if (nameNeedsIdentifier(kpiName)) {
    return null;
  }
  return kpiName;
}

function objectIsEmpty(obj) {
  if (obj === undefined) return true;
  if (obj === null) return true;
  return Object.keys(obj).length === 0;
}

function objectPop(obj, key, _default=null) {
  const temp = obj[key];
  delete obj[key];
  return temp === undefined ? _default : temp;
}

export default {
  nameNeedsIdentifier,
  getIdentifier,
  objectIsEmpty,
  objectPop,
};
