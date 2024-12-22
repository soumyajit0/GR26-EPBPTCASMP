const message_selector_uri = '[data-ad-preview="message"]';
const more_link_selector = 'a[href*="more"]'; // Selector for the "see more" link

const MAX_REQUESTS = 30;
let totalRequest = 0;
async function check_for_image(post) {
  let p1 = post?.parentElement?.parentElement?.parentElement;
  console.log(p1);
  // Proceed to the next lines only if p1 exists
  if (!p1) {
    return Promise.resolve([]);
  }

  let d1 = p1;
  let imagesInDiv = d1.querySelectorAll('img');

  // Create a list containing all img.src
  let imgSrcs = [];
  for (let img of imagesInDiv) {
    imgSrcs.push(img.currentSrc || img.src); // Use currentSrc or fallback to src
  }

  return Promise.resolve(imgSrcs);
}


async function expandPost(post) {
  const moreButton = Array.from(post.querySelectorAll('div[role="button"]'))
    .find(button => button.innerText.includes('See more'));

  if (moreButton) {
    moreButton.click();
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
}

async function sendName(){
  console.log("In");
  const firstH1 = document.querySelector('h1');

  // Check if the h1 element exists
  if (firstH1) {
      // Get the text content of the h1 element
      let h1Text = firstH1.textContent.trim();

      // Define the possible strings to be removed
      const verifiedAccountBengali = "ভেরিফায়েড অ্যাকাউন্ট";
      const verifiedAccountEnglish = "verified account";

      // Remove "ভেরিফায়েড অ্যাকাউন্ট" or "verified account" if they appear at the end
      if (h1Text.endsWith(verifiedAccountBengali)) {
          h1Text = h1Text.slice(0, -verifiedAccountBengali.length).trim();
      } else if (h1Text.endsWith(verifiedAccountEnglish)) {
          h1Text = h1Text.slice(0, -verifiedAccountEnglish.length).trim();
      }
      console.log(h1Text);
      const name=h1Text;
      chrome.runtime.sendMessage({ action: 'sendName', Name: name});
  }
}

async function searchPost() {
  let posts = [];
  const allPosts = document.querySelectorAll(message_selector_uri);

  for (let i = 0; i < allPosts.length; i++) {
    const post = allPosts[i];
    console.log(post);
    if (!post.is_visited) {
      posts.push(post);
    }
  }

  if (totalRequest < MAX_REQUESTS) {
    for (let post of posts) {
      if (!post.is_visited) {
        await expandPost(post);
        const postText = post.innerText;
        let img_links=await check_for_image(post);
        console.log(img_links);
        post.is_visited = true;
        if (postText) {
          chrome.runtime.sendMessage({ action: 'sendPost', postText: postText,imgs:img_links});
          totalRequest++;
        }
        if (totalRequest >= MAX_REQUESTS) break;
      }
    }
  }
}

window.addEventListener('scroll', searchPost);
window.addEventListener('load', searchPost);
window.addEventListener('load', sendName);

// window.addEventListener("DOMContentLoaded",()=>{
//   /// Override the visibility state to keep the tab "active"
// Object.defineProperty(document, 'visibilityState', {
//   get() {
//     return 'visible';
//   }
// });

// Object.defineProperty(document, 'hidden', {
//   get() {
//     return false;
//   }
// });

// // Trigger visibilitychange event to simulate active tab
// document.dispatchEvent(new Event('visibilitychange'));

// // Keep triggering it periodically
// setInterval(() => {
//   document.dispatchEvent(new Event('visibilitychange'));
// }, 10000); // Every 10 seconds

// });