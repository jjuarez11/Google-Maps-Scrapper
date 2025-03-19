const express = require('express');
const puppeteer = require('puppeteer'); // Añadir esta línea
const { getMapsData } = require('./services/mapsService');
const { Logger } = require('./utils/logger');

const app = express();

app.get('/get_places', async (req, res) => {
    const searchFor = req.query.Busqueda || 'restaurants';
    const lat = req.query.Latitud || '26.8484046';
    const lng = req.query.Longitud || '75.7215344';
    const zoom = req.query.Zoom || '12';
    const lang = req.query.idioma || 'en';
    const total = parseInt(req.query.total) || 20;

    try {
        const data = await getMapsData(searchFor, lat, lng, zoom, lang, total);
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.get('/', async (req, res) => {
    const puppeteerVersion = require('puppeteer/package.json').version;
    const puppeteerExecutablePath = puppeteer.executablePath();
    res.send(`Puppeteer version: ${puppeteerVersion}<br>Executable path: ${puppeteerExecutablePath}`);
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
    Logger.log(`Server is running on port ${PORT}`);
});