


// The extension was initially meant for Twitter
// that should explain the reference to "tweet"
// like "tweetSender" "searchTweets" as function names

// The below is a function that detects URL change events
(() => {
  const hasNativeEvent = Object.keys(window).includes('onurlchange');
  if (!hasNativeEvent) {
    let oldURL = location.href;
    setInterval(() => {
      const newURL = location.href;
      if (oldURL === newURL) {
        return;
      }
      const urlChangeEvent = new CustomEvent('urlchange', {
        detail: {
          oldURL,
          newURL,
        },
      });
      oldURL = newURL;
      dispatchEvent(urlChangeEvent);
    }, 25);
    addEventListener('urlchange', (event) => {
      if (typeof onurlchange === 'function') {
        onurlchange(event);
      }
    });
  }
})();

window.onurlchange = (event) => {
  resetState(); // reset the analysis view
  console.log('URL CHANGED');
};

const message_selector_uri = '[data-ad-preview="message"]';
// The above uri comes from pure observation of the Facebook
// website's structure and may break in future if they make
// severe changes (unlikely but may happen)
// In that case find a new uri through observation, Good luck in advance

const USER_TRAIT_BOX_ID = 'mbti-user-traits-box';
const USER_TRAIT_TABLE_ID = 'mbti-user-traits-table';
const USER_TRAIT_CHART_ID = 'mbti-user-traits-chart';
const USER_TRAIT_CLOSE_CHART_ID = 'mbti-user-traits-chart';
var TRAITS = ['I', 'E', 'S', 'N', 'T', 'F', 'J', 'P'];

const LOGO_LINK = 'assets/icon.png';
const RESPONSE_THRESHOLD = 0; // unused
const MAX_REQUESTS = 30; // This is set to deter client from sending 100's of requests
// to the server, which would get overloaded
// Increase this to analyze more than 30 posts
const URL_REGEX_PATTERN = /^https:\/\/www\.facebook\.com\/[\w.]+/; // unused

// The colors are for representing different MBTI dichotomies on the wheel
const COLORS = ['#f8d359', '#f78a86', '#edddc2', '#71cae5', '#31dcb2'];

var mbtiTraitsMap;
var totalReceivedResponses = 0; // This is the number of responses we have received from the server
var totalRequest = 0; // This is the number of requests that have been made to the server
var chart = null;
var Name,
  prev = '';
var postCount,
  repostCount,
  feedCount,
  imageCount; // names are self-explanatory

function init() {
  // used for setup when the extension loads
  mbtiTraitsMap = {
    INFJ: 0,
    ENTP: 0,
    INTP: 0,
    INTJ: 0,
    ENTJ: 0,
    ENFJ: 0,
    INFP: 0,
    ENFP: 0,
    ESTP: 0,
    ESTJ: 0,
    ESFJ: 0,
    ISTP: 0,
    ISFP: 0,
    ISFJ: 0,
    ISTJ: 0,
    ESFP: 0
  };
  Name = '';
  postCount = 0;
  repostCount = 0;
  feedCount = 0;
  imageCount = 0;
  totalReceivedResponses = 0;
  totalRequest = 0;
  chart = null;
  prev = location.href;
}

function setTraits(trait) {
  // called each time a response is received from the server
  totalReceivedResponses += 1;
  if (mbtiTraitsMap.hasOwnProperty(trait)) {
    mbtiTraitsMap[trait] += 1;
  } else {
    mbtiTraitsMap[trait] = 1;
  }
}

const tweetSender = async (Data) => {
  const body = { type: 'tweetSender', text: Data }; // Specify the action
  // The below line sends the Data to the background script
  const sending = browser.runtime.sendMessage(body);
  // above returns a Promise
  sending.then(
    function handleResponse(response) {
      if (response?.success && response?.data) {
        // Data Received here
        console.log(response);
        setTraits(response.data);
        setTimeout(createTable, 100);
      }
    },
    function handleError(e) {
      console.log(e);
    }
  );
};

const tableExists = () => {
  // check if the user personality traits table exists in the DOM
  const box = document.getElementById(USER_TRAIT_TABLE_ID);
  if (box) 
    return true;
  return false;
};


const setTableHeader = (table) => {
  const th1 = document.createElement('th');
  th1.innerText = 'Trait';

  const th2 = document.createElement('th');
  th2.innerText = 'Percentage';

  const thead = document.createElement('tr');
  thead.appendChild(th1);
  thead.appendChild(th2);

  table.appendChild(thead);
};

const getSummary = () => {
  // used to get percentage details for the table columns
  const summary = new Map();
  for (var key in mbtiTraitsMap) {
    let value = mbtiTraitsMap[key];
    const percent = (value / totalReceivedResponses) * 100;
    summary.set(key, percent.toFixed(2));
  }
  return summary;
};

const setTableRows = (table) => {
  const summary = getSummary();
  for (let [key, value] of summary) {
    const row = document.createElement('tr');
    const td1 = document.createElement('td');
    const td2 = document.createElement('td');

    td1.innerText = key;
    td2.innerText = `${value}%`;

    row.appendChild(td1);
    row.appendChild(td2);

    table.appendChild(row);
  }
};

