//The extainsion was initially meant for tweeter
//that should expain the reference to "tweet"
//like "tweetsender" "searchtweets" as function names


//The below is a function that detects url change events
(() => {
  const hasNativeEvent = Object.keys(window).includes('onurlchange')
  if (!hasNativeEvent) {
    let oldURL = location.href
    setInterval(() => {
      const newURL = location.href
      if (oldURL === newURL) {
        return
      }
      const urlChangeEvent = new CustomEvent('urlchange', {
        detail: {
          oldURL,
          newURL
        }
      })
      oldURL = newURL
      dispatchEvent(urlChangeEvent)
    }, 25)
    addEventListener('urlchange', event => {
      if (typeof (onurlchange) === 'function') {
        onurlchange(event)
      }
    })
  }
})()

window.onurlchange = event => {
  resetState(); //reset the analysis view
  console.log("URL CHANGED");
}


const message_selector_uri = '[data-ad-preview="message"]';
//The above uri comes from pure observation of the facebook 
// website's structure and may break in future if they make
//severe changes(unlikely but may happen)
//In that case find a new uri through observation,Good luck in advance

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
const RESPONSE_THRESHOLD = 0; //unused
const MAX_REQUESTS = 30;    //This is set to deter client from sending 100's of requests
                            //to the server, which would get overloaded
//Increase this to analyse more than 30 posts 
const URL_REGEX_PATTERN = /^https:\/\/www\.facebook\.com\/[\w.]+/;  //unused

//the colors are for representing different type
//of personalities on the wheel
const COLORS = ['#f8d359', '#f78a86', '#edddc2', '#71cae5', '#31dcb2'];

var big5TraitsMap;
var totalReceivedResponses = 0; //This is the number of responses we have recieved from the server
var totalRequest = 0;       // This is number of requests that have been made to server
var chart = null;
var Name,prev="";
var postCount,repostCount,feedCount,imageCount; //names are self explainatory


function init() {   //used for setup when the extension loads
  big5TraitsMap = {
    'Agreeableness':0,
    'Conscientiousness':0,
    'Extraversion':0,
    'Neuroticism':0,
    'Openness':0
  };
  Name="";
  postCount=0;
  repostCount=0;
  feedCount=0;
  imageCount=0;
  totalReceivedResponses = 0;
  totalRequest = 0;
  chart = null;
  prev=location.href;
}

function setTraits(trait) { //called each time a response is recieved from server
  totalReceivedResponses += 1;
  if (big5TraitsMap.hasOwnProperty(trait)) {
    big5TraitsMap[trait]=big5TraitsMap[trait]+ 1;
  }else{
    big5TraitsMap[trait]= 1;
  }
}

