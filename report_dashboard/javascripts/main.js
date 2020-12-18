$(document).ready(function() {

    var params = new URLSearchParams(window.location.search);

    var userId = '';
    if(params.has('user_id')) {
        userId = params.get('user_id');
    }

    var advertizerId = '';
    if(params.has('advertiser')) {
      advertizerId = params.get('advertiser');
    }

    var brandCategoryId = '';
    if(params.has('brand_category')) {
      brandCategoryId = params.get('brand_category');
    }

    $(document).on("click", "#mainNavTabs button", function(e) {
      $("#mainNavTabs li.activeTab").removeClass("activeTab");
      $(e.target).parent().addClass("activeTab");
    });

    $(document).on("mousedown", "#mainNavTabs button", function(e) {
        $('body').removeClass('keyboardMode');
    });
        $(document).on("keydown", "#mainNavTabs button", function(e) {
        $('body').addClass('keyboardMode');
    });

    $('#row3').on( 'init.dt', function ( e, settings ) {
        var api = new $.fn.dataTable.Api( settings );
        var filter = $('#eventMainTable_filter');
        var lbl = filter.find('label');
        lbl.addClass('filterIcon');
        var input = lbl.find('input');
        input.attr('id', 'tableFilter');
        input.attr('placeholder', 'Search');
        var ll = lbl.get(0);
        if(ll && ll.childNodes.length) {
          if(ll.childNodes[0].nodeType == 3) {
            ll.removeChild(ll.childNodes[0]);
          }
        }
        
        $('#tableToolbar #filterWrapper').append(filter);

        if(advertizerId) {
          setTimeout(function() {
            api.search(advertizerId).draw();
          });
        }
    } );

    var baseUrl = 'https://ec2-13-56-191-71.us-west-1.compute.amazonaws.com/hackathon/show_report';
    var url = baseUrl + '?report=ad_event&user_id=' + encodeURIComponent(userId);

    function processWrongTimeStamp(tm) {

      var split = tm.split(' ');
      var dP = split[0];
      var tP = split[1];
      var year = parseInt(dP.substring(0, 4));
      var month = parseInt(dP.substring(4,6));
      var day = parseInt(dP.substring(6));
      
      var hour = parseInt(tP.substring(0,2));
      var mins = parseInt(tP.substring(4,5));
      var secs = parseInt(tP.substring(7));

      var dm = new Date();
      dm.setFullYear(year); dm.setMonth(month - 1); dm.setDate(day); dm.setHours(hour); dm.setMinutes(mins); dm.setSeconds(secs);

      return dm.getTime();
    }

    function padItem(i) {
      return i < 10 ? '0' + i : i;
    }
    function formatColumnDate(tm) {
      var d = new Date(tm);

      return d.getFullYear() + '/' + padItem(d.getMonth() + 1) + '/' + padItem(d.getDay()) + ' ' + padItem(d.getHours()) + ':' + padItem(d.getMinutes()) + ':' + padItem(d.getSeconds());
    }

    $.getJSON(url, {}, function(data)  {
      var updatedData = [];
      for(var i = 0; i < data.length; i++) {
        var dt = data[i];
        var ts = processWrongTimeStamp(dt.time_stamp);
        dt.time_stamp = ts;
        updatedData.push( dt );
      }
      $('#eventMainTable').DataTable( {
        "data": updatedData,
        "columns": [
            { "data": "ad_title" },
            { "data": "ad_type" },
            { "data": "event_id" },
            { "data": "publisher" },
            { "data": "advertizer" },
            { "data": "brand_category" },
            { "data": "ad_description" },
            { "data": "ip_address" },
            { "data": "device_type"},
            { "data": "time_stamp"}
        ],
        "order": [[9, "desc"]],
        "columnDefs": [
          {
            "render": function (data, type, row) {
              return formatColumnDate(data);
            },
            "targets": 9
          }
        ],
        paging: false
    });
    });
    

    var userInfoUrl = baseUrl + '?report=rpt_user&user_id=' + encodeURIComponent(userId);

    $.getJSON(userInfoUrl, {}, function (data) {
      if(data && data.length) {
        var single = data[0];
        $('#totalAdsValue').text(single.impressions);
        var val = parseFloat(single.average_advertizer_impressions);
        $('#avgAdsValue').text(Math.round(val * 100) / 100);
      }
    });

    Highcharts.setOptions({
        colors: ['#2D61FF', '#00CCED', '#13D666', '#FFC72F', '#FF9700', '#E50000', '#FC2C7D', '#A937FD', '#41515F', '#B3C0CB', '#143CBF', '#00A3BE', '#11BF5B', '#BF215F', '#802ABF']
    });
    
    // time series chart
    var timeSeriesUrl = baseUrl + '?report=rpt_user_hour&user_id=' + encodeURIComponent(userId);
    $.getJSON(timeSeriesUrl, {}, function(dtaa) {

      var timeSeriesData = [];
      
      for(var i = 0; i < dtaa.length; i++) {
        var single = dtaa[i];
        var hrStr = single.hour_string;
        var imps = parseInt(single.impressions, 10);

        var split = hrStr.split(' ');
        var dt = split[0];
        var dtParts = dt.split('/');
        var tm = split[1];
        var tmParts = tm.split(':');

        var dtObj = new Date();
        dtObj.setDate(parseInt(dtParts[1]));
        dtObj.setMonth(parseInt(dtParts[0]) - 1);
        dtObj.setFullYear(parseInt('20' + dtParts[2]));
        dtObj.setHours(parseInt(tmParts[0]));
        dtObj.setMinutes(parseInt(tmParts[1]));

        
        timeSeriesData.push([ parseInt(dtObj.getTime() / 1000), imps]);
        
      };
      
      var daysLable = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
      var monthsLabel = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      function fomratDate(dt) {
        var day = dt.getDay();
        var month = dt.getMonth();
        var hrs = dt.getHours();
        hrs = hrs < 10 ? '0' + hrs : hrs;
        var mins = dt.getMinutes();
        mins = mins < 10 ? '0' + mins : mins;
        var secs = dt.getSeconds();
        secs = secs < 10 ? '0' + secs : secs;
        return daysLable[day] + ', ' + monthsLabel[month] + ' ' + dt.getDate() + ', ' + hrs +':' + mins + ':' + secs;
      }
      
      Highcharts.chart('timeSeriesContainer', {
        chart: {
          zoomType: 'x'
        },
        credits: {
          enabled: false
        },
        title: {
          text: ''
        },
        xAxis: {
          type: 'datetime',
          labels: {
            formatter: function(dt) {
              var dd = dt.value * 1000;
              var dat = new Date(dd);
              var hours = dat.getHours();
              hours = hours < 10 ? '0' + hours : hours;
              var mins = dat.getMinutes();
              mins = mins < 10 ? '0' + mins : mins;
              var secs = dat.getSeconds();
              secs = secs < 10 ? '0' + secs : secs;
              return hours +':' + mins +':' + secs;
            }
          }
        },
        yAxis: {
          title: {
            text: ''
          }
        },
        legend: {
          enabled: false
        },
        plotOptions: {
          area: {
            fillColor: {
              linearGradient: {
                x1: 0,
                y1: 0,
                x2: 0,
                y2: 1
              },
              stops: [
                [0, Highcharts.getOptions().colors[0]],
                [1, Highcharts.color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
              ]
            },
            marker: {
              radius: 2
            },
            lineWidth: 1,
            states: {
              hover: {
                lineWidth: 1
              }
            },
            threshold: null
          }
        },
        tooltip: {
          formatter: function() {
             var dt = new Date(this.x * 1000);
              return '<div class="tooltip-top">'+ fomratDate(dt) +'</div><br />'+
                  '<div class="tooltip-high">Ads Viewed: '+ this.y + '</div>';
          }
        },
        series: [{
          type: 'area',
          name: 'Ads Viewed',
          data: timeSeriesData
        }]
  });

    });
      

    var topBrandsUrl = baseUrl + '?report=rpt_user_advertizer&user_id=' + encodeURIComponent(userId);
    
    $.getJSON(topBrandsUrl, {}, function (data) {

      var topBrandsData = [];
      for(var i = 0; i < data.length; i++) {
        topBrandsData.push([data[i].advertizer, data[i].impressions]);
      }
      // Build the chart
    Highcharts.chart('topBrandsContainer', {
      credits: {
        enabled: false
      },
      legend: {
        align: 'right',
        verticalAlign: 'top',
        layout: 'vertical',
        x: 0,
        y: 24
      },
      chart: {
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        type: 'pie'
      },
      title: {
        text: ''
      },
      tooltip: {
        pointFormat: '<b>{point.percentage:.1f}%</b>'
      },
      accessibility: {
        point: {
          valueSuffix: '%'
        }
      },
      plotOptions: {
        pie: {
          allowPointSelect: true,
          cursor: 'pointer',
          dataLabels: {
            enabled: false
          },
          showInLegend: true
        }
      },
      series: [{
        name: 'Brands',
        colorByPoint: true,
        data: topBrandsData
      }]
    });
    });

    
    
    
  });