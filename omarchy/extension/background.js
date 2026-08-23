const DEFAULT_ENDPOINT = 'http://127.0.0.1:8787/v1/context';

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type !== 'humain-resolve') return undefined;
  const pointer = String(message.pointer || '');
  if (!pointer.startsWith('https://') || pointer.includes('?') || pointer.includes('#')) {
    sendResponse({ ok: false, error: 'only clean HTTPS public pointers are accepted' });
    return false;
  }
  chrome.storage.local.get({ endpoint: DEFAULT_ENDPOINT }, async ({ endpoint }) => {
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pointer, requester: 'omarchy-browser' })
      });
      const payload = await response.json();
      sendResponse({ ok: response.ok, payload });
    } catch (error) {
      sendResponse({ ok: false, error: 'local adapter unavailable' });
    }
  });
  return true;
});
