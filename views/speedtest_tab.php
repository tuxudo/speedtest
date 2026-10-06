<div id="lister" style="font-size: large; float: right;">
    <a href="/show/listing/speedtest/speedtest" title="List">
        <i class="btn btn-default tab-btn fa fa-list"></i>
    </a>
</div>
<div id="speedtest-tab"></div>
<h2 data-i18n="speedtest.speedtest"></h2>
<div id="speedtest-msg" data-i18n="listing.loading" class="col-lg-12 text-center"></div>

<script>
$(document).on('appReady', function(){
    $.getJSON(appUrl + '/module/speedtest/get_tab_data/' + serialNumber, function(data){
        if( ! data ){
            // Change loading message to no data
            $('#speedtest-msg').text(i18n.t('no_data'));

        } else {

            // Hide loading/no data message
            $('#speedtest-msg').text('');

            $.each(data, function(i,d){
                // Generate rows from data
                var rows = '';
                var table_header_name = ''
                for (var prop in d){
                    // Do nothing for empty values to blank them
                    if ((d[prop] == '' || d[prop] == null) && d[prop] !== 0){
                        rows = rows

                    // Format bits per second
                    } else if(prop == "dl_throughput"){
                        dl_throughput = fileSize_bits(parseFloat(d[prop]), 2)+'ps'
                        rnd_dl_throughput = fileSize_bits(parseFloat(d[prop]), 0)+'⬇︎'
                        rows = rows + '<tr><th>'+i18n.t('speedtest.'+prop)+'</th><td><span title="'+ fileSize(( parseFloat(d[prop])/ 8), 2) + 'ytes/s' + '" </span>' + dl_throughput + '</td></tr>';
                        // Update the tab badge count
                        $('#speedtest-cnt').text(dl_throughput);
                        table_header_name = table_header_name + rnd_dl_throughput + " - "

                    // Format bits per second
                    } else if(prop == "ul_throughput"){
                        ul_throughput = fileSize_bits(parseFloat(d[prop]), 2)+'ps'
                        rnd_ul_throughput = fileSize_bits(parseFloat(d[prop]), 0)+'⬆︎'
                        rows = rows + '<tr><th>'+i18n.t('speedtest.'+prop)+'</th><td><span title="'+ fileSize(( parseFloat(d[prop])/ 8), 2) + 'ytes/s' + '" </span>' + fileSize_bits(parseFloat(d[prop]), 2) + 'ps</td></tr>';
                        table_header_name = table_header_name + rnd_ul_throughput + " - "

                    // Format bytes
                    } else if(prop == "dl_bytes_transferred" || prop == "ul_bytes_transferred"){
                        rows = rows + '<tr><th>'+i18n.t('speedtest.'+prop)+'</th><td>' + fileSize(parseFloat(d[prop]), 2)+'</td></tr>';

                    // Format yes
                    } else if(prop == "latest" && (d[prop] == 1 || d[prop] == "1")){
                        rows = rows + '<tr><th>'+i18n.t('speedtest.'+prop)+'</th><td>' + i18n.t('yes') + '</td></tr>';

                    // Format base_rtt
                    } else if(prop == "base_rtt"){
                        rows = rows + '<tr><th>'+i18n.t('speedtest.'+prop)+'</th><td>' + d[prop] + '</td></tr>';

                    // Format ipv4ip and external_ip_isp for table header
                    } else if(prop == "ipv4ip" || prop == "external_ip_isp"){
                        rows = rows + '<tr><th>'+i18n.t('speedtest.'+prop)+'</th><td>' + d[prop] + '</td></tr>';
                        table_header_name = table_header_name + d[prop] + " - "

                    // Format timestamps
                    } else if(prop == "end_time"){
                        var date = new Date(d[prop] * 1000);
                        var date_formatted = moment(date).format('llll')
                        rows = rows + '<tr><th>'+i18n.t('speedtest.test_time')+'</th><td><span title="'+moment(date).fromNow()+'">'+date_formatted+'</span></td></tr>';
                        table_header_name = table_header_name + date_formatted 

                    // Format lat lon coordinates to show link to Google Maps
                    } else if(prop == "lat"){
                        rows = rows + '<tr><th>'+i18n.t('speedtest.coordinates')+'</th><td><a href="https://www.google.com/maps/place/'+d[prop]+','+d['lon']+'" target="_blank">'+d[prop]+', '+d['lon']+'</a></td></tr>';

                    } else if(prop == "lon"){
                        rows = rows

                    // Else, build out rows from test results
                    } else {
                        rows = rows + '<tr><th>'+i18n.t('speedtest.'+prop)+'</th><td>'+d[prop]+'</td></tr>';
                    }
                }

                // Generate table
                $('#speedtest-tab')
                    .append($('<h4>')
                        .append($('<i>')
                            .addClass('fa fa-industry'))
                        .append(' '+table_header_name))
                    .append($('<div style="max-width:600px;">')
                        .append($('<table>')
                            .addClass('table table-striped table-condensed')
                            .append($('<tbody>')
                                .append(rows))))
            })
        }
    });
});


// Filesize formatter (uses 1000 as base)
function fileSize_bits(size, decimals){
    // Check if number
    if(!isNaN(parseFloat(size)) && isFinite(size)){
        if(size == 0){ return '0 B'}
        if(decimals == undefined){decimals = 0};
        var i = Math.floor( Math.log(size) / Math.log(1000) );
        return ( size / Math.pow(1000, i) ).toFixed(decimals) * 1 + ' ' + ['', 'K', 'M', 'G', 'T', 'P', 'E'][i] + 'b';
    }
}
</script>
