let map, infoWindow;

let current_location = {lat: -34.397, lng: 150.644}

function get_current_location() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const pos = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                };
                current_location = pos
                map.setCenter(pos);
            },
            () => {
                handleLocationError(true, infoWindow, map.getCenter());
            }
        );
    } else {
        // Browser doesn't support Geolocation
        handleLocationError(false, infoWindow, map.getCenter());
    }
}

function initMap() {
    const directionsService = new google.maps.DirectionsService();
    const directionsRenderer = new google.maps.DirectionsRenderer();

    map = new google.maps.Map(document.getElementById("map"), {
        center: current_location,
        zoom: 15,
    });
    get_current_location()
    directionsRenderer.setMap(map);
    var markers = [];

    const onChangeHandler = function () {
        const start = document.getElementById("start").value;
        const end = document.getElementById("end").value;
        calculateAndDisplayRoute(directionsService, directionsRenderer);
        var body = {
            "start": current_location,
            "end": end,
            "user": '{{ user.id }}',
        }
        fetch('{% url "adventure-list" %}', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        }).then(function (response) {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Error: ' + response.status);
            }
        }).then(function (data) {
            console.log(data["pois"]);
            if (markers.length > 0) {
                for (var i = 0; i < markers.length; i++) {
                    markers[i].setMap(null);
                }
            }
            data["pois"].forEach((poi) => {
                var marker = new google.maps.Marker({
                    position: {lat: poi.geometry.location.lat, lng: poi.geometry.location.lng},
                    map: map,
                    title: poi.name
                });
                markers.push(marker);
            });
        })
    };

    document.getElementById("calculateRoute").addEventListener("click", onChangeHandler);

    // Autocomplete
    const center = current_location;
    // Create a bounding box with sides ~10km away from the center point
    const defaultBounds = {
        north: center.lat + 0.1,
        south: center.lat - 0.1,
        east: center.lng + 0.1,
        west: center.lng - 0.1,
    };
    const input = document.getElementById("destination");
    const options = {
        bounds: defaultBounds,
        fields: ["address_components", "geometry", "icon", "name"],
        strictBounds: false,
    };
    const autocomplete = new google.maps.places.Autocomplete(input, options);
    autocomplete.setFields(["place_id", "geometry", "name"]);
}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
    infoWindow.setPosition(pos);
    infoWindow.setContent(
        browserHasGeolocation
            ? "Error: The Geolocation service failed."
            : "Error: Your browser doesn't support geolocation."
    );
    infoWindow.open(map);
}

function calculateAndDisplayRoute(directionsService, directionsRenderer) {
    directionsService
        .route({
            origin: current_location,
            destination: {
                query: document.getElementById("destination").value,
            },
            travelMode: google.maps.TravelMode.DRIVING,
        })
        .then((response) => {
            $("#floating-container").addClass("hidden")
            directionsRenderer.setDirections(response);
        })
        .catch((e) => {
            debugger
            window.alert("Directions request failed due to " + status)
        });
}

window.initMap = initMap;

function initService() {
    const displaySuggestions = function (predictions, status) {
        if (status != google.maps.places.PlacesServiceStatus.OK || !predictions) {
            alert(status);
            return;
        }

        predictions.forEach((prediction) => {
            const li = document.createElement("li");

            li.appendChild(document.createTextNode(prediction.description));
            document.getElementById("results").appendChild(li);
        });
    };

    const service = new google.maps.places.AutocompleteService();

    service.getQueryPredictions({input: "pizza near Syd"}, displaySuggestions);
}

window.initService = initService;