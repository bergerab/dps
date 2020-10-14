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

function arrayEqual(a1, a2) {
  return JSON.stringify(a1) === JSON.stringify(a2);
}

function dateToString(dt) {
  if (!(dt instanceof Date)) { // if it is a moment object
    dt = dt.toDate();
  }
  return `${dt.getUTCFullYear()}-${numPad2(dt.getUTCMonth())}-${numPad2(dt.getUTCDate())} ${numPad2(dt.getUTCHours())}:${numPad2(dt.getUTCMinutes())}:${numPad2(dt.getUTCSeconds())}.${dt.getUTCMilliseconds()}`    
}

function numPad2(n) {
  return ('0' + n).slice(-2);
}

export default {
  nameNeedsIdentifier,
  getIdentifier,
  objectIsEmpty,
  objectPop,
  arrayEqual,
  dateToString,  
};
