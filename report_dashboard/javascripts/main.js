$(document).ready(function() {

    var params = new URLSearchParams(window.location.search);

    var userId = '';
    if(params.has('user_id')) {
        userId = params.get('user_id');
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

    var dataSet = [
        ['First ad', 'Main', 'main event', 'JD', 'JD', 'Retail', 'Nice big ad'],
        ['Second ad', 'Main', 'main event', 'JD', 'JD', 'Retail', 'Nice big ad'],
        ['Third ad', 'Main', 'main event', 'JD', 'JD', 'Retail', 'Nice big ad'],
        ['Fourth ad', 'Main', 'main event', 'JD', 'JD', 'Retail', 'Nice big ad']
    ];

    $('#row3').on( 'init.dt', function ( e, settings ) {
        var api = new $.fn.dataTable.Api( settings );
        var filter = $('#eventMainTable_filter');
        var lbl = filter.find('label');
        lbl.addClass('filterIcon');
        lbl.prepend($('<i class="fa fa-filter"></i>'));
        var icon = lbl.find('i').get(0);
        if(icon) {
            $(icon.nextSibling).remove();
        }
        lbl.find('input').attr('id', 'tableFilter');

        $('#tableToolbar #filterWrapper').append(filter);
    } );

    var baseUrl = 'https://ec2-13-56-191-71.us-west-1.compute.amazonaws.com/hackathon/show_report';
    var url = baseUrl + '?report=ad_event&user_id=' + userId;

    $('#eventMainTable').DataTable( {
        "ajax": {
            "url": url,
            "dataSrc": ""
        },
        "columns": [
            { "data": "ad_title" },
            { "data": "ad_type" },
            { "data": "event_id" },
            { "data": "publisher" },
            { "data": "advertizer" },
            { "data": "brand_category" },
            { "data": "ad_description" },
            { "data": "ip_address" },
            { "data": "device_type"}
        ],
        paging: false
    });

    Highcharts.setOptions({
        colors: ['#2D61FF', '#00CCED', '#13D666', '#FFC72F', '#FF9700', '#E50000', '#FC2C7D', '#A937FD', '#41515F', '#B3C0CB', '#143CBF', '#00A3BE', '#11BF5B', '#BF215F', '#802ABF']
    });
    
    var timeSeriesData = [[1608390000, 10],[1608397200, 15],[1608400800, 6],[1608404400, 22],[1608408000, 3],[1608411600, 19],[1608415200, 13],[1608418800, 5],[1608422400, 2],[1608426000, 4],[1608429600, 8],[1608433200, 15],[1608436800, 27]]
    
    var timeSeriesUrl = baseUrl + '?report=rpt_user_hour&user_id=' + userId;
    
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
            type: 'datetime'
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
    
          series: [{
            type: 'area',
            name: 'Ads Viewed',
            data: timeSeriesData
          }]
    });
    
    //var topBrandsData = [{name:"Apple", y:55},{Name:"Google",y: 42},{name:"Portal by Facebook", y:39},{name:"Nest", y:33},{name:"Autonomous", y:32},{name:"Uplift", y:27},{name:"BevMo", y:22},{name:"Chipotle", y:19},{name:"Total Wine", y:18},{name:"Masterclass", y:18}];
    
    var topBrandsData = [["Apple",55],["Google",42],["Portal by Facebook",39],["Nest",33],["Autonomous",32],["Uplift",27],["BevMo",22],["Chipotle",19],["Total Wine",18],["Masterclass",18]]
    
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