const tweetSender = async (Data) => {
  const body = { type: "tweetSender", text: Data }; // Specify the action
  //The below line sends the Data to the background script
  const sending = browser.runtime.sendMessage(body);
  //above returns a Promise
  sending.then(
    function handleResponse(response) {
      if (response?.success && response?.data) {
        // Data Received here
        console.log(response);
        setTraits(response.data);
        setTimeout(createTable,100);
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

const getSummary = () => {  //used to get percentage details for the table columns
  const summary = new Map();
  for (var key in big5TraitsMap) {
    let value=big5TraitsMap[key];
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
  userBox.is_visited=true;
  const exists = tableExists();
  if (!userBox) {
    console.log("Not Found!!!!");
    return;
  }
  var tableWrapper;
  let table = null;

  if (exists) {
    table = document.getElementById(USER_TRAIT_TABLE_ID);
    table.innerHTML = "";
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
    header.classList.add('big_5_header');

    const logo = document.createElement('img');
    logo.setAttribute('src', browser.extension.getURL(LOGO_LINK));
    logo.setAttribute('alt', 'Big-5');
    header.appendChild(logo);

    const title = document.createElement('h4');
    title.innerText = 'BIG-5 Personality Traits';

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

  for (var key in big5TraitsMap) {
    labels.push(key);
    values.push(big5TraitsMap[key]);
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
 //This is the  main function that searches for posts once
 // it detects that current page user is on, is a facebook profile page
  var posts = [];
  const All = document.querySelectorAll(message_selector_uri);

  for (let i = 0; i < All.length; i++) {
    var post;
    try {
      post = All[i];
      if (post.is_visited == true)
        continue;
      posts.push(post);
    } catch (error) {
      continue;
    }
  }

  if (totalRequest < MAX_REQUESTS) {  //this is the guard that stops user from sending more than MAX requests
    for (let Post of posts) {
      if (Post.is_visited) {
        continue;
      }

      const PostText = Post.innerText;
      if (PostText == "")
        continue;

      Post.is_visited = true;
      //console.log(PostText);
      
      //the things done below comes purely from observation of the webpage's structure
      //If this does not make sense console log them and check the conditional logic.
      //The below things are done to know whether the post selected is a Post from user
      //Or a Repost or is a post on their Feed, some other analysis is done to
      //find whether the post has any image/videos attached.

      var par = Post?.parentNode?.parentNode?.parentNode;
      var par2 = Post?.parentNode?.parentNode;
      var t=par2;
      var img_vid= par2?.children[1];
      var pattern = /:.+:/;
      var id = img_vid?.id;

      var secChild = par;
      var firstH2 = secChild?.querySelector('h2');
      var firstH1 = document.querySelector('[role="main"]').querySelector('h1');

      let backgroundColor;
      if (firstH1) {
        var textContent = firstH1.textContent.trim();
        var textContent = firstH1.textContent.trim(); // Get the text content and remove leading/trailing whitespace
        if (textContent.endsWith("account")) {
          var modifiedText = textContent.replace("Verified account", "").trim(); 
          Name=modifiedText; 
        } else {
          Name = textContent;
        }
      } else {
        Name = "";
      }
      console.log(PostText);
      console.log(Name);
      if (firstH2) {
        var L=Name.length;
        var h2Text = firstH2.textContent.trim().slice(0,L);
        
        if (h2Text.startsWith(Name)) {
          backgroundColor = '#b3f0ff';
          postCount+=1;
          if (img_vid && pattern.test(id)) {
            console.log("This is a image/video");
            par2.children[0].prepend(`Image/video found`);
            imageCount++;
          } else {
            console.log("The id does not match the pattern.");
          }
        } else {
          backgroundColor = '#ffcc80';
          feedCount+=1;
          if (img_vid && pattern.test(id)) {
            console.log("This is a image/video");
            par2.children[0].prepend(`Image/video found`);
          } else {
            console.log("The id does not match the pattern.");
          }
        }
      } else {
        backgroundColor = '#99ff99';
        repostCount+=1;
        par2=par2?.parentNode?.parentNode;
        var z=par2?.children[0]?.children[0]?.children[0]?.children[0];
        var link=z.getAttribute('href');
        if(link){
          t.prepend(`Image/vid found`);
        }
      }
      Post.parentNode.style.backgroundColor = backgroundColor;
      
      tweetSender(PostText); 
      totalRequest += 1;

      if (totalRequest >= MAX_REQUESTS) {
        break;
      }
    }
  } else {
    console.log("Max requests over");
  }
}


//Below function is used to reliably detect if current page that user is on 
//is a profile page of some user, then only we start our text analysis
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

//This is the entry point of the extension
window.addEventListener('load', () => {
  console.log("Hello I'm loaded!!!");
  // Entry point
  if(!isFacebookURL(location.href))
    return;
  window.addEventListener('scroll', searchTweets);

  // initialization
  init();
  searchTweets();
});


async function resetState() {
  const userBox = document.getElementById(USER_TRAIT_BOX_ID);
  if (userBox) {
    userBox.remove();
  }

  window.removeEventListener('scroll', searchTweets);
  //If the previous page was a valid profile url
  //we can store the user's analysis
  //uncomment the below two lines to use this feature
  //if(isFacebookURL(prev))
    //await storeDetails(Name, big5TraitsMap,postCount,repostCount,feedCount,imageCount);
  init();
  if (isFacebookURL(window.location)) {
    window.addEventListener('scroll', searchTweets);
  }else{
    console.log("Not facebook url");
  }
}


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
  setTimeout(() => {
    box.remove();
  }, 9000); // 9000 milliseconds = 9 seconds

}


browser.runtime.onMessage.addListener((message) => {
  if (message?.type === 'selected-text-popup') {
      showPopup(message.data);
  }
});


const storeDetails = async (name,data,post,repost,feed,image) => {

 if(!name){
  name='Unaccessable';  //user's name could not be found
  //This is a guard and this condition doesn't occur,but may
 }
 //Finding gender and age of user programatically is possible
 //but takes a lot of resourses on the client side.
  var gender=prompt('Emter gender:');
  var age=prompt("Enter age");
  if(!gender||!age)
    return;
    //The below body structure should have the data required in 'Item' class declared in the api.py file
  const body = {
    type: "storeDetails",
    Name: name,
    Gender: gender,
    Age: age,
    Data: data, 
    Post: post,
    Repost: repost,
    Feed: feed,
    Image:image
  };
  console.log(body);
  //the below sends the data to the background script
  const sending = browser.runtime.sendMessage(body);
  sending.then(
    function handleResponse(response) {
      if (response?.success && response?.data) {
        // Data Received here
        console.log(response);
      }
    },
    function handleError(e) {
      console.log(e);
    }
  );
};

