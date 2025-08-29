import re
import PTN
import unicodedata

from typing import List, Optional
from dataclasses import dataclass, field

@dataclass
class Movie:
    title: str
    normalized_title: str
    year: Optional[int]
    resolution: Optional[str]
    quality: Optional[str]
    codec: Optional[str]
    extra: List[str] = field(default_factory=list)
    split: bool = False
    part: Optional[int] = None

class MovieParser:
    def __parse_file_name(self, file_name: str):
        file_name = re.sub(r'@[\w_]+', '', file_name.lower()).strip()
        file_name = file_name.replace('_', ' ')
        self.file_name = file_name
        self.extension = self.file_name.split('.')[-1]
        self.movie = PTN.parse(self.file_name)
        self.tags = []

    def fallback_title(self, file_name):
        name = re.sub(r'\.\w{2,4}$', '', file_name)
        name = name.replace('_', ' ').replace('.', ' ')
        name = re.sub(r'@\w+', '', name)
        name = unicodedata.normalize('NFKC', name)
        tags_pattern = r'\b(480p|720p|1080p|2160p|BR_Rip|WEBRip|HDRip|x264|x265|HEVC|AAC|DD\+?5\.1|[0-9]+MB|1GB|2GB|Tamil|Telugu|Hindi|English|Dubbed|HDTV|WEB-DL|BluRay|Blu-ray|YTS|YIFY|fps)\b'
        name = re.sub(tags_pattern, '', name, flags=re.IGNORECASE)
        name = re.split(r'\b(S\d+|Ep\d+)\b', name, 1)[0]
        name = re.sub(r'\s+', ' ', name).strip()
        return name

    def fallback_year(self, file_name):
        years = re.findall(r'(?<!\d)(19\d{2}|20\d{2})(?!\d)', file_name)
        return int(years[0]) if years else None

    def _fix_roman_numerals(self, text: str) -> str:
        roman_pattern = r'\b(i{1,3}|iv|v|vi{0,3}|ix|x{1,3}|xl|l|li{0,3}|lx|xc|c|ci{0,3}|cd|d|dc|cm|m|m{1,3})\b'
        return re.sub(roman_pattern, lambda m: m.group(0).upper(), text, flags=re.IGNORECASE)

    def extract(self, file_name: str) -> Movie:
        
        self.__parse_file_name(file_name)
        title = self.movie.get('title', '').replace('.', ' ').strip()
        if not title:title = self.fallback_title(self.file_name)
        else:title = title.replace('.', ' ').strip()

        year = self.movie.get('year') or self.fallback_year(self.file_name)
        if year and str(year) in title:title = title.replace(str(year), '').strip()

        resolution = self.movie.get('resolution')
        quality = self.movie.get('quality')
        codec = self.movie.get('codec')
        if codec:codec = codec.replace('H', 'x').replace('.', '')

        extra = []
        tag_keywords = {
            'psa': 'PSA', 'pahe': 'Pahe', 'galaxyrg': 'GalaxyRG',
            'imax': 'IMAX', '60fps': '60FPS'
        }
        for k, v in tag_keywords.items():
            if k in self.file_name:
                extra.append(v)

        if any(k in self.file_name for k in ['dolby', 'atmos']):
            extra.append('DolbyAtmos')

        match = re.search(r'\.(\d{3})$', file_name)
        split = match is not None
        part = int(match.group(1)) if split else None

        return Movie(
            title=self._fix_roman_numerals(title.title()),
            normalized_title=re.sub(r'[^a-z0-9&\+]+', ' ', title.lower()).strip(),
            year=year,
            resolution=resolution,
            quality=quality,
            codec=codec,
            extra=extra,
            split=split,
            part=part
        )

parser = MovieParser()

