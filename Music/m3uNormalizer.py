import m3u8
import ffmpy3
import asyncio
from os import chdir
from os.path import splitext, abspath, dirname
from urllib.parse import urlparse
from glob import glob


async def main():
    playlists = glob("*.m3u")
    basePath = None
    coros = []

    for file in playlists:
        playlistObj = m3u8.load(file)
        if not playlistObj:
            continue

        for key in playlistObj.keys:
            if key and key.uri:
                basePath = '/'.join(key.uri.split('/')[:-1])

        if basePath:
            break

    for file in playlists:
        playlistObj = m3u8.load(file)
        if not playlistObj:
            continue

        playlistObj.base_path = basePath
        with open(file, "w") as f:
            f.write(playlistObj.dumps())

        ff = ffmpy3.FFmpeg(
            global_options="-protocol_whitelist file,http,https,tcp,tls,crypto",
            inputs={file: "-f hls"},
            outputs={splitext(file)[0] + ".mp3": None}
        )

        coros.append(ff.run_async())

    await asyncio.gather(*coros)


if __name__ == "__main__":
    chdir(dirname(abspath(__file__)))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
