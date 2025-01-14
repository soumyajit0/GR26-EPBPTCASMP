const API_URL = 'http://127.0.0.1:8000/api';

// Listener for messages from content script
browser.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
  // console.log({ message, sender, sendResponse });

  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(message)
  };

  return new Promise(async (resolve) => {
    // Send the selectedText to the API
    const res = await fetch(API_URL, options);
    if (!res.ok) {
      resolve({ success: false, data: null });
      return;
    }

    const response = await res.json();

    // TODO: Perform necessary processing and send the result back to the content script
    resolve({ success: true, data: response?.data });
  });
});

browser.tabs.onUpdated.addListener(function (tabId, changeInfo, tab) {
  if (changeInfo.status === 'complete' && tab.active) {
    if (tab.url.startsWith('https://twitter.com/')) {
      browser.browserAction.setPopup({ popup: 'popup.html' });
    } else {
      browser.browserAction.setPopup({ popup: 'newtab.html' });
    }
  }
});

// Context menu creation
browser.contextMenus.create({
  id: 'bigFiveContextMenu',
  title: 'BIG 5',
  contexts: ['selection']
});

// Context menu click listener
browser.contextMenus.onClicked.addListener(function (info, tab) {
  if (info.menuItemId === 'bigFiveContextMenu') {
    const selectedText = info.selectionText;
    const body = { text: selectedText };

    // Send the selectedText to the API
    fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })
      .then((response) => response.json())
      .then((data) => {
        // Handle the API response data
        console.log('API response:', data);
        browser.tabs.sendMessage(tab.id, { type: 'selected-text-popup', data: data.data });
      })
      .catch((error) => {
        // Handle API errors
        console.error('API Error:', error);
      });
  }
});