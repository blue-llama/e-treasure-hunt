const map = L.map("map", {
  center: [20, 8],
  zoom: 3,
});

let latlng = null;
const search_button = document.getElementById("searchbutton");
search_button.disabled = true;
search_button.classList.add("disabled");

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution:
    "&copy; <a href='https://osm.org/copyright'>OpenStreetMap</a> contributors",
}).addTo(map);

const searchControl = new L.esri.Geocoding.geosearch({
  placeholder: "Begin typing for suggestions",
  useMapBounds: "false",
}).addTo(map);

map.zoomControl.setPosition("topright");

const results = new L.LayerGroup().addTo(map);
L.control.scale().addTo(map);

searchControl.on("results", function (data) {
  results.clearLayers();
  latlng = data.results[0].latlng;
  results.addLayer(L.marker(latlng, { draggable: "true" }));

  search_button.disabled = false;
  search_button.classList.remove("disabled");
});

map.on("click", function (e) {
  results.clearLayers();
  latlng = e.latlng;
  results.addLayer(L.marker(latlng, { draggable: "true" }));
  search_button.disabled = false;
  search_button.classList.remove("disabled");
});

function searchHere() {
  if (latlng !== null) {
    const url = new URL(window.location);
    const lvl = url.searchParams.get("lvl");
    let href = "/do-search?lat=" + latlng.lat + "&long=" + latlng.lng;

    if (lvl !== null) {
      href += "&lvl=" + lvl;
    }

    window.location.href = href;
  }
}
