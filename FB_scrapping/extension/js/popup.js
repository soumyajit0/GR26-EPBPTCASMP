var TRAITS = [
    'Agreeableness',
    'Conscientiousness',
    'Extraversion',
    'Neuroticism',
    'Openness'
];

const COLORS = ['#f8d359', '#f78a86', '#edddc2', '#71cae5', '#31dcb2'];

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