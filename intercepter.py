from re import sub
import fnmatch
from os import path, getcwd, listdir
from sys import exit
from multiprocessing import Pool
from mitmproxy import http, ctx
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
        if self.linkAmount < len(self.trackList):
            if flow.request.pretty_host.endswith("vkuseraudio.net") and ".mp3?extra=" in flow.request.path:
                self.downloadQueue.append((flow.request.url, self.trackList[self.linkAmount]))
                self.linkAmount += 1
                ctx.log(f"\n[00000] Got a link: {flow.request.url}. Stats: {self.linkAmount} / {len(self.trackList)}\n")

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
            exit(0)

    def restore_state(self):
        if path.exists(path.join(getcwd(), "audios")):
            self.linkAmount = len(fnmatch.filter(listdir(path.join(getcwd(), "audios")), '*.mp3'))
            if self.linkAmount > 0:
                self.controller.restore_track_position(self.linkAmount)

    def initiate_download(self):
        pool = Pool()
        pool.map(self.downloader.download, self.downloadQueue)
        pool.close()
        pool.join()

    def finish(self):
        print("Cleaning up...\n")
        self.downloader.cleanup()
        print("My job is done here.\n")


addons = [
    Intercepter()
]
