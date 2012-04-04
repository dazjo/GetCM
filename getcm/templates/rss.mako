<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>CyanogenMod Downloads</title>
<link>http://get.cm</link>
<ttl>60</ttl>
<description>CyanogenMod Downloads</description>
% for file in files:
% if file.info_hash:
<item>
    <title>${file.filename}</title>
    <link>http://bacon.cyanogenmod.com/cm/torrents/${file.filename}.torrent</link>
    <guid isPermaLink="true">http://bacon.cyanogenmod.com/cm/torrents/${file.filename}.torrent</guid>
    <pubDate>${file.date_created}</pubDate>
    <enclosure url="http://bacon.cyanogenmod.com/cm/torrents/${file.filename}.torrent" type="application/x-bittorrent"/>
</item>
% endif
% endfor
</channel>
</rss>
