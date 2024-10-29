const map = L.map('map').setView([34.05, -118.25], 11);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

fetch('./tax_data.geojson')  // Update to the correct path of your GeoJSON file
    .then(data => {
        L.geoJSON(data, {
            onEachFeature: function (feature, layer) {
                const apn = feature.properties.AIN;
                const taxBill = feature.properties.TAX_BILL || 'N/A';
                const marketValue = feature.properties.MARKET_VALUE || 'N/A';
                const ratio = feature.properties.RATIO || 0;

                layer.on('click', () => {
                    // Update Property Details tab
                    const content = `
                        <div class="property-details-content">
                            <p><b>APN:</b> ${apn}</p>
                            <p><b>TAX BILL:</b> ${taxBill}</p>
                            <p><b>MARKET VALUE:</b> ${marketValue}</p>
                            <p><b>RATIO:</b> ${ratio}</p>
                        </div>
                    `;
                    window.postMessage({ type: 'propertyDetails', content: content }, '*');
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
    if (ratio === 0) return '#676767';  // Grey for invalid data
    if (ratio < 0.05) return '#00FF00';  // Bright Green
    if (ratio < 0.1) return '#66FF66';   // Light Green
    if (ratio < 0.15) return '#CCFF99';  // Pale Yellow Green
    if (ratio < 0.2) return '#FFFF00';   // Yellow
    if (ratio < 0.25) return '#FFCC00';  // Light Orange
    if (ratio < 0.3) return '#FF9900';   // Orange
    if (ratio < 0.4) return '#FF6600';   // Dark Orange
    if (ratio < 0.5) return '#FF3300';   // Red Orange
    return '#FF0000';                     // Bright Red
}

window.addEventListener('message', function (event) {
    if (event.data.type === 'propertyDetails') {
        document.getElementById('property-details-drawer').innerHTML = event.data.content;
        const myTab = new bootstrap.Tab(document.getElementById('nav-property-details-tab'));
        myTab.show();
    }
});