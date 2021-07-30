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
  if (kpiIdentifier || kpiName === undefined || kpiName === null) {
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
  //delete obj[key];
  return temp === undefined ? _default : temp;
}

function arrayEqual(a1, a2) {
  return JSON.stringify(a1) === JSON.stringify(a2);
}

function dateToString(dt) {
  try {
  if (!(dt instanceof Date)) { // if it is a moment object
    dt = dt.toDate();
  }
  return `${dt.getUTCFullYear()}-${numPad2(dt.getUTCMonth() + 1)}-${numPad2(dt.getUTCDate())} ${numPad2(dt.getUTCHours())}:${numPad2(dt.getUTCMinutes())}:${numPad2(dt.getUTCSeconds())}.${dt.getUTCMilliseconds()}`    
  } catch {
    return '';
  }
}

function dateToPrettyDate(dt) {
  return dt.toLocaleDateString('en-US') + ' ' + dt.toLocaleTimeString('en-US');
}

function dateToUTCDate(dt) {
  dt = Date.UTC(dt.getUTCFullYear(), dt.getUTCMonth(), dt.getUTCDate(),
		dt.getUTCHours(), dt.getUTCMinutes(), dt.getUTCSeconds());
  return new Date(dt);
}

function stringToUTCDate(s) {
  const dt = new Date(s);
  const os = dt.getTimezoneOffset();
  var d = new Date((dt.getTime() - (os * 60 * 1000)));
  return d;
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
  stringToUTCDate,  
  dateToUTCDate,
  dateToPrettyDate,
};
