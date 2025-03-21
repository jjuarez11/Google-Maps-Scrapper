const extractItems = async (page) => {
    let maps_data = await page.evaluate(() => {
        return Array.from(document.querySelectorAll(".Nv2PK")).map((el) => {
            const link = el.querySelector("a.hfpxzc").getAttribute("href");
            return {
                title: el.querySelector(".qBF1Pd")?.textContent.trim(),
                avg_rating: el.querySelector(".MW4etd")?.textContent.trim(),
                reviews: el.querySelector(".UY7F9")?.textContent.replace("(", "").replace(")", "").trim(),
                address: el.querySelector(".W4Efsd:last-child > .W4Efsd:nth-of-type(1) > span:last-child")?.textContent.replaceAll("·", "").trim(),
                description: el.querySelector(".W4Efsd:last-child > .W4Efsd:nth-of-type(2)")?.textContent.replace("·", "").trim(),
                website: el.querySelector("a.lcr4fd")?.getAttribute("href"),
                category: el.querySelector(".W4Efsd:last-child > .W4Efsd:nth-of-type(1) > span:first-child")?.textContent.replaceAll("·", "").trim(),
                timings: el.querySelector(".W4Efsd:last-child > .W4Efsd:nth-of-type(3) > span:first-child")?.textContent.replaceAll("·", "").trim(),
                phone_num: el.querySelector(".W4Efsd:last-child > .W4Efsd:nth-of-type(3) > span:last-child")?.textContent.replaceAll("·", "").trim(),
                extra_services: el.querySelector(".qty3Ue")?.textContent.replaceAll("·", "").replaceAll("  ", " ").trim(),
                latitude: link.split("!8m2!3d")[1].split("!4d")[0],
                longitude: link.split("!4d")[1].split("!16s")[0],
                link,
                dataId: link.split("1s")[1].split("!8m")[0],
            };
        });
    });
    return maps_data;
};

const scrollPage = async (page, scrollContainer, itemTargetCount) => {
    let items = [];
    let previousHeight = await page.evaluate(`document.querySelector("${scrollContainer}").scrollHeight`);
    while (itemTargetCount > items.length) {
        items = await extractItems(page);
        await page.evaluate(`document.querySelector("${scrollContainer}").scrollTo(0, document.querySelector("${scrollContainer}").scrollHeight)`);
        await page.waitForTimeout(2000);
        let newHeight = await page.evaluate(`document.querySelector("${scrollContainer}").scrollHeight`);
        if (newHeight === previousHeight) {
            break; // Break the loop if no new items are loaded
        }
        previousHeight = newHeight;
    }
    return items;
};

module.exports = { extractItems, scrollPage };