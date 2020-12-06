from __future__ import print_function, unicode_literals, division, absolute_import
import base64
import binascii
import hashlib
import os
from Crypto.Cipher import AES
from future.builtins import int, pow
import json
import httpx
import asyncio

"""
MIT License
Copyright (c) 2018 omi mailto:4399.omi@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


class NeteaseCloudMusic(object):
    """
    from https://github.com/darknessomi/musicbox
    """

    def __init__(self):
        self.header = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip,deflate,sdch",
            "Accept-Language": "zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "music.163.com",
            "Referer": "http://music.163.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        }
        self.baseURL = "http://music.163.com"

        self.MODULUS = (
            "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7"
            "b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280"
            "104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932"
            "575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b"
            "3ece0462db0a22b8e7"
        )
        self.PUBKEY = "010001"
        self.NONCE = b"0CoJUm6Qyw8W8jud"

    async def search(
        self, keywords: str, stype: int = 1, offset: int = 0, total="true", limit=50
    ):
        """
        keywords 搜索的关键词
        stype : 搜索单曲(1)，歌手(100)，专辑(10)，歌单(1000)，用户(1002) *(type)*
        offset: 搜索结果的第几页
        total :用处不明
        limit :每一页显示多少(返回结果的数目)
        """
        path = "/weapi/search/get"
        params = dict(s=keywords, type=stype, offset=offset, total=total, limit=limit)
        return await self.request("POST", path, params)

    async def song_detail(self, song_id):
        """
        歌曲 ID
        """
        path = "/weapi/v3/song/detail"
        params = dict(c='[{"id":' + str(song_id) + "}]", ids="[" + str(song_id) + "]")
        return await self.request("POST", path, params)

    async def album(self, album_id):
        """
        专辑ID
        """
        path = "/weapi/v1/album/" + str(album_id)
        params = {}
        return await self.request("POST", path, params)

    async def song_url(self, song_id, bit_rate=0):
        """
        bit_rate:
        0   :   128000
        1   :   192000
        2   :   320000
        """
        rate_map = {0: 128000, 1: 192000, 2: 320000}
        path = "/weapi/song/enhance/player/url"
        params = dict(ids=[song_id], br=rate_map[bit_rate])
        return await self.request("POST", path, params)

    async def request(self, method, path, params={}):
        endpoint = "{}{}".format(self.baseURL, path)
        csrf_token = ""
        params.update({"csrf_token": csrf_token})

        params = self.encrypted_request(params)

        async with httpx.AsyncClient(headers=self.header) as client:
            if method == "GET":
                res = await client.get(endpoint, params=params)
            elif method == "POST":
                res = await client.post(endpoint, data=params)
        return res.json()

    def encrypted_request(self, text):
        data = json.dumps(text).encode("utf-8")
        secret = self.create_key(16)
        params = self.aes(
            self.aes(
                data,
                self.NONCE,
            ),
            secret,
        )
        encseckey = self.rsa(secret, self.PUBKEY, self.MODULUS)
        return {"params": params, "encSecKey": encseckey}

    def aes(self, text, key):
        pad = 16 - len(text) % 16
        text = text + bytearray([pad] * pad)
        encryptor = AES.new(key, 2, b"0102030405060708")
        ciphertext = encryptor.encrypt(text)
        return base64.b64encode(ciphertext)

    def rsa(self, text, pubkey, modules):
        text = text[::-1]
        rs = pow(int(binascii.hexlify(text), 16), int(pubkey, 16), int(modules, 16))
        return format(rs, "x").zfill(256)

    def encrypted_id(self, id):
        magic = bytearray("3go8&$8*3*3h0k(2)2", "u8")
        song_id = bytearray(id, "u8")
        magic_len = len(magic)
        for i, sid in enumerate(song_id):
            song_id[i] = sid ^ magic[i % magic_len]
        m = hashlib.md5(song_id)
        result = m.digest()
        result = base64.b64encode(result).replace(b"/", b"_").replace(b"+", b"-")
        return result.decode("utf-8")

    def create_key(self, size):
        return binascii.hexlify(os.urandom(size))[:16]


async def SearchSongsInNeteaseCloudMusic(keyword):
    ncm = NeteaseCloudMusic()
    song = await ncm.search(keyword, limit=1)
    song = song["result"]["songs"][0]
    song_id = song["id"]
    song_name = song["name"]
    song_author = song["artists"][0]["name"]
    song_detial = await ncm.song_detail(song_id)
    song_detial = song_detial["songs"][0]
    song_picture = song_detial["al"]["picUrl"]
    song_url = await ncm.song_url(song_id)
    song_url = song_url["data"][0]["url"] or ""
    content = f"""{{"app":"com.tencent.structmsg","desc":"音乐","view":"music","ver":"0.0.0.1","prompt":"[分享]{song_name}","meta":{{"music":{{"action":"","android_pkg_name":"","app_type":1,"appid":100495085,"desc":"{song_author}","jumpUrl":"https://music.163.com/#/song?id={song_id}","musicUrl":"{song_url}","preview":"{song_picture}","sourceMsgId":"0","source_icon":"","source_url":"","tag":"网易云音乐","title":"{song_name}"}}}}}}"""
    return content, f"https://music.163.com/#/song?id={song_id}", song_url
