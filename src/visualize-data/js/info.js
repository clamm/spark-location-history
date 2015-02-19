GET_URI_INFO = 'http://localhost:1338/data/output/info.json';


function setInfo(data) {
    $('#aggregationInputSize').text(data.aggregationInputSize);
    $('#aggregationOutputSize').text(data.aggregationOutputSize);
    $('#processingTime').text(data.processingTimeInSeconds);
    $('#startDate').text(data.startDate);
    $('#endDate').text(data.endDate);
}


$(document).ready(function () {
    $.getJSON(GET_URI_INFO, function (data) {
        setInfo(data)
    });
});