(async function() {
  const response = await fetch('/requests');
  const data = await response.json();
  const pre = document.body.appendChild(document.createElement('pre'))
  if ('requests' in data) {
    pre.textContent = data['requests'].map(v => [v.value == 1 ? 'OPEN ' : 'CLOSE', ...[v.date, v.created].map(v => new Date(v * 1000).toISOString())].join(',')).join('\n');
  }
})();
