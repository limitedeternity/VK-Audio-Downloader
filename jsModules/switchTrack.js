var element = window.__audioIterator.next();

if (element && !window.__noPlayback) {
  element.click();
  return true;

} else {
  return false;
}
