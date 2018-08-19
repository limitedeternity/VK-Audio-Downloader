const fs = require("fs");
const path = require("path");
const chalk = require("chalk");
const puppeteer = require("puppeteer");
const request = require("request");
const progress = require("request-progress");

const download = ({ link, fname }) => {
    return new Promise((resolve, reject) => {
        let destination = path.join(process.cwd(), 'Music', fname);

        progress(request(link))
            .on('error', err => reject(err))
            .on('end', () => resolve(true))
            .pipe(fs.createWriteStream(destination));

        console.log(chalk.green('::: ->') + ` ${destination}\n`);
    });
}

(async () => {
    let browser = await puppeteer.launch({
        userDataDir: path.join(process.cwd(), 'tmp'),
        headless: false
    });

    let page = await browser.newPage();

    await page.emulateMedia('screen');
    await page.setViewport({ width: 1280, height: 720 });
    await page.setRequestInterception(true);

    var interceptorCallback = req => req.continue();
    page.on('request', interceptorCallback);

    await page.goto("https://vk.com/", {
        waitUntil: 'domcontentloaded'
    });

    await page.waitForSelector('._audio_page_layout.audio_page_layout', { timeout: 0 });

    await page.evaluate(async () => {
        await new Promise(resolve => {
            var offset = -100;
            let pageScroll = () => {
                window.scrollBy(0, 50);
                if (window.pageYOffset === offset) {
                    return resolve(true);
                }

                offset = window.pageYOffset;
                setTimeout(pageScroll, 50);
            };

            pageScroll();
        });
    });

    let nameList = await page.evaluate(() => {
        function createIterator(array) {
            var nextIndex = 0;

            return {
                next() {
                    return nextIndex < array.length ? array[nextIndex++] : false
                }
            };
        }

        let audioList = Array.from(
            document.querySelector('div.audio_page__audio_rows_list._audio_page__audio_rows_list._audio_pl.audio_w_covers.audio_owner_list_canedit')
            .childNodes
        )
        .filter(el => ! Array.from(el.classList).includes("audio_claimed"));

        window.__audioIterator = createIterator(audioList);

        let nameList = [];

        for (let audio of audioList) {
            let textArr = audio.innerText.split("\n").filter(Boolean);
            let name = textArr[0] + ' - ' + textArr[1]

            nameList.push(
                name
                .replace(/\//g, "")
                .replace(/\\/g, "")
                .replace(/\|/g, "")
                .replace(/\?/g, "")
                .replace(/\*/g, "")
                .replace(/:/g, "")
                .replace(/</g, "")
                .replace(/>/g, "")
                .replace(/"/g, "")
                .replace(/'/g, "")
                .replace(/\.$/, "")
                .replace(/ $/, "")
                + ".mp3"
            );
        }

        return nameList;
    });

    page.off('request', interceptorCallback);

    var position = 0;
    var interceptorCallback = async req => {
        req.continue();

        if (new URL(req.url()).host.includes("vkuseraudio.net") && new URL(req.url()).pathname.includes(".mp3")) {
            await download({ link: req.url(), fname: nameList[position++] });
            await page.evaluate(() => {
                let element = window.__audioIterator.next();

                if (element) {
                    let evt = new Event("click");
                    element.dispatchEvent(evt);
                }
            });
        }
    }

    page.on('request', interceptorCallback);

    await page.evaluate(() => {
        let element = window.__audioIterator.next();

        if (element) {
            let evt = new Event("click");
            element.dispatchEvent(evt);
        }
    });
})();
