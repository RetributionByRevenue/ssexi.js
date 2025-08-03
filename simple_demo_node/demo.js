const express = require('express');
const path = require('path');
const multer = require('multer');
const fs = require('fs');

const app = express();
const upload = multer();

// Store todos in memory
let todos = [];

// Middleware
app.use('/static', express.static('.', { index: false })); // Serve static files from current directory under /static
app.use(express.static('.', { index: false })); // Also serve static files from root for direct access
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Home route - serve the HTML file
app.get('/', (req, res) => {
    try {
        const html = fs.readFileSync('index.html', 'utf8');
        res.setHeader('Content-Type', 'text/html');
        res.send(html);
    } catch (error) {
        res.status(500).send('Error loading index.html');
    }
});

// SSE endpoint that handles all website logic
app.get('/website-logic', (req, res) => {
    // Set SSE headers
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('Transfer-Encoding', 'chunked');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Headers', 'Cache-Control');

    let count = 0;
    let intervalId;

    const sendEvent = (data) => {
        res.write(`data: ${JSON.stringify(data)}\n\n`);
    };

    const eventGenerator = () => {
        count++;
        const timestamp = Math.floor(Date.now() / 1000);
        
        // Update timestamp
        sendEvent({
            html: {
                timestamp: `<div id="timestamp">Current Time: ${timestamp}</div>`
            }
        });
        
        // Update counter
        sendEvent({
            html: {
                counter: `<div id="counter">Count: ${count}</div>`
            }
        });
        
        // Update todos list
        const todosHtml = todos.map(todo => `<li>${todo}</li>`).join('');
        sendEvent({
            html: {
                todos: `<ul id="todos">${todosHtml}</ul>`
            }
        });
        
        // Every 5 counts, set a JS variable and execute some code
        if (count % 5 === 0) {
            sendEvent({
                js: {
                    counterValue: count
                }
            });
            
            sendEvent({
                js: {
                    exec: `console.log('Counter reached ${count}!');`
                }
            });
        }
        
        // Every 10 counts, change background color
        if (count % 10 === 0) {
            const colors = ["lightblue", "lightgreen", "lightcoral", "wheat"];
            const color = colors[Math.floor(Math.random() * colors.length)];
            
            sendEvent({
                js: {
                    exec: `document.body.style.backgroundColor = '${color}';`
                }
            });
        }
    };

    // Start the interval
    intervalId = setInterval(eventGenerator, 1000);

    // Handle client disconnect
    req.on('close', () => {
        if (intervalId) {
            clearInterval(intervalId);
        }
    });

    req.on('aborted', () => {
        if (intervalId) {
            clearInterval(intervalId);
        }
    });

    // Send initial event to establish connection
    res.write('data: {"status": "connected"}\n\n');
});

// Todo endpoint
app.post('/todo', upload.none(), (req, res) => {
    const todoText = req.body.todo_text;
    
    if (!todoText) {
        return res.status(400).json({ 
            status: 'error', 
            message: 'todo_text is required' 
        });
    }

    console.log(`Received todo: ${todoText}`); // Print to console as requested
    todos.push(todoText);
    
    // The SSE stream will pick up the updated todos automatically
    res.json({ 
        status: 'success', 
        message: `Added todo: ${todoText}` 
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('Something broke!');
});

// Start the server
const PORT = process.env.PORT || 8001;
const HOST = process.env.HOST || '0.0.0.0';

app.listen(PORT, HOST, () => {
    console.log(`🚀 SSEXI.js Demo Server running on http://${HOST}:${PORT}`);
    console.log(`📡 SSE endpoint: http://${HOST}:${PORT}/website-logic`);
    console.log(`📝 Todo endpoint: http://${HOST}:${PORT}/todo`);
});

module.exports = app;
