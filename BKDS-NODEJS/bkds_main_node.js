const express = require('express');
const expressLayouts = require('express-ejs-layouts');
const app = express();
const homeRoute = require('./routes/bkds_router');
const path = require('path');


// Existing static file serving
app.use(express.static(path.join(__dirname, 'public')));


app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');
//app.use(cors());
app.use(express.static('public'));
app.use(expressLayouts);
app.use('/', homeRoute);
app.use(express.json()); // Add this line

let appCache = {
  iconCache: {}
}

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
