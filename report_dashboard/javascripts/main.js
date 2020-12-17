$(document).ready(function() {
    $(document).on("click", "#mainNavTabs button", function(e) {
      console.log(1);
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
        ['First ad', 'Main', 'main event', 'JD', 'JD', 'Retail', 'Nice big ad']
    ];

    $('#eventMainTable').DataTable( {data: dataSet, paging: false});
  });