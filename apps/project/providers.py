from typing import List
from urllib.parse import quote
import re

import requests


class EmbedStrategy(object):
    def __init__(self, base_url, media_host):
        self.embed_base_url = base_url
        self.media_host = media_host

    def match(self, url):
        pass

    def get_embed_iframe(self, url: str):
        print(self.embed_base_url.format(quote(url)))
        try:
            r = requests.get(self.embed_base_url.format(quote(url)))
            if r.status_code == 200:
                return r.json()['html']
            else:
                return None
        except:
            return None


class EmbedProvider(object):
    def __init__(self, strategies: List[EmbedStrategy]):
        self.embed_strategies = strategies

    def get_iframe(self, url):
        if not isinstance(url, str):
            return None

        for strategy in self.embed_strategies:
            if strategy.match(url):
                print("matched ", strategy)
                return strategy.get_embed_iframe(url), strategy.media_host
        return None


class Youtube(EmbedStrategy):
    embed_base_url = "https://www.youtube.com/oembed?url={}&format=json"
    media_host = "YOUTUBE"

    def __init__(self):
        super(Youtube, self).__init__(self.embed_base_url, self.media_host)

    def match(self, url):
        youtube_regex = re.compile("http(?:s?)://(?:www\.)?youtu(?:be\.com|\.be)")
        return youtube_regex.match(url)

    def __str__(self):
        return "YOUTUBE"


class Vimeo(EmbedStrategy):
    embed_base_url = "https://vimeo.com/api/oembed.json?url={}"
    media_host = "VIMEO"

    def __init__(self):
        super(Vimeo, self).__init__(self.embed_base_url, self.media_host)

    def match(self, url):
        vimeo_regex_list = [
            re.compile("http(?:s?)://(?:www\.)?vimeo.com/*"),
            re.compile("http(?:s?)://(?:www\.)?vimeo.com/*/*/video/*"),
            re.compile("http(?:s?)://(?:www\.)?vimeo.com/album/*/video/*"),
            re.compile("http(?:s?)://(?:www\.)?vimeo.com/channels/*/*"),
            re.compile("http(?:s?)://(?:www\.)?vimeo.com/groups/*/videos/*"),
            re.compile("http(?:s?)://(?:www\.)?vimeo.com/ondemand/*/*")
        ]
        return any(regex.match(url) for regex in vimeo_regex_list)

    def __str__(self):
        return "VIMEO"


class Soundcloud(EmbedStrategy):
    embed_base_url = "https://soundcloud.com/oembed?format=json&url={}"
    media_host = "SOUNDCLOUD"

    def __init__(self):
        super(Soundcloud, self).__init__(self.embed_base_url, self.media_host)

    def match(self, url):
        sound_cloud_regex = re.compile("http(?:s?)://(?:www\.)?soundcloud.com/*")
        return sound_cloud_regex.match(url)

    def __str__(self):
        return "SOUNDCLOUD"

# TODO: write test suit
# print(embed_provider.get_iframe("https://www.youtube.com/watch?v=HlQQ1v0Y7FI"))
