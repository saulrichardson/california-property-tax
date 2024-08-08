const map = L.map('map').setView([34.05, -118.25], 11);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

fetch('/data')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            onEachFeature: function (feature, layer) {
                const apn = feature.properties.APN;
                const taxBill = feature.properties.TAX_BILL;
                const marketValue = feature.properties.MARKET_VALUE;
                const ratio = feature.properties.RATIO;

                layer.on('click', () => {
                    // Update Property Details tab
                    content =
                        `
                        <div class="property-details-content">
                            <p><b>APN:</b> ${apn}</p>
                            <p><b>TAX BILL:</b> ${taxBill}</p>
                            <p><b>MARKET VALUE:</b> ${marketValue}</p>
                            <p><b>RATIO:</b> ${ratio}</p>
                        </div>
                        `
                    window.postMessage({type: 'propertyDetails', content: content}, '*');
                });
            },
            pointToLayer: function (feature, latlng) {
                return L.circleMarker(latlng, {
                    radius: 5,
                    fillColor: colorBasedOnRatio(feature.properties.RATIO),
                    color: colorBasedOnRatio(feature.properties.RATIO),
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                });
            }
        }).addTo(map);
    })
    .catch(error => console.error('Error fetching GeoJSON data:', error));

function colorBasedOnRatio(ratio) {
    if (ratio < 0.1) return 'green';
    if (ratio < 0.3) return 'yellow';
    if (ratio < 0.5) return 'orange';
    return 'red';
}

window.addEventListener('message', function (event) {
    if (event.data.type === 'propertyDetails') {
        const content = event.data.content;
        document.getElementById('property-details-drawer').innerHTML = content;
        const myTab = new bootstrap.Tab(document.getElementById('nav-property-details-tab'));
        myTab.show();
    }
});