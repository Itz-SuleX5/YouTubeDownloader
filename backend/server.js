import express from 'express';
import cors from 'cors';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

// Configurar CORS para permitir solo el dominio de Netlify
const corsOptions = {
  origin: process.env.FRONTEND_URL || 'https://youtubedownloaderitzsulex5.netlify.app',
  optionsSuccessStatus: 200
};

app.use(cors(corsOptions));
app.use(express.json());

app.post('/api/download', async (req, res) => {
    try {
        const { url } = req.body;
        
        const response = await axios.post('https://all-media-api.p.rapidapi.com/v1/social/youtube/detail', {
            url: url
        }, {
            headers: {
                'x-rapidapi-key': process.env.RAPIDAPI_KEY || 'bb18653d4dmsh9763ddd8e0a6f76p1896cejsnb2c4604c6ecc',
                'x-rapidapi-host': 'all-media-api.p.rapidapi.com',
                'Content-Type': 'application/json'
            }
        });

        if (response.data && response.data.streamingData && response.data.streamingData.formats) {
            const format = response.data.streamingData.formats[0];
            res.json({ downloadUrl: format.url });
        } else {
            res.status(404).json({ error: 'No download URL found' });
        }
    } catch (error) {
        console.error('Error getting video details:', error);
        res.status(500).json({ error: 'Error getting video details' });
    }
});

// Ruta de prueba
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', message: 'Server is running' });
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
