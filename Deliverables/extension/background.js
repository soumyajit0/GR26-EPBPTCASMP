chrome.runtime.onInstalled.addListener(() => {
  console.log('Facebook Post Scraper extension installed');
});

// Listen for messages from the content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'sendPost') {
    fetch('http://localhost:8090/api', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url:request.url,text: request.postText, imgs:request.imgs})
    })
    .then(response => response.json())
    .then(data => {
      sendResponse({ success: true });
    })
    .catch(error => {
      console.error('Error sending post:', error);
      sendResponse({ success: false });
    });
    return true; // Indicates async response
  }
  else if (request.action === 'sendName'){
    fetch('http://localhost:8090/send_name', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({url:request.url, name: request.Name,dp:request.dp })
    })
    .then(response => response.json())
    .then(data => {
      sendResponse({ success: true });
    })
    .catch(error => {
      console.error('Error sending name:', error);
      sendResponse({ success: false });
    });
    return true; // Indicates async response
  }
  else if (request.action === 'Reset'){
    fetch('http://localhost:8090/reset')
    .catch(error => {
      console.error('Error sending name:', error);
      sendResponse({ success: false });
    });
    return true; // Indicates async response
  }
});


