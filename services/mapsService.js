const puppeteer = require('puppeteer');
const chromium = require('@sparticuz/chromium');
const puppeteerCore = require('puppeteer-core');
const { extractItems, scrollPage } = require('./pageUtils');
const { Logger } = require('../utils/logger');

const getMapsData = async (searchFor, lat, lng, zoom, lang, total) => {
    let browser = null;

    try {
        const executablePath = process.env.BROWSER_EXECUTABLE_PATH;

        if (process.env.NODE_ENV === 'development') {
            Logger.log('Development browser: ');
            browser = await puppeteer.launch({
                args: ['--no-sandbox', '--disable-setuid-sandbox'],
                headless: false,
                executablePath: executablePath || undefined, // Use the path if provided
            });
        } else if (process.env.NODE_ENV === 'production') {
            Logger.log('Production browser: ');
            browser = await puppeteerCore.launch({
                args: chromium.args,
                defaultViewport: chromium.defaultViewport,
                executablePath: executablePath || await chromium.executablePath(), // Use the path if provided
                headless: chromium.headless,
            });
        }

        if (!browser) {
            throw new Error('Failed to launch browser');
        }

        const page = await browser.newPage();
        await page.setExtraHTTPHeaders({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4882.194 Safari/537.36",
        });

        const cookies = [
            { 
                name: 'SOCS',
                value: 'CAESNQgEEitib3FfaWRlbnRpdHlmcm9udGVuZHVpc2VydmVyXzIwMjUwMzEyLjA4X3AwGgJlcyACGgYIgMDIvgY',
                domain: '.google.com',
                path: '/',
                httpOnly: true,
                secure: true,
                sameSite: 'None'
            },
        ];
        await page.setCookie(...cookies);

        const url = `https://www.google.com/maps/search/${searchFor}/@${lat},${lng},${zoom}z?&hl=${lang}`;
        await page.goto(url, {
            waitUntil: 'domcontentloaded',
            timeout: 60000
        });

        await page.waitForTimeout(5000);

        let data = await scrollPage(page, ".m6QErb[aria-label]", total);

        await browser.close();
        return data;
    } catch (error) {
        if (browser) {
            await browser.close();
        }
        Logger.error('Error launching browser:', error);
        throw error;
    }
};

module.exports = { getMapsData };