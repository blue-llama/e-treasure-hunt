// JS HOLD

var marker = null;
var map;
var search_button;
var autocomplete;

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
  var input = document.getElementById("autocomplete");

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

function setMarkerToResult() {
  // Get the place details from the autocomplete object.
  var place = autocomplete.getPlace();

  if (place.geometry) {
    bounds = new google.maps.LatLngBounds();

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

function createOrMoveMarker(latLng) {
  if (marker == null) {
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

function moveToPlace(event) {
  if (event.latLng != null) {
    createOrMoveMarker(event.latLng);
  }
}

function showSearchAlert() {
  var searchPos;
  if (marker != null && marker.getPosition() != null) {
    searchPos = marker.getPosition();

    var url = new URL(window.location);
    var lvl = url.searchParams.get("lvl");
    var href_string =
      "/do-search?lat=" + searchPos.lat() + "&long=" + searchPos.lng();

    if (lvl != null) {
      href_string += "&lvl=" + lvl;
    }

    window.location.href = href_string;
  }
}
