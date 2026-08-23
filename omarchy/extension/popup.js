document.getElementById('resolve').addEventListener('click', async () => {
  const status = document.getElementById('status');
  status.textContent = 'Resolving…';
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.url?.startsWith('https://') || tab.url.includes('?') || tab.url.includes('#')) {
    status.textContent = 'Only a clean HTTPS public pointer is supported.';
    return;
  }
  const result = await chrome.runtime.sendMessage({ type: 'humain-resolve', pointer: tab.url });
  status.textContent = result.ok ? `Resolved: ${result.payload.resolution_state}` : `Unavailable: ${result.error || result.payload?.error || 'error'}`;
  if (tab.id) chrome.tabs.sendMessage(tab.id, { type: 'humain-result', ...result });
});
