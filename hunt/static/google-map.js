window.gm_authFailure = function () {
  if (
    confirm(
      "Google Maps doesn't seem to be working right now. Do you want to try the alternative map instead?"
    )
  ) {
    let href = "/alt-map";
    const url = new URL(window.location);
    const lvl = url.searchParams.get("lvl");

    if (lvl !== null) {
      href += "?lvl=" + lvl;
    }

    window.location.href = href;
  }
};

let marker = null;
let map;
let search_button;
let autocomplete;

function createOrMoveMarker(latLng) {
  if (marker === null) {
    marker = new google.maps.Marker({
      map: map,
      position: latLng,
    });
  } else {
    marker.setPosition(latLng);
  }

  search_button.disabled = false;
  search_button.classList.remove("disabled");
}

function setMarkerToResult() {
  // Get the place details from the autocomplete object.
  const place = autocomplete.getPlace();

  if (place.geometry) {
    const bounds = new google.maps.LatLngBounds();

    createOrMoveMarker(place.geometry.location);

    if (place.geometry.viewport) {
      // Only geocodes have viewport.
      bounds.union(place.geometry.viewport);
    } else {
      bounds.extend(place.geometry.location);
    }
    map.fitBounds(bounds);
  }
}

function moveToPlace(event) {
  if (event.latLng !== null) {
    createOrMoveMarker(event.latLng);
  }
}

function initAutocomplete() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 20, lng: 8 },
    zoom: 2,
    streetViewControl: false,
    rotateControl: false,
    zoomControl: true,
    zoomControlOptions: {
      position: google.maps.ControlPosition.RIGHT_CENTER,
    },
    fullscreenControl: true,
    fullscreenControlOptions: {
      position: google.maps.ControlPosition.RIGHT_BOTTOM,
    },
    mapTypeControl: false,
  });

  // Create the search box and link it to the UI element.
  const input = document.getElementById("autocomplete");

  // Create the autocomplete object, restricting the search predictions to
  // geographical location types.
  autocomplete = new google.maps.places.Autocomplete(input);
  autocomplete.setFields(["geometry"]);
  autocomplete.addListener("place_changed", setMarkerToResult);

  map.controls[google.maps.ControlPosition.TOP_CENTER].push(input);

  search_button = document.getElementById("search-button");
  search_button.classList.add("disabled");
  search_button.disabled = true;
  map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(search_button);

  map.addListener("click", moveToPlace);
}

function searchHere() {
  if (marker !== null && marker.getPosition() !== null) {
    const searchPos = marker.getPosition();

    const url = new URL(window.location);
    const lvl = url.searchParams.get("lvl");
    let href = "/do-search?lat=" + searchPos.lat() + "&long=" + searchPos.lng();

    if (lvl !== null) {
      href += "&lvl=" + lvl;
    }

    window.location.href = href;
  }
}
