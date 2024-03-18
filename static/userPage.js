"use strict";

const $showRatings = $("#show-ratings");

let offsetAmount = 0;
let loaded = true;
let endOfItems = false;


/** Makes API request to server to recieve rating HTML and appends it to the page*/
async function getRatings() {

  const params = new URLSearchParams({
    'user': $("#username").text(),
    'offset': offsetAmount
  });

  const resp = await fetch(`/ratings/load?${params}`);
  const ratings = await resp.json();

  if (ratings.length == 0) endOfItems = true;

  for (let rating of ratings) {
    const $html = $(`${rating}`);
    $showRatings.append($html);
  }

  offsetAmount += 10;

}


/** Calls `getRatings` when the user gets to the end of the page */
async function handleScroll() {
  if (!endOfItems) {
    let height = $(document).height();
    let position = $(window).height() + $(window).scrollTop();

    if ((height - position) <= 100 && loaded) {
      loaded = false;
      await getRatings();
    }

    if ((height - position) > 100) loaded = true;
  }
}

$(window).on('scroll', handleScroll);

getRatings();