"use strict";

const $showRatings = $("#show-ratings");

let offsetAmount = 0;
let loaded = true;
let endOfItems = false;

async function getRatings() {

  const params = new URLSearchParams({
    'homepage': true,
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

async function handleScroll() {
  let height = $(document).height();
  let position = $(window).height() + $(window).scrollTop();

  if ((height - position) <= 100 && loaded) {
    loaded = false;
    await getRatings();
  }

  if ((height - position) > 100) loaded = true;

}

$(window).on('scroll', handleScroll);

getRatings();