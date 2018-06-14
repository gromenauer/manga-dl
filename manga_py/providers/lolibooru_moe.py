from .danbooru_donmai_us import DanbooruDonmaiUs
from .helpers.std import Std


class LoliBooruMoe(DanbooruDonmaiUs, Std):
    _archive_prefix = 'lolibooru_'

    def get_manga_name(self) -> str:
        if ~self.get_url().find('?tags='):
            self._is_tag = True
            self._manga_name = self._get_name(r'\?tags=([^&]+)')
        else:
            self._manga_name = self._get_name(r'/post/show/(\d+)')
        return self._archive_prefix + self._manga_name

    def get_chapters(self):  # pragma: no cover
        if self._is_tag:
            pages = self._elements('#paginator .pagination > a')
            images_on_page = len(self._elements('ul#post-list-posts > li'))
            print('Pages!')
            if pages:
                count = self.re.search(r'\bpage=(\d+)', pages[-2].get('href')).group(1)
                max_page = int(int(count) / images_on_page) + 1
                print(max_page)
                if max_page > 1001:
                    self.log('1000 pages maximum!')
                    max_page = 1000
                return range(1, max_page)[::-1]
        return [1]

    def _tag_images(self):  # pragma: no cover
        url = '{}/post?tags={}&page={}'.format(
            self.domain,
            self._manga_name,
            self.chapter,
        )
        parser = self.html_fromstring(url)
        return self._images_helper(parser, '#post-list-posts a.directlink', 'href')

    def _post_image(self, url):  # pragma: no cover
        if isinstance(url, str):
            parser = self.html_fromstring(url)
        else:
            parser = url

        full_size = parser.cssselect('.status-notice a.highres-show')
        if full_size:
            return [full_size[0].get('href')]
        return [parser.cssselect('#image')[0].get('src')]


main = LoliBooruMoe
