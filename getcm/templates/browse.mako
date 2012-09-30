<%inherit file="base.mako" />

<%def name="device_link(device)">
    % if request_type is None:
        /?device=${device|h}
    % else:
        /?device=${device|h}&type=${request_type|h}
    % endif
</%def>

<%def name="filter_link(type)">
    % if request_device is None:
        /?type=${type|h}
    % else:
        /?type=${type|h}&device=${request_device|h}
    % endif
</%def>

<%def name="filter_label()">
    % if request_device and len(devicenames) and request_device in devicenames:
        for <i>${devicenames[request_device]|h}</i>
    % endif
    % if request_device and request_type:
        - ${request_device|h} / ${request_type|h}
    % elif request_device and not request_type:
        - ${request_device|h}
    % elif request_type and not request_device:
        - ${request_type|h}
    % endif
</%def>

% if len(builds) > 0:
<h3>Builds in Progress</h3>
<table class="table table-bordered table-striped">
  <thead>
    <tr>
      <th>Build Number</th>
      <th>Type</th>
      <th>Branch</th>
      <th>Device</th>
    </tr>
  </thead>
  <tbody>
    % for build in builds:
    <tr>
      <td>${build['number']}</td>
      <td>${build['type']}</td>
      <td>${build['branch']}</td>
      <td>${build['lunch']}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

<h3>Browse Files ${filter_label()}</h3>

<table class="table table-bordered table-striped">
  <thead>
    <tr>
      <th>Device</th>
      <th>Type</th>
      <th>Filename</th>
      <th>Size</th>
      <th>Date Added</th>
    </tr>
  </thead>
  <tbody>
    % for file in files:
    <% device=file.device %>
    <tr>
      <td><a href="${device_link(device)}">${file.device|h}</a><br/><small class="md5">${devicenames[file.device]|h}</small></td>
      <td>${file.type}</td>
      <td>
        <a href="https://tickleservice.appspot.com/authorizedtickle?applicationId=ROM%20Manager&data.url=http://get.cm/get/${file.full_path}&data.name=${file.filename}&failure_redirect=http://rommanager.appspot.com/webconnectfailure.html&success_redirect=http://rommanager.appspot.com/webconnectsuccess.html"><img src="http://download.cyanogenmod.com/static/rommanager.png" alt="Send to ROMManager" title="Send to ROManager"/></a>
        <a href="/torrents/${file.filename|h}.torrent"><img src="/static/bittorrent.png" alt="Download Torrent" title="Download Torrent"/></a>
        &nbsp; <b>Direct Download</b>: 
        <a href="/get/${file.full_path}">${file.filename|h}</a>
        <br/>
        <small class="md5">md5sum: ${file.md5sum|h} &nbsp;&nbsp;&nbsp;&nbsp; Short URL: <a href="http://get.cm/get/${file.base62}">http://get.cm/get/${file.base62}</a></small>
      </td>
      <td>${file.human_size|h}</small></td>
      <td>${file.date_created|h}</td>
    </tr>
    % endfor
  </tbody>
</table>
