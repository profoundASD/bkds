const express = require('express');
const cors = require('cors');
const expressLayouts = require('express-ejs-layouts');
const app = express();
const homeRoute = require('./routes/bkds_router');
const path = require('path');
const axios = require('axios');

app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');
app.use(express.static('public'));
app.use(expressLayouts);

// Use the home route module for the root path
app.use('/', homeRoute);

// CORS Middleware
app.use(cors());


const API_ENDPOINT = 'https://en.wikipedia.org/w/api.php'; 

app.use((req, res, next) => {
  // Set CORS headers to allow requests from any origin
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');
  next();
});

app.get('/api', async (req, res) => {
  const queryParams = req.url.slice(4);  // Get query parameters
  const url = API_ENDPOINT + queryParams;
  try {
    const response = await axios.get(url);
    res.send(response.data);
  } catch (error) {
    console.error('Error fetching API:  ', error);
    res.status(500).send('Error fetching API');
  }
});

app.get('/proxy', async (req, res) => {
  const url = decodeURIComponent(req.query.url);
  try {
    const response = await axios.get(url);
    res.send(response.data);
  } catch (error) {
    console.error('Error fetching URL:', error);
    res.status(500).send('Error fetching URL');
  }
});


const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
