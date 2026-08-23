(() => {
  if (window.top !== window) return;
  const ID = 'humain-os-lens-overlay';

  function render(result) {
    document.getElementById(ID)?.remove();
    const box = document.createElement('aside');
    box.id = ID;
    box.setAttribute('role', 'status');
    box.innerHTML = `<strong>HumAIn OS Lens</strong><br>${result}`;
    Object.assign(box.style, {
      position: 'fixed', zIndex: '2147483647', right: '16px', bottom: '16px',
      maxWidth: '360px', padding: '12px 14px', borderRadius: '10px',
      background: '#111827', color: '#f9fafb', font: '13px/1.4 system-ui',
      boxShadow: '0 8px 30px #0008'
    });
    document.body.appendChild(box);
    setTimeout(() => box.remove(), 10000);
  }

  chrome.runtime.onMessage.addListener((message) => {
    if (message?.type !== 'humain-result') return;
    if (!message.ok) return render(`Unavailable: ${message.error || 'resolver error'}`);
    const p = message.payload;
    render(`State: ${p.resolution_state}<br>Pointer: ${p.pointer}<br>No private context or actions.`);
  });
})();
