const express = require('express');
const app = express();
const cors = require('cors');
app.use(cors({ origin: '*' }))
const server = require("http").createServer(app);
const io = require('socket.io')(server, { cors: { origin: "http://localhost:5173", methods: ["GET", "POST"] } })

app.use(express.urlencoded({ extended: true }));
const sqlite3 = require('sqlite3').verbose();

// Open the database
const db = new sqlite3.Database('./sensor_data.db', (err) => {
    if (err) {
        console.error('Error opening database', err.message);
    } else {
        console.log('Connected to the SQLite database.');
    }
});



app.get('/data', async function (req, res) {
    const stations = ["hw6gen1", "hw5gen1", "hw7gen1" ,"hw1gen2", "hw2gen2"];
    const rows = [];

    // Create an array of promises for each database query
    const promises = stations.map(async (station) => {
        const sql = `SELECT "distance", "received_at", (SELECT ROUND(AVG("distance")) FROM "${station}") AS average FROM "${station}" ORDER BY "received_at" DESC LIMIT 1`;
        return new Promise((resolve, reject) => {
            db.get(sql, (err, row) => {
                if (err) {
                    return reject(err); // Reject the promise on error
                }
                console.log(row); // Log the row
                resolve(row); // Resolve the promise with the row
            });
        });
    });

    try {
        // Wait for all promises to resolve
        const results = await Promise.all(promises);
        rows.push(...results); // Combine results into rows
        console.log(rows); // Log the final rows
        res.send(rows); // Send the response with the rows
    } catch (error) {
        console.error(error);
        res.status(500).send('Error retrieving data'); // Handle errors
    }
});

app.post('/mqtt/configure', (req, res) => {
    const { mqttLink, apiKey, username, gpsData } = req.body;

    if (!mqttLink || !apiKey || !username || !gpsData) {
        return res.status(401).send('Missing required fields');
    }

    const sql = `INSERT INTO mqtt_config (mqtt_link, username, api_key, gps_data) VALUES (?, ?, ?, ?)`;

    db.run(sql, [mqttLink, apiKey, username, gpsData], function (err) {
        if (err) {
            console.error('Error inserting data into database:', err.message);
            return res.status(501).send('Error saving configuration');
        }
        res.status(202).send('Configuration saved successfully');
    });
});


const PORT = 3000;
server.listen(PORT, () => {
    console.log(`Server läuft auf http://localhost:${PORT}`);
})
