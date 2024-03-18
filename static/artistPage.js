"use strict";

const $showAlbums = $("#show-albums");

let offsetAmount = 0;
let loaded = true;
let endOfItems = false;

/**Calls `getAlbums` when user gets to the end of the page */
async function handleScroll() {
  if (!endOfItems) {
    let height = $(document).height();
    let position = $(window).height() + $(window).scrollTop();

    if ((height - position) <= 100 && loaded) {
      loaded = false;
      await getAlbums();
    }

    if ((height - position) > 100) loaded = true;
  }
}

$(window).on('scroll', handleScroll);

/**Makes API request to server to recieve Album data and appends it to the page */
async function getAlbums() {

  const artistId = $("#artist-id").text();

  const params = new URLSearchParams({
    'offset': offsetAmount
  });

  const resp = await fetch(`/artists/${artistId}/albums?${params}`);
  const album_data = await resp.json();

  if (album_data.length === 0) endOfItems = true;

  for (let album of album_data) {
    generateAlbumHTML(album);
  }

  offsetAmount += 10;
}

/**Creates HTML for individual albums */
function generateAlbumHTML(album) {
  const $html = $(`
    <div class="card border-primary mb-5 col-9" style="background-color: rgba(38, 39, 48, 0.141); margin: auto;">
      <div class="card-body border-primary" onclick="location.href='/albums/${album.id}';" style="cursor: pointer;">
        <img src="${album.image_url}" alt="${album.name}" class="col-2" style="display: inline-block">
        <div style="display: inline-block;" class="ms-2">
          <h2 class="text-light">
            ${album.name}
          </h2>
          <p class="text-secondary">
            released: ${album.release_year}
          </p>
        </div>
      </div>
    </div>`);

  $showAlbums.append($html);
}


$(window).on('scroll', handleScroll);

getAlbums();