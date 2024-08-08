
//This adds a listener to catch incomng requests from the content.js script
const url = 'http://127.0.0.1:8090'
//change IP and port as necessary
browser.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
  if (message.type === "storeDetails") {
    // Handle storing details
    const URL = `${url}/register`; 
    // Listener for messages from content script
    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      //The below body will be sent to the server for storage
      // the structure of the body must match that of what is 
      //declared in the Item class of api.py
      body: JSON.stringify({
        'Name': message.Name, 'Gender': message.Gender, 'Age': message.Age,
        'Data': message.Data, 'Post': message.Post,'Repost':message.Repost,
        'Feed':message.Feed,"Image":message.Image })
    };
    return new Promise(async (resolve) => {
      // Send the selectedText to the API
      const res = await fetch(URL, options);
      if (!res.ok) {
        resolve({ success: false, data: null });
        return;
      }
      const response = await res.json();
      // Perform necessary processing and send the result back to the content script
      resolve({ success: true, data: response?.data });
    });

  
  } else if (message.type === "tweetSender") {  
    // The extension was originally made for tweeter
    // that explains the name of the message.type
    const API_URL = `${url}/api`;

    // Listener for messages from content script

    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({'text':message.text})
    };

    return new Promise(async (resolve) => {
      // Send the selectedText to the API
      const res = await fetch(API_URL, options);
      if (!res.ok) {
        resolve({ success: false, data: null });
        return;
      }

      const response = await res.json();

      // Perform necessary processing and send the result back to the content script
      resolve({ success: true, data: response?.data });
    });

  }
});


browser.tabs.onUpdated.addListener(function (tabId, changeInfo, tab) {
  if (changeInfo.status === 'complete' && tab.active) {
    if (tab.url.startsWith('https://www.facebook.com')) {
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
//this function handles manual analysis of text
// initiated by selecting and clicking the extension icon
browser.contextMenus.onClicked.addListener(function (info, tab) {
  var API_URL = `${url}/api`;
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