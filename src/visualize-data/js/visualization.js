var GET_URI_DATA = 'http://localhost:1338/data/output/spark_out_data.json';
var GET_URI_MIN_MAX = 'http://localhost:1338/data/output/spark_out_extrema.json';
var POLL_FREQ = 1000 * 60 * 60;  // 1h in milliseconds

// function to create the map and the heatmap overlay
function createMap(locData) {
    var mapCenter = new google.maps.LatLng(locData.data[0].lat, locData.data[0].lng);
    var mapOptions = {
        zoom: 12,
        center: mapCenter
    };
    // standard map
    var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    window.heatmapLayer = new HeatmapOverlay(map,
        {
            // radius should be small ONLY if scaleRadius is true (or small radius is intended)
            'radius': 10,
            'maxOpacity': 1,
            // scales the radius based on map zoom
            'scaleRadius': false,
            // if set to false the heatmap uses the global maximum for colorization
            // if activated: uses the data maximum within the current map boundaries
            //   (there will always be a red spot with useLocalExtremas true)
            'useLocalExtrema': false,
            // which field name in your data represents the latitude - default 'lat'
            'latField': 'lat',
            // which field name in your data represents the longitude - default 'lng'
            'lngField': 'lng',
            // which field name in your data represents the data value - default 'value'
            'valueField': 'count',
            // update legend
            'onExtremaChange': function onExtremaChange(data) {
                updateLegend(data);
            }
        }
    );
    window.heatmapLayer.setData({
        min: locData.min,
        max: locData.max,
        data: locData.data
    });
}


function updateLegend(data) {
    // the onExtremaChange callback gives us min, max, and the gradientConfig
    // so we can update the legend
    document.getElementById('min').innerHTML = data.min;
    document.getElementById('max').innerHTML = data.max;
    // regenerate gradient image
    if (data.gradient != window.gradientCfg) {
        window.gradientCfg = data.gradient;
        var gradient = window.legendCtx.createLinearGradient(0, 0, 100, 1);
        for (var key in window.gradientCfg) {
            gradient.addColorStop(key, window.gradientCfg[key]);
        }

        window.legendCtx.fillStyle = gradient;
        window.legendCtx.fillRect(0, 0, 100, 10);
        document.getElementById('gradient').src = window.legendCanvas.toDataURL();
    }
}


function doPoll() {
    getExtrema();

    $.getJSON(GET_URI_DATA, function (data) {
        window.heatmapLayer.setData({
            data: data,
            min: window.extrema.minCount,
            max: window.extrema.maxCount
        });
        setTimeout(doPoll, POLL_FREQ);
    });
}


function getExtrema() {
    $.getJSON(GET_URI_MIN_MAX, function (data) {
        window.extrema = {
            minCount: data.minCount,
            maxCount: data.maxCount
        }
    });
}



// MAIN FUNCTION

$(function () {
    getExtrema();
    $.getJSON(GET_URI_DATA, function (data) {
        createMap({
            data: data,
            min: window.extrema.minCount,
            max: window.extrema.maxCount
        });
    });

    // we want to display the gradient, so we have to draw it
    window.legendCanvas = document.createElement('canvas');
    window.legendCanvas.width = 100;
    window.legendCanvas.height = 10;

    window.legendCtx = window.legendCanvas.getContext('2d');
    window.gradientCfg = {};

    doPoll();
})
;

