from manga_py.crypt import KissMangaComCrypt
from manga_py.fs import basename
from manga_py.provider import Provider
from .helpers.std import Std

from sys import stderr
from time import sleep


class KissMangaCom(Provider, Std):
    __local_data = {
        'iv': b'a5e8e2e9c2721be0a84ad660c472c1f3',
        'key': b'mshsdf832nsdbash20asdm',
    }

    def get_archive_name(self) -> str:
        idx = self.get_chapter_index()
        return 'Ch-{:0>3}_Vol-{:0>3}-{:0>1}'.format(*idx.split('-'))

    def get_chapter_index(self) -> str:
        bn = basename(self.chapter)
        name = self.re.search(r'Vol-+(\d+)-+Ch\w*?-+(\d+)-+(\d+)', bn)
        if name:
            name = name.groups()
            return '{1}-{0}-{2}'.format(*name)
        name = self.re.search(r'Vol-+(\d+)-+Ch\w*?-+(\d+)', bn)
        if name:
            name = name.groups()
            return '{1}-{0}-0'.format(*name)
        name = self.re.search(r'Ch\w*?-(\d+)(?:-v(\d+))?', bn)
        if name:
            name = name.groups()
            return '{}-{}-0'.format(*name, '0')
        name = self.re.search(r'/Manga/[^/]+/(\d+)', self.chapter)
        return '{}-000-0'.format(name.group(1))

    def get_main_content(self):
        return self._get_content('{}/Manga/{}')

    def get_manga_name(self) -> str:
        return self._get_name('/Manga/([^/]+)')

    def get_chapters(self):
        chapters = self._elements('.listing td a')
        if not len(chapters):
            print('Chapters not found', file=stderr)
        return chapters

    def prepare_cookies(self):
        self.cf_protect(self.get_url())
        self._storage['cookies']['rco_quality'] = 'hq'
        if not self._params['cf-protect']:
            print('CloudFlare protect fail!', file=stderr)

    def __decrypt_images(self, crypt, key, hexes):
        images = []
        for i in hexes:
            try:
                img = crypt.decrypt(self.__local_data['iv'], key, i)
                img = img.decode('utf-8').replace('\x10', '').replace('\x0f', '')
                images.append(img)
            except Exception as e:
                print('ERROR! %s \n' % str(e), file=stderr)

        return images

    def __check_key(self, crypt, content):
        # if need change key
        need = self.re.search(r'\["([^"]+)"\].\+chko.?=.?chko', content)
        key = self.__local_data['key']
        if need:
            # need last group
            key += crypt.decode_escape(need.group(1))
        else:
            # if need change key
            need = self.re.findall(r'\["([^"]+)"\].*?chko.*?=.*?chko', content)
            if need:
                key = crypt.decode_escape(need[-1])
        return key

    def get_files(self):
        crypt = KissMangaComCrypt()

        sleep(.5)

        print('chapter %s' % self.chapter)

        content = self.http_get(self.chapter)
        key = self.__check_key(crypt, content)

        hexes = self.re.findall(r'lstImages.push\(wrapKA\(["\']([^"\']+?)["\']\)', content)

        if not hexes:
            print('Images not found!', file=stderr)
            return []

        self._storage['referer'] = self.http().referer = ''

        print('\n\nImages: SUCCESS')

        _images = self.__decrypt_images(crypt, key, hexes)

        print('\n\nDecrypted images: SUCCESS')
        print('\n\n')

        return _images

    def get_cover(self):
        return self._cover_from_content('.rightBox .barContent img')

    def book_meta(self) -> dict:
        # todo meta
        pass


main = KissMangaCom
