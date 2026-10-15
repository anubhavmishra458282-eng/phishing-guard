document.addEventListener('DOMContentLoaded', async () => {
  const urlDisplay = document.getElementById('urlDisplay');
  const scanBtn = document.getElementById('scanBtn');
  const resultBox = document.getElementById('resultBox');
  const badge = document.getElementById('badge');
  const score = document.getElementById('score');
  const signals = document.getElementById('signals');

  let currentUrl = '';

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.url) {
      currentUrl = tab.url;
      urlDisplay.textContent = currentUrl;
    } else {
      urlDisplay.textContent = 'Cannot inspect this page.';
      scanBtn.disabled = true;
    }
  } catch (err) {
    urlDisplay.textContent = 'Error reading active URL.';
    scanBtn.disabled = true;
  }

  scanBtn.addEventListener('click', async () => {

    scanBtn.disabled = true;
    scanBtn.textContent = 'Analyzing link...';
    resultBox.style.display = 'none';

    try {
      const response = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: currentUrl })
      });

      const data = await response.json();

      resultBox.style.display = 'block';
      score.textContent = `Risk Score: ${data.risk_score} / 100`;

      if (data.classification === 'Phishing') {
        resultBox.style.background = '#fee2e2';
        badge.style.background = '#dc2626';
        badge.style.color = '#fff';
        badge.textContent = '⚠️ PHISHING DETECTED';
      } else if (data.classification === 'Suspicious') {
        resultBox.style.background = '#fef3c7';
        badge.style.background = '#d97706';
        badge.style.color = '#fff';
        badge.textContent = '⚡ SUSPICIOUS URL';
      } else {
        resultBox.style.background = '#dcfce7';
        badge.style.background = '#16a34a';
        badge.style.color = '#fff';
        badge.textContent = '✅ SAFE LINK';
      }

      signals.innerHTML = '';
      if (data.signals && data.signals.length > 0) {
        data.signals.forEach(sig => {
          const li = document.createElement('li');
          li.textContent = sig;
          signals.appendChild(li);
        });
      } else {
        const li = document.createElement('li');
        li.textContent = 'No structural threat detected.';
        li.style.color = '#16a34a';
        signals.appendChild(li);
      }
    } catch (err) {
      alert('Backend offline! Ensure FastAPI server is running on port 8000.');
    } finally {
      scanBtn.disabled = false;
      scanBtn.textContent = 'Scan Current Page';
    }
  });
});
