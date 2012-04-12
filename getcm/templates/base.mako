<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>CyanogenMod Downloads</title>
    <link rel="stylesheet" type="text/css" href="http://download.cyanogenmod.com/bootstrap/css/bootstrap.min.css"/>
    <link rel="stylesheet" type="text/css" href="http://download.cyanogenmod.com/bootstrap/css/bootstrap-responsive.min.css"/>
    <script type="text/javascript" src="http://code.jquery.com/jquery-1.7.2.min.js"></script>
    <script type="text/javascript"> 

      var _gaq = _gaq || [];
      _gaq.push(['_setAccount', 'UA-26672035-1']);
      _gaq.push(['_trackPageview']);
     
      (function() {
        var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
      })();
     
    </script> 
    <style type="text/css">
      body { padding: 10px 0 20px 0; }
      .md5 { font-size: 80%; }
      .content { padding-top: 10px; }
      .adunit { text-align: center; padding-bottom: 10px; }
    </style>
  </head>
  <body>
    <div class="container-fluid">
      <div class="row-fluid">
        <div class="span-12">
          <img src="http://download.cyanogenmod.com/static/logo.png" alt="CyanogenMod" />
        </div>
      </div>
      <div class="row-fluid content">
        <div class="span2">
          <div class="well sidebar-nav">
            <ul class="nav nav-list">
              <li class="nav-header">Type</li>
              <li id="type_all"><a href="javascript:void(0)" onclick="navigate_type('')">all</a></li>
              <li id="type_stable"><a href="javascript:void(0)" onclick="navigate_type('stable')">stable</a></li>
              <li id="type_RC"><a href="javascript:void(0)" onclick="navigate_type('RC')">release candidate</a></li>
              <li id="type_nightly"><a href="javascript:void(0)" onclick="navigate_type('nightly')">nightly</a></li>
            </ul>
          </div>
          <div class="well sidebar-nav">
            <ul class="nav nav-list">
              <li class="nav-header">Devices</li>
              <li id="device_all"><a href="javascript:void(0)" onclick="navigate_device('');">all</a></li>
              % for device in devices:
              <li id="device_${device}"><a href="javascript:void(0)" onclick="navigate_device('${device}');">${device}</a></li>
              % endfor
            </ul>
          </div>
        </div>
        <div class="span10 adunit">
<script type="text/javascript"><!--
google_ad_client = "ca-pub-4305693279235670";
/* TeamDouche Mirror */
google_ad_slot = "5118872808";
google_ad_width = 728;
google_ad_height = 90;
//-->
</script>
<script type="text/javascript"
src="http://pagead2.googlesyndication.com/pagead/show_ads.js">
</script>
        </div>
        <div class="span10">
          ${next.body()}
        </div>
      </div>
    </div>
  <script type="text/javascript">
    (function(){
        window.urlParams = {};
        var e,
                a = /\+/g,  // Regex for replacing addition symbol with a space
                r = /([^&=]+)=?([^&]*)/g,
                d = function (s) { return decodeURIComponent(s.replace(a, " ")); },
                q = window.location.search.substring(1);
        while (e = r.exec(q)) {
            window.urlParams[d(e[1])] = d(e[2]);
        }
    })();

    (function(){
        if (window.urlParams.device) {
            $("li#device_" + window.urlParams.device).addClass('active');
        } else {
            $('li#device_all').addClass('active');
        }
        if (window.urlParams.type) {
            $("li#type_" + window.urlParams.type).addClass('active');
        } else {
            $('li#type_all').addClass('active');
        }
    })(jQuery);

    window.navigate_device = function(device) {
        if (window.urlParams.type) {
            location.href = '/?' + $.param({
                device: device,
                type: window.urlParams.type
            });
        } else {
            if (device == "") {
                location.href = '/';
                return
            }
            location.href = '/?' + $.param({device: device});
        }
    }

    window.navigate_type = function(type) {
        if (window.urlParams.device) {
            location.href = '/?' + $.param({
                device: window.urlParams.device,
                type: type
            });
        } else {
            if (type == "") {
                location.href = '/';
                return
            }
            location.href = '/?' + $.param({type: type});
        }
    }
  </script>
  </body>
</html>
