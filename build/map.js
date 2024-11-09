const map = L.map('map').setView([34.05, -118.25], 11);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

fetch('./property_data.geojson')
    .then(response => response.json())
    .then(data => {
        console.log('GeoJSON data fetched:', data);
        const ratioValues = data.features.map(f => f.properties["Effective Tax Rate"]).filter(r => r != null);

        // Set up color scale with min/max of ratio values
        const colorScale = d3.scaleLinear()
            .domain([Math.min(...ratioValues), Math.max(...ratioValues)])
            .range(['#008d00', '#d8d800', '#ab0000']);

        // Use the colorScale to determine circle color based on ratio
        L.geoJSON(data, {
            onEachFeature: function (feature, layer) {
                const properties = feature.properties;
                const ain = properties["AIN"] || 'N/A';
                const taxBill = properties["Property Tax Bill"] || 'N/A';
                const assessedValue = properties["Assessed Value"] || 'N/A';

                // Additional properties
                const address = properties["Address"] || 'N/A';
                const taxClass = properties["Tax Class"] || 'N/A';
                const effectiveTaxRate = properties["Effective Tax Rate"] + '%' || 'N/A';
                const taxRateComparison = properties["Tax Rate Comparison"] || 'N/A';

                layer.on('click', () => {
                    // Update Property Details tab
                    const content = `
                                <div class="property-details-content">
                                    <p><b>APN:</b> ${ain}</p>
                                    <p><b>ADDRESS:</b> ${address}</p>
                                    <p><b>TAX CLASS:</b> ${taxClass}</p>
                                    <p><b>ASSESSED VALUE:</b> ${assessedValue}</p>
                                    <p><b>TAX BILL:</b> ${taxBill}</p>
                                    <p><b>EFFECTIVE TAX RATE:</b> ${effectiveTaxRate}</p>
                                    <p><b>TAX RATE COMPARISON:</b> ${taxRateComparison}</p>
                                </div>
                            `;
                    window.postMessage({ type: 'propertyDetails', content: content }, '*');
                });
            },
            pointToLayer: function (feature, latlng) {
                const ratio = parseFloat(feature.properties["Effective Tax Rate"]) || 0;
                return L.circleMarker(latlng, {
                    radius: 5,
                    fillColor: colorScale(ratio),
                    color: colorScale(ratio),
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                });
            }
        }).addTo(map);
    })
    .catch(error => console.error('Error fetching GeoJSON data:', error));

// Listener for property details display
window.addEventListener('message', function (event) {
    if (event.data.type === 'propertyDetails') {
        document.getElementById('property-details-drawer').innerHTML = event.data.content;
        const myTab = new bootstrap.Tab(document.getElementById('nav-property-details-tab'));
        myTab.show();
    }
});