const createTable = () => {
  const userBox = document.querySelector(message_selector_uri);
  userBox.is_visited = true;
  const exists = tableExists();
  if (!userBox) {
    console.log('Not Found!!!!');
    return;
  }
  var tableWrapper;
  let table = null;

  if (exists) {
    table = document.getElementById(USER_TRAIT_TABLE_ID);
    table.innerHTML = '';
  } else {
    table = document.createElement('table');
    table.setAttribute('id', USER_TRAIT_TABLE_ID);
  }
  setTableHeader(table);
  setTableRows(table);

  if (!exists) {
    tableWrapper = document.createElement('div');
    tableWrapper.setAttribute('id', USER_TRAIT_BOX_ID);
    tableWrapper.classList.add('float_right');

    const header = document.createElement('div');
    header.classList.add('mbti_header');

    const logo = document.createElement('img');
    logo.setAttribute('src', browser.extension.getURL(LOGO_LINK));
    logo.setAttribute('alt', 'MBTI');
    header.appendChild(logo);

    const title = document.createElement('h4');
    title.innerText = 'MBTI Personality Traits';

    header.appendChild(title);
    tableWrapper.appendChild(header);
    const chart = document.createElement('div');
    chart.setAttribute('id', USER_TRAIT_CHART_ID);
    const content = document.createElement('div');
    content.appendChild(table);
    content.appendChild(chart);
    tableWrapper.appendChild(content);
    const tnc = document.createElement('small');
    tnc.setAttribute('id', 'tnc');
    tnc.innerText = `*Analysis based on the last ${totalReceivedResponses} Posts of the user.`;
    tableWrapper.appendChild(tnc);
    userBox.prepend(tableWrapper);
  } else {
    document.getElementById(
      'tnc'
    ).innerText = `*Analysis based on the last ${totalReceivedResponses} Posts of the user.`;
  }

  renderChart();
};

function renderChart() {
  const values = [];
  const labels = [];

  for (var key in mbtiTraitsMap) {
    labels.push(key);
    values.push(mbtiTraitsMap[key]);
  }

  const options = {
    chart: {
      type: 'pie',
      toolbar: {
        show: false,
      },
    },
    series: values,
    labels: labels,
    legend: {
      show: false,
    },

    colors: COLORS,
  };

  const ele = document.querySelector(
    `#${USER_TRAIT_CHART_ID} .apexcharts-canvas`
  );

  if (ele) {
    chart.updateSeries(values);
  } else {
    chart = new ApexCharts(
      document.querySelector('#' + USER_TRAIT_CHART_ID),
      options
    );
    chart.render();
  }
}

function searchTweets() {
  // This is the main function that searches for posts once
  // it detects that current page user is on, is a Facebook profile page
  var posts = [];
  const All = document.querySelectorAll(message_selector_uri);

  for (let i = 0; i < All.length; i++) {
    var post;
    try {
      post = All[i];
      if (post.is_visited == true) continue;
      posts.push(post);
    } catch (error) {
      continue;
    }
  }

  if (totalRequest < MAX_REQUESTS) {
    for (let Post of posts) {
      if (Post.is_visited) continue;
      const PostText = Post.innerText;
      if (PostText == '') continue;
      Post.is_visited = true;
      tweetSender(PostText);
      totalRequest += 1;
      if (totalRequest >= MAX_REQUESTS) break;
    }
  } else {
    console.log('Max requests over');
  }
}

async function resetState() {
  const userBox = document.getElementById(USER_TRAIT_BOX_ID);
  if (userBox) {
    userBox.remove();
  }

  window.removeEventListener('scroll', searchTweets);
  init();
  if (isFacebookURL(window.location)) {
    window.addEventListener('scroll', searchTweets);
  } else {
    console.log('Not facebook url');
  }
}

function isFacebookURL(url) {
  if (url =="https://www.facebook.com/")//This is the homepage url
    return false;
  // Regular expressions to match different Facebook URL patterns
  const patterns = [
    /^https:\/\/www\.facebook\.com\/(?!$)(.*)/,
    /^https:\/\/www\.facebook\.com\/profile\.php\?id=\d+$/,
  ];

  return patterns.some(pattern => pattern.test(url));
}


function showPopup(data) {
  // This function shows a temporary pop-up on the screen, this is called when
  // the selected text's MBTI analysis is done.
  const box = document.createElement('div');
  box.setAttribute('class', 'mbti_selected_text_analysis_box');
  const color = COLORS[TRAITS.indexOf(data)];
  box.innerHTML = `
    <h3 class="title"><span>MBTI analysis on the selected text.</span></h3>
    <h2 class="prediction" style="color: ${color};">${data}</h2>
    <small>*Analysis based on the selected text.</small>
  `;
  const closeBtn = document.createElement('button');
  closeBtn.innerHTML = '&#10005;';
  closeBtn.addEventListener('click', () => {
    box.remove();
  });
  box.querySelector('h3').appendChild(closeBtn);
  document.querySelector('body').appendChild(box);
  setTimeout(() => {
    box.remove();
  }, 9000);
}

browser.runtime.onMessage.addListener((message) => {
  if (message?.type === 'selected-text-popup') {
    showPopup(message.data);
  }
});
