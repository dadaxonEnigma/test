const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();

const PORT = 3000;
const DATA_DIR = path.join(__dirname, 'data');

// Serve static files
app.use(express.static(__dirname));

// API endpoint to get test content
app.get('/api/test/:filename', (req, res) => {
    try {
        const filename = decodeURIComponent(req.params.filename);
        const filepath = path.join(DATA_DIR, filename);

        // Prevent directory traversal
        if (!filepath.startsWith(DATA_DIR)) {
            return res.status(403).json({ error: 'Access denied' });
        }

        if (!fs.existsSync(filepath)) {
            return res.status(404).json({ error: 'File not found' });
        }

        const content = fs.readFileSync(filepath, 'utf-8');
        res.send(content);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Server error' });
    }
});

// API endpoint to list test files
app.get('/data', (req, res) => {
    try {
        const files = fs.readdirSync(DATA_DIR).filter(file =>
            file.endsWith('.txt') || file.endsWith('.docx')
        );
        res.json({ files });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Server error' });
    }
});

// Serve index.html for root
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Сервер ishlanmoqda: http://localhost:${PORT}`);
    console.log('Браузерда очиш: http://localhost:3000');
});
