// Define icons for trees and holes
const treeIcon = L.icon({
    iconUrl: treeIconUrl, // URL provided by the template
    iconSize: [20, 20],
});

const holeIcon = L.icon({
    iconUrl: holeIconUrl, // URL provided by the template
    iconSize: [10, 10],
});

const defaultIcon = L.icon({
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    iconSize: [25, 41],
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    shadowSize: [41, 41]
});

// Define the boundary GeoJSON data
var RSRGA_Boundary = {
    "type": "FeatureCollection",
    "name": "RSRGA_Boundary",
    "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
    "features": [
        {
            "type": "Feature",
            "properties": { "Id": 0 },
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [36.970773408279804, -0.399641588541591],
                            [36.970501948799999, -0.398831597317524],
                            [36.970955062873763, -0.398842442225552],
                            [36.971274907411896, -0.398853254256024],
                            [36.971482813315227, -0.398831839185875],
                            [36.971871980391612, -0.398751436359811],
                            [36.972005252713657, -0.398740736032539],
                            [36.9722025023448, -0.398697851954547],
                            [36.972463705826044, -0.39871938264273],
                            [36.972895475109787, -0.398821454149959],
                            [36.973284579902895, -0.398998647417687],
                            [36.973726984902541, -0.399208053429561],
                            [36.973950853496724, -0.399310073831589],
                            [36.974148082500463, -0.399353055182203],
                            [36.974350648853118, -0.399369204894017],
                            [36.9746118657526, -0.399337069725395],
                            [36.974755790772726, -0.39936393816312],
                            [36.97465436585923, -0.399938138625163],
                            [36.974606380832981, -0.399970326338435],
                            [36.974505095671887, -0.399970301335078],
                            [36.973008080845496, -0.399618098152485],
                            [36.972271195749634, -0.399439316280315],
                            [36.971800408883169, -0.399322423213892],
                            [36.971721938006951, -0.399329273074014],
                            [36.971561587070973, -0.399332668109531],
                            [36.970773408279804, -0.399641588541591]
                        ]
                    ]
                ]
            }
        }
    ]
};

// Initialize the map and add base layers
let map = L.map('map').setView([-0.399298, 36.9726269], 18.5);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 25,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

var esriSatellite = L.tileLayer('http://mt0.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}', {
    attribution: '&copy; <a href="https://www.esri.com/">Esri</a>',
    maxZoom: 18
});

var baseLayers = {
    "OpenStreetMap": L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 25,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }),
    "ESRI Satellite": esriSatellite,
};
L.control.layers(baseLayers).addTo(map);

// Add boundary to the map
L.geoJSON(RSRGA_Boundary, {
    style: {
        color: '#3388ff',
        weight: 2,
        opacity: 0.3,
        fillColor: '#3388ff',
        fillOpacity: 0.1
    },
}).addTo(map);

// Create a global layer group for tree markers
let markersLayer = L.layerGroup().addTo(map);

// Function to fetch all tree data from the server
async function fetchTrees() {
    try {
        const response = await fetch('/api/trees/');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching tree data:', error);
        return [];
    }
}

// Function to add tree markers to the markersLayer
function addTreeMarkers(trees) {
    trees.forEach(tree => {
        // Determine the marker icon based on tree status
        let icon;
        if (tree.status === 'No Tree') {
            icon = holeIcon;
        } else if (['Healthy', 'Unknown', 'Needs Attention'].includes(tree.status)) {
            icon = treeIcon;
        } else {
            icon = treeIcon; // fallback icon
        }

        // Create marker and add it to the global markers layer
        const marker = L.marker([tree.latitude, tree.longitude], { icon: icon });
        marker.on('click', () => updateTreeInfo(tree));
        markersLayer.addLayer(marker);
    });
}

// Function to update the tree information panel
function updateTreeInfo(tree) {
    console.log("Tree Data:", tree);
    document.getElementById('tree-pointname').textContent = tree.pointname || 'Unknown';
    document.getElementById('tree-commonname').textContent = tree.commonname;
    document.getElementById('tree-scientificname').textContent = tree.scientificname || 'Unknown';
    document.getElementById('tree-localname').textContent = tree.localname;
    document.getElementById('tree-planter').textContent = tree.planter;
    document.getElementById('tree-affiliation').textContent = tree.affiliation || 'Unknown';
    document.getElementById('tree-dateplanted').textContent = tree.dateplanted || 'Unknown';
    document.getElementById('tree-status').textContent = tree.status;

    const viewDetailsButton = document.getElementById('view-details-button');
    if (tree.treeid) {
        viewDetailsButton.href = `/tree/${tree.treeid}/`;
        viewDetailsButton.style.display = 'inline-block';
    } else {
        viewDetailsButton.style.display = 'none';
    }
}

// Function to retrieve the CSRF token from the DOM
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Function to set default spinner values for the form
function setDefaultSpinnerValues() {
    const treeTypeSpinner = document.getElementById('treetype');
    if (treeTypeSpinner) {
        treeTypeSpinner.value = '1';
    }
    const statusSpinner = document.getElementById('status');
    if (statusSpinner) {
        statusSpinner.value = '1';
    }
    const planterSpinner = document.getElementById('planterid');
    if (planterSpinner) {
        planterSpinner.value = '1';
    }
}

// Function to handle new tree form submission
async function handleNewTreeSubmission(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    try {
        const response = await fetch('/api/trees/add/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
            },
            body: formData
        });
        if (!response.ok) {
            throw new Error('Failed to add new tree');
        }
        const newTree = await response.json();
        addTreeMarkers([newTree]);
        setDefaultSpinnerValues();
        alert('New tree added successfully!');
    } catch (error) {
        console.error('Error adding new tree:', error);
        alert('Failed to add new tree. Please try again.');
    }
}
document.getElementById('new-tree-form').addEventListener('submit', handleNewTreeSubmission);

// ------------------------------
// SEARCH FUNCTIONALITY
// ------------------------------

// Function to perform a search for trees and update the markers
async function performSearch() {
    const query = document.getElementById('tree-search').value.trim();
    if (!query) {
        alert('Please enter a search term.');
        return;
    }
    try {
        const response = await fetch(`/api/trees/search/?q=${encodeURIComponent(query)}`);
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || 'Failed to fetch search results');
        }
        const data = await response.json();
        // Clear existing markers from the map
        markersLayer.clearLayers();

        if (data.error || data.message) {
            alert(data.error || data.message);
        } else {
            addTreeMarkers(data);
        }
    } catch (error) {
        console.error('Error performing search:', error);
        alert('An error occurred while searching. Please try again later.');
    }
}

// Attach event listeners for search button and "Enter" key in the search input
document.getElementById('search-btn').addEventListener('click', performSearch);
document.getElementById('tree-search').addEventListener('keyup', function(e) {
    if (e.key === 'Enter') {
        performSearch();
    }
});

// Initialize the map with all tree data on page load
async function initializeMap() {
    const trees = await fetchTrees();
    addTreeMarkers(trees);
}
window.addEventListener('load', initializeMap);
