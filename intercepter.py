from re import sub
from fnmatch import filter as fnfilter
from os import path, getcwd, listdir
from multiprocessing import Pool
from mitmproxy import http
from mitmproxy.proxy import protocol

from downloader import Downloader
from controller import Controller


class Intercepter:
    def __init__(self):
        self.downloader = Downloader()

        self.controller = Controller()
        self.controller.start()
        print("\nNavigate to audios page\n")

        self.proxyConnectionDetected = False
        self.trackList = self.controller.get_audio()
        self.linkAmount = 0
        self.downloadQueue = []

        self.restore_state()

    def clientconnect(self, layer: protocol.Layer):
        if not self.proxyConnectionDetected:
            self.controller.switch_track()
            self.proxyConnectionDetected = True

    def done(self):
        self.controller.finish()

    def request(self, flow: http.HTTPFlow):
        if flow.request.pretty_host.endswith("vkuseraudio.net") and ".mp3?extra=" in flow.request.path:
            if self.linkAmount < len(self.trackList):
                link = flow.request.url
                name = self.trackList[self.linkAmount]

                self.downloadQueue.append((link, name))
                self.linkAmount += 1

                self.log_entry(name)

                if len(self.downloadQueue) >= 15:
                    self.initiate_download()
                    self.downloadQueue = []

                self.controller.switch_track()

            if self.linkAmount == len(self.trackList):
                self.linkAmount += 1

                if len(self.downloadQueue) != 0:
                    self.initiate_download()
                    self.downloadQueue = []

                self.finish()

    def log_entry(self, name):
        print(f"\n[00000] Got audio: {name}. Stats: {self.linkAmount} / {len(self.trackList)}")

    def restore_state(self):
        if path.exists(path.join(getcwd(), "audios")):
            tmpLinkAmount = len(fnfilter(listdir(path.join(getcwd(), "audios")), '*.mp3')) - 1
            if tmpLinkAmount > 0:
                self.linkAmount = tmpLinkAmount
                for _ in range(0, self.linkAmount):
                    self.controller.switch_track()

    def initiate_download(self):
        pool = Pool()
        pool.map(self.downloader.download, self.downloadQueue)
        pool.close()
        pool.join()

    def finish(self):
        self.controller.finish()
        print("Cleaning up...\n")

        self.downloader.cleanup()
        print("My job is done here.\n")


addons = [
    Intercepter()
]
