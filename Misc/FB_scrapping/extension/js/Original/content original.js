
const USER_TRAIT_BOX_ID = 'big5-user-traits-box';
const USER_TRAIT_TABLE_ID = 'big5-user-traits-table';
const USER_TRAIT_CHART_ID = 'big5-user-traits-chart';
const USER_TRAIT_CLOSE_CHART_ID = 'big5-user-traits-chart';
const TRAITS = [
  'Agreeableness',
  'Conscientiousness',
  'Extraversion',
  'Neuroticism',
  'Openness'
];
const LOGO_LINK = 'assets/icon.png';
const RESPONSE_THRESHOLD = 2;
const MAX_REQUESTS = 30;
const URL_REGEX_PATTERN = /^https:\/\/twitter\.com\/[^\/\?]+$/;
const COLORS = ['#f8d359', '#f78a86', '#edddc2', '#71cae5', '#31dcb2'];

var big5TraitsMap = new Map();
var totalReceivedResponses = 0;
var totalRequest = 0;
var chart = null;

function init() {
  big5TraitsMap = new Map();
  for (let trait of TRAITS) {
    big5TraitsMap.set(trait, 0);
  }
  totalReceivedResponses = 0;
  totalRequest = 0;
  chart = null;
}

function setTraits(trait) {
  if (big5TraitsMap.has(trait)) {
    big5TraitsMap.set(trait, big5TraitsMap.get(trait) + 1);
    totalReceivedResponses += 1;
  }
}

const tweetSender = async (Data) => {
  const body = { text: Data  };
  console.log(body);
  const sending = browser.runtime.sendMessage(body);
  sending.then(
    function handleResponse(response) {
      if (response?.success && response?.data) {
        // Data Receviced here
        console.log(response)
        setTraits(response.data);

        if (totalReceivedResponses > RESPONSE_THRESHOLD) {
          createTable();
        }
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
  if (box) {
    return true;
  }
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
  const summary = new Map();
  for (let [key, value] of big5TraitsMap) {
    if (big5TraitsMap.has(key)) {
      const percent = (value / totalReceivedResponses) * 100;
      summary.set(key, percent.toFixed(2));
    }
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
  const userBox = document.querySelector('[data-testid="UserName"');

  if (!userBox) {
    return;
  }

  const tableWrapper = document.createElement('div');
  tableWrapper.setAttribute('id', USER_TRAIT_BOX_ID);

  const header = document.createElement('div');
  header.classList.add('big_5_header');

  const logo = document.createElement('img');
  logo.setAttribute('src', browser.extension.getURL(LOGO_LINK));
  logo.setAttribute('alt', 'Big-5');
  header.appendChild(logo);

  const title = document.createElement('h4');
  title.innerText = 'BIG-5 Personality Traits';

  header.appendChild(title);
  tableWrapper.appendChild(header);

  let table = null;

  const exists = tableExists();
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
    const chart = document.createElement('div');
    chart.setAttribute('id', USER_TRAIT_CHART_ID);

    const content = document.createElement('div');

    content.appendChild(table);
    content.appendChild(chart);
    tableWrapper.appendChild(content);
    const tnc = document.createElement('small');
    tnc.setAttribute('id', 'tnc');
    tnc.innerText = `*Analysis based on the last ${totalReceivedResponses} tweets of the user.`;
    tableWrapper.appendChild(tnc);
    userBox.appendChild(tableWrapper);
  } else {
    document.getElementById(
      'tnc'
    ).innerText = `*Analysis based on the last ${totalReceivedResponses} tweets of the user.`;
  }

  renderChart();
};

function renderChart() {
  const values = [];
  const labels = [];

  for (let [key, value] of big5TraitsMap) {
    labels.push(key);
    values.push(value);
  }

  const options = {
    chart: {
      type: 'pie',
      toolbar: {
        show: false
      }
    },
    series: values,
    labels: labels,
    legend: {
      show: false
    },
    colors: COLORS
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
  // console.log('Searching tweets...');
  var tweets = [];
  let name = document.querySelector('[data-testid="User-Name"]');
  const Name=name.innerText.split('\n')[0];
  const All = document.querySelectorAll('[data-testid="tweet"]');
  var Date="";
  for (let i = 0; i < All.length; i++) {
    var img_text = "";
    var Tweet = "";
    try {
      Tweet = All[i].querySelector('[data-testid="tweetText"]');
      var image = All[i].querySelector('[data-testid="tweetPhoto"]').querySelector('img');
      var date = All[i].querySelector('time');
      Date=date.dateTime.substring(0,19);
      if (image){
        img_text = image.alt;
      }
    
    } catch (error) {
      continue;
    } finally {
      tweets.push([Tweet, img_text,Name,Date]);
    }
  }



  
  if (totalRequest < MAX_REQUESTS) {
    for (let Tweet of tweets) {
      let tweet=Tweet[0];
      if (tweet.dataset.is_visited) {
        return;
      }

      const tweetText = (tweet.innerText.concat(" ")).concat(Tweet[1]);
      // console.log({ tweetText });
      tweet.dataset.is_visited = true;

      tweetSender(tweetText.concat("$@$@$"+Tweet[2]).concat("$@$@$"+Tweet[3])); //"$@$@$" has been choosen as delimiter
      totalRequest += 1;

      if (totalRequest >= MAX_REQUESTS) {
        break;
      }
    }
  }

  const doc = document.documentElement;
  const top = (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);

  const wrapper = document.getElementById(USER_TRAIT_BOX_ID);

  if (!wrapper) return;

  if (top > 500) {
    wrapper.classList.add('float_right');
  } else {
    wrapper.classList.remove('float_right');
  }
}

window.addEventListener('load', () => {
  console.log("Hello I'm loaded!!!");


  if (!URL_REGEX_PATTERN.test(window.location)) return;

  // Entry point
  window.addEventListener('scroll', searchTweets);

  // initialization
  init();

  searchTweets();
});

function resetState() {
  const userBox = document.getElementById(USER_TRAIT_BOX_ID);
  if (userBox) {
    userBox.remove();
  }

  window.removeEventListener('scroll', searchTweets);
  init();

  if (URL_REGEX_PATTERN.test(window.location)) {
    window.addEventListener('scroll', searchTweets);
  }
}

// Route change handler
let url = location.href;
document.body.addEventListener(
  'click',
  () => {
    requestAnimationFrame(() => {
      if (url !== location.href) {
        // console.log('URL changed');
        url = location.href;
        resetState();
      }
    });
  },
  true
); 
function showPopup(data) {
  const box = document.createElement('div');
  box.setAttribute('class', 'big_5_selected_text_analysis_box');

  const color = COLORS[TRAITS.indexOf(data)];

  box.innerHTML = `
    <h3 class="title">
      <span>Big-5 analysis on the selected text.</span>
    </h3>
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
}

browser.runtime.onMessage.addListener((message) => {
  if (message?.type === 'selected-text-popup') {
      showPopup(message.data);
  }
});