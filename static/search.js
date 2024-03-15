"use strict";

const $resultContainer = $("#search-results")

async function getSearchResults(evt) {
  evt.preventDefault();

  const searchInput = $("#search-form input").val();
  const searchType = $("#search-form input[name='search-type']:checked").val();

  const params = new URLSearchParams({
    'query': searchInput,
    'type': searchType
  });

  const resp = await fetch(`/search/results?${params}`);
  const searchResults = await resp.json();

  console.log(searchInput);
  console.log(searchType);

  addResultsToPage(searchResults, searchType);

}


function addResultsToPage(results, searchType) {
  $resultContainer.empty();

  if (searchType === "album") {
    for (let album of results) {
      const $albumResult = generateAlbumSearchHTML(album);
      $resultContainer.append($albumResult);
    }
  } else if (searchType === "artist") {
    for (let artist of results) {
      const $artistResult = generateArtistSearchHTML(artist);
      $resultContainer.append($artistResult);
    }
  } else {
    for (let user of results) {
      const $userResult = generateUserSearchHTML(user);
      $resultContainer.append($userResult);
    }
  }

}


function generateUserSearchHTML(user) {
  const $html = $(
    `<div>
      <img src='${user.image_url}' style='height: 100px; width: 100px; border-radius: 50%;'>
      <h3>
        <a href='/users/${user.username}' class='text-light'>${user.first_name} ${user.last_name || ""}</a>
      </h3>
      <p>${user.username}</p>
    </div>`
  );

  return $html;
}


function generateArtistSearchHTML(artist) {
  const $html = $(
    `<div>
      <img src='${artist.image_url}' style='height: 100px; width: 100px; border-radius: 50%;'>
      <h3>
        <a href='/artists/${artist.id}' class='text-light'>${artist.name}</a>
      </h3>
    </div>`
  );

  return $html;
}


function generateAlbumSearchHTML(album) {
  const $html = $(
    `<div>
      <img src='${album.image_url}' style='height: 100px; width: 100px;'>
      <h3>
        <a href='/albums/${album.id}' class='text-light'>${album.name}</a>
      </h3>
      <p class='text-secondary'>
        By: <a href='/artists/${album.artist_id}'><i class='text-secondary'>${album.artist}</i></a>
      </p>
    </div>`
  );

  return $html;
}

$("#search-form").on("submit", getSearchResults);