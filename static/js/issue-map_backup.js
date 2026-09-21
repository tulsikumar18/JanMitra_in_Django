document.addEventListener("DOMContentLoaded", function () {

    console.log("JanMitra: issue-map.js loaded");

    /* =========================================================
       1. CHECK LEAFLET
    ========================================================= */

    if (typeof L === "undefined") {
        console.error("JanMitra: Leaflet failed to load.");
        return;
    }

    console.log("JanMitra: Leaflet loaded successfully");


    /* =========================================================
       2. MAP ELEMENT
    ========================================================= */

    const mapElement = document.getElementById("issue-map");

    if (!mapElement) {
        console.error("JanMitra: #issue-map not found.");
        return;
    }


    /* =========================================================
       3. BENGALURU CONFIGURATION
    ========================================================= */

    const BENGALURU_CENTER = [
        12.9716,
        77.5946
    ];

    const BENGALURU_BOUNDS = L.latLngBounds(
        [12.80, 77.40],
        [13.20, 77.80]
    );

    const ISSUE_RADIUS_KM = 10;


    /* =========================================================
       4. CREATE MAP
    ========================================================= */

    const map = L.map("issue-map", {
        center: BENGALURU_CENTER,
        zoom: 12,
        minZoom: 10,
        maxZoom: 19,
        zoomControl: true,
        maxBounds: BENGALURU_BOUNDS,
        maxBoundsViscosity: 1.0
    });


    /* =========================================================
       5. MAP TILES
    ========================================================= */

    /*
       We are intentionally not using the public OSM
       standard tile endpoint here because it was returning
       a 403 policy response in your current setup.

       CARTO provides a clean basemap suitable for this
       development project.
    */

    L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        {
            maxZoom: 20,
            attribution:
                '&copy; OpenStreetMap contributors &copy; CARTO'
        }
    ).addTo(map);


    /* =========================================================
       6. DATA FROM DJANGO
    ========================================================= */

    const issues = window.janmitraIssues || [];

    console.log(
        "JanMitra: issues received:",
        issues.length
    );


    /* =========================================================
       7. ELEMENTS
    ========================================================= */

    const categoryFilter =
        document.getElementById("category-filter");

    const statusFilter =
        document.getElementById("status-filter");

    const issueCount =
        document.getElementById("issue-count");

    const searchInput =
        document.getElementById("map-search-input");

    const searchButton =
        document.getElementById("map-search-button");

    const searchResults =
        document.getElementById("map-search-results");

    const locationButton =
        document.getElementById("current-location-button");


    /* =========================================================
       8. STATE
    ========================================================= */

    const markers = [];

    let userLocation = null;

    let userLocationMarker = null;


    /* =========================================================
       9. MARKER COLOR
    ========================================================= */

    function getMarkerColor(status) {

        if (status === "resolved") {
            return "green";
        }

        if (status === "in_progress") {
            return "blue";
        }

        if (status === "under_review") {
            return "orange";
        }

        if (status === "rejected") {
            return "gray";
        }

        return "red";
    }


    /* =========================================================
       10. MARKER ICON
    ========================================================= */

    function createMarkerIcon(status) {

        const color = getMarkerColor(status);

        let iconClass = "bi-exclamation-lg";

        if (status === "resolved") {
            iconClass = "bi-check-lg";
        }

        if (status === "rejected") {
            iconClass = "bi-x-lg";
        }

        return L.divIcon({

            className: "civic-map-marker",

            html:
                '<div class="map-marker marker-' +
                color +
                '">' +
                '<i class="bi ' +
                iconClass +
                '"></i>' +
                '</div>',

            iconSize: [
                36,
                36
            ],

            iconAnchor: [
                18,
                36
            ],

            popupAnchor: [
                0,
                -34
            ]
        });
    }


    /* =========================================================
       11. USER LOCATION ICON
    ========================================================= */

    function createUserLocationIcon() {

        return L.divIcon({

            className: "user-location-icon",

            html:
                '<div class="user-location-marker"></div>',

            iconSize: [
                22,
                22
            ],

            iconAnchor: [
                11,
                11
            ]
        });
    }


    /* =========================================================
       12. POPUP
    ========================================================= */

    function createPopup(issue) {

        const color =
            getMarkerColor(issue.status);

        const upvotes =
            Number(issue.upvotes || 0);

        const supporterText =
            upvotes === 1
                ? JANMITRA_TRANSLATIONS.citizen
                : JANMITRA_TRANSLATIONS.citizens;

        return `
            <div class="issue-popup">

                <div class="popup-status popup-${color}">
                    <i class="bi bi-circle-fill"></i>
                    ${issue.statusName}
                </div>

                <h3>
                    ${issue.title}
                </h3>

                <div class="popup-category">
                    <i class="bi bi-grid"></i>
                    ${issue.categoryName}
                </div>

                <div class="popup-location">
                    <i class="bi bi-geo-alt"></i>
                    ${issue.location || "Bengaluru"}
                </div>

                <div class="popup-date">
                    <i class="bi bi-calendar3"></i>
                    ${issue.date}
                </div>

                <div class="popup-upvotes">
                    <i class="bi bi-hand-thumbs-up-fill"></i>
                    ${upvotes}
                    ${supporterText}
                    ${JANMITRA_TRANSLATIONS.supporting}
                </div>

                <a
                    href="/issues/${issue.id}/"
                    class="popup-button"
                >
                    ${JANMITRA_TRANSLATIONS.viewIssue}
                    <i class="bi bi-arrow-right"></i>
                </a>

            </div>
        `;
    }


    /* =========================================================
       13. DISTANCE CALCULATION
    ========================================================= */

    function calculateDistance(
        lat1,
        lon1,
        lat2,
        lon2
    ) {

        const earthRadius = 6371;

        const latitudeDifference =
            (lat2 - lat1) *
            Math.PI /
            180;

        const longitudeDifference =
            (lon2 - lon1) *
            Math.PI /
            180;

        const a =
            Math.sin(latitudeDifference / 2) *
            Math.sin(latitudeDifference / 2) +

            Math.cos(
                lat1 * Math.PI / 180
            ) *

            Math.cos(
                lat2 * Math.PI / 180
            ) *

            Math.sin(longitudeDifference / 2) *
            Math.sin(longitudeDifference / 2);

        const c =
            2 *
            Math.atan2(
                Math.sqrt(a),
                Math.sqrt(1 - a)
            );

        return earthRadius * c;
    }


    /* =========================================================
       14. DISPLAY ISSUES
    ========================================================= */

    function displayIssues() {

        /* Remove existing markers */

        markers.forEach(function (marker) {

            map.removeLayer(marker);

        });

        markers.length = 0;


        const selectedCategory =
            categoryFilter
                ? categoryFilter.value
                : "all";

        const selectedStatus =
            statusFilter
                ? statusFilter.value
                : "all";


        let visibleCount = 0;


        issues.forEach(function (issue) {

            /* -----------------------------------------------
               VALID COORDINATES
            ----------------------------------------------- */

            const latitude =
                Number(issue.latitude);

            const longitude =
                Number(issue.longitude);

            if (
                !Number.isFinite(latitude) ||
                !Number.isFinite(longitude)
            ) {
                return;
            }


            /* -----------------------------------------------
               CATEGORY FILTER
            ----------------------------------------------- */

            if (
                selectedCategory !== "all" &&
                issue.category !== selectedCategory
            ) {
                return;
            }


            /* -----------------------------------------------
               STATUS FILTER
            ----------------------------------------------- */

            if (
                selectedStatus !== "all" &&
                issue.status !== selectedStatus
            ) {
                return;
            }


            /* -----------------------------------------------
               USER LOCATION FILTER
            ----------------------------------------------- */

            if (userLocation) {

                const distance =
                    calculateDistance(
                        userLocation.latitude,
                        userLocation.longitude,
                        latitude,
                        longitude
                    );

                if (
                    distance > ISSUE_RADIUS_KM
                ) {
                    return;
                }
            }


            /* -----------------------------------------------
               CREATE MARKER
            ----------------------------------------------- */

            const marker =
                L.marker(
                    [
                        latitude,
                        longitude
                    ],
                    {
                        icon:
                            createMarkerIcon(
                                issue.status
                            )
                    }
                );


            marker.bindPopup(
                createPopup(issue),
                {
                    maxWidth: 320,
                    minWidth: 250
                }
            );


            marker.addTo(map);

            markers.push(marker);

            visibleCount++;

        });


        /* -----------------------------------------------
           UPDATE COUNT
        ----------------------------------------------- */

        if (issueCount) {

            issueCount.textContent =
                visibleCount;

        }

    }


    /* =========================================================
       15. CATEGORY FILTER
    ========================================================= */

    if (categoryFilter) {

        categoryFilter.addEventListener(
            "change",
            function () {

                displayIssues();

            }
        );
    }


    /* =========================================================
       16. STATUS FILTER
    ========================================================= */

    if (statusFilter) {

        statusFilter.addEventListener(
            "change",
            function () {

                displayIssues();

            }
        );
    }


    /* =========================================================
       17. SEARCH LOCATION
    ========================================================= */

    async function searchLocation() {

        const query =
            searchInput
                ? searchInput.value.trim()
                : "";

        if (!query) {
            return;
        }


        if (searchButton) {

            searchButton.disabled = true;

            searchButton.textContent =
                JANMITRA_TRANSLATIONS.searching;
        }


        if (searchResults) {

            searchResults.innerHTML = "";

        }


        try {

            const searchQuery =
                query +
                ", Bengaluru, Karnataka, India";


            const response =
                await fetch(
                    "https://nominatim.openstreetmap.org/search?" +
                    new URLSearchParams({
                        format: "json",
                        q: searchQuery,
                        limit: "5",
                        countrycodes: "in",
                        viewbox:
                            "77.40,13.20,77.80,12.80",
                        bounded: "1"
                    })
                );


            if (!response.ok) {

                throw new Error(
                    "Location search failed"
                );
            }


            const results =
                await response.json();


            const bengaluruResults =
                results.filter(function (result) {

                    const latitude =
                        parseFloat(result.lat);

                    const longitude =
                        parseFloat(result.lon);

                    return (
                        latitude >= 12.80 &&
                        latitude <= 13.20 &&
                        longitude >= 77.40 &&
                        longitude <= 77.80
                    );

                });


            if (
                bengaluruResults.length === 0
            ) {

                if (searchResults) {

                    searchResults.innerHTML =
                        `
                        <div class="map-no-results">
                            ${JANMITRA_TRANSLATIONS.noLocations}
                        </div>
                        `;

                }

                return;
            }


            bengaluruResults.forEach(
                function (result) {

                    const latitude =
                        parseFloat(result.lat);

                    const longitude =
                        parseFloat(result.lon);


                    const button =
                        document.createElement(
                            "button"
                        );


                    button.type = "button";

                    button.className =
                        "map-search-result";


                    button.innerHTML =
                        `
                        <i class="bi bi-geo-alt"></i>
                        <span>
                            ${result.display_name}
                        </span>
                        `;


                    button.addEventListener(
                        "click",
                        function () {

                            map.setView(
                                [
                                    latitude,
                                    longitude
                                ],
                                16
                            );


                            searchInput.value =
                                result.display_name;


                            searchResults.innerHTML =
                                "";

                        }
                    );


                    searchResults.appendChild(
                        button
                    );

                }
            );

        } catch (error) {

            console.error(
                "JanMitra location search error:",
                error
            );


            if (searchResults) {

                searchResults.innerHTML =
                    `
                    <div class="map-no-results">
                        ${JANMITRA_TRANSLATIONS.searchError}
                    </div>
                    `;

            }

        } finally {

            if (searchButton) {

                searchButton.disabled =
                    false;

                searchButton.textContent =
                    JANMITRA_TRANSLATIONS.search;
            }

        }

    }


    /* =========================================================
       18. SEARCH BUTTON
    ========================================================= */

    if (searchButton) {

        searchButton.addEventListener(
            "click",
            searchLocation
        );

    }


    /* =========================================================
       19. ENTER KEY
    ========================================================= */

    if (searchInput) {

        searchInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    event.preventDefault();

                    searchLocation();

                }

            }
        );

    }


    /* =========================================================
       20. CURRENT LOCATION
    ========================================================= */

    if (locationButton) {

        locationButton.addEventListener(
            "click",
            function () {

                if (
                    !navigator.geolocation
                ) {

                    alert(
                        JANMITRA_TRANSLATIONS.locationUnsupported
                    );

                    return;
                }


                locationButton.disabled =
                    true;


                locationButton.innerHTML =
                    `
                    <i class="bi bi-hourglass-split"></i>
                    ${JANMITRA_TRANSLATIONS.locating}
                    `;


                navigator.geolocation.getCurrentPosition(

                    function (position) {

                        const latitude =
                            position.coords.latitude;

                        const longitude =
                            position.coords.longitude;


                        /* -------------------------------------
                           BENGALURU CHECK
                        ------------------------------------- */

                        const isInBengaluru =
                            latitude >= 12.80 &&
                            latitude <= 13.20 &&
                            longitude >= 77.40 &&
                            longitude <= 77.80;


                        if (!isInBengaluru) {

                            alert(
                                JANMITRA_TRANSLATIONS.bengaluruOnly
                            );

                            locationButton.disabled =
                                false;

                            locationButton.innerHTML =
                                `
                                <i class="bi bi-crosshair"></i>
                                ${JANMITRA_TRANSLATIONS.myLocation}
                                `;

                            return;
                        }


                        userLocation = {
                            latitude: latitude,
                            longitude: longitude
                        };


                        /* -------------------------------------
                           REMOVE OLD LOCATION MARKER
                        ------------------------------------- */

                        if (
                            userLocationMarker
                        ) {

                            map.removeLayer(
                                userLocationMarker
                            );

                        }


                        /* -------------------------------------
                           CREATE LOCATION MARKER
                        ------------------------------------- */

                        userLocationMarker =
                            L.marker(
                                [
                                    latitude,
                                    longitude
                                ],
                                {
                                    icon:
                                        createUserLocationIcon()
                                }
                            ).addTo(map);


                        userLocationMarker.bindPopup(
                            `
                            <strong>
                                ${JANMITRA_TRANSLATIONS.yourLocation}
                            </strong>
                            `
                        );


                        /* -------------------------------------
                           CENTER MAP
                        ------------------------------------- */

                        map.setView(
                            [
                                latitude,
                                longitude
                            ],
                            14
                        );


                        /* -------------------------------------
                           SHOW NEARBY ISSUES
                        ------------------------------------- */

                        displayIssues();


                        locationButton.disabled =
                            false;

                        locationButton.innerHTML =
                            `
                            <i class="bi bi-crosshair"></i>
                            ${JANMITRA_TRANSLATIONS.myLocation}
                            `;

                    },


                    function () {

                        alert(
                            JANMITRA_TRANSLATIONS.locationPermission
                        );


                        locationButton.disabled =
                            false;

                        locationButton.innerHTML =
                            `
                            <i class="bi bi-crosshair"></i>
                            ${JANMITRA_TRANSLATIONS.myLocation}
                            `;

                    },


                    {
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 300000
                    }

                );

            }
        );

    }


    /* =========================================================
       21. INITIAL DISPLAY
    ========================================================= */

    displayIssues();


    /* =========================================================
       22. FIX LEAFLET SIZE
    ========================================================= */

    setTimeout(
        function () {

            map.invalidateSize();

        },
        300
    );


    window.addEventListener(
        "resize",
        function () {

            map.invalidateSize();

        }
    );


    console.log(
        "JanMitra: Bengaluru issue map initialized successfully."
    );

});