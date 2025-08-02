# SSEXI.js

**SSE + Fixi: Declarative Server-Sent Events for Hypermedia-Driven Web Applications**

SSEXI.js is a lightweight JavaScript library that brings superior reactivity to web applications through Server-Sent Events (SSE), inspired by the simplicity of Fixi.js but designed for real-time, event-driven architectures. It embraces the hypermedia philosophy by keeping JavaScript minimal and hidden, using declarative HTML attributes to create reactive web applications that are easy to understand and maintain.

## Philosophy

SSEXI.js is built on the principle that web applications should be simple, declarative, and follow the hypermedia approach. Instead of complex JavaScript frameworks, it uses inline HTML attributes to define behavior, making web applications more readable and maintainable.

### Core Principles

1. **Single Persistent Connection**: Keep one GET connection open using `sx-connect` on the body element
2. **Form-Based Interactions**: Use standard HTML forms with `sx-post` for user interactions
3. **Declarative Attributes**: Define behavior through HTML attributes, not JavaScript
4. **Real-time Reactivity**: Superior to traditional AJAX through persistent SSE connections
5. **Hypermedia Compliance**: HTML-first approach with minimal JavaScript interference

## Why SSEXI.js?

Traditional web applications rely on AJAX requests that create multiple short-lived connections. SSEXI.js maintains a single persistent SSE connection, providing:

- **Lower Latency**: No connection overhead for updates
- **Real-time Updates**: Server can push updates instantly
- **Better UX**: Immediate feedback and live data updates
- **Simplified Architecture**: One connection pattern to understand
- **Resource Efficiency**: Fewer server connections and network overhead

## Key Differences from Fixi.js

While inspired by Fixi.js, SSEXI.js takes a fundamentally different approach:

| Aspect | Fixi.js | SSEXI.js |
|--------|---------|----------|
| **Connection Type** | AJAX requests | Server-Sent Events |
| **Response Format** | HTML responses | SSE JSON messages |
| **Connection Pattern** | Request-response cycles | Persistent connection |
| **Update Mechanism** | Pull-based | Push-based |
| **Real-time Capability** | Limited | Native |

## Three Core Features

SSEXI.js supports three essential capabilities for modern web applications:

### 1. HTML Updates by Target ID

Update specific DOM elements by targeting their ID:

```json
{
  "html": {
    "user-list": "<div id='user-list'><p>Updated content</p></div>",
    "status-bar": "<div id='status-bar' class='success'>Operation complete</div>"
  }
}
```

### 2. JavaScript Variable Updates

Set global JavaScript variables for application state:

```json
{
  "js": {
    "userCount": 42,
    "isLoggedIn": true,
    "currentUser": {"name": "John", "id": 123}
  }
}
```

### 3. JavaScript Code Execution

Execute arbitrary JavaScript code for complex operations:

```json
{
  "js": {
    "exec": "console.log('User connected'); updateDashboard();"
  }
}
```

## Getting Started

### Basic Setup

1. Include SSEXI.js in your HTML:

```html
<!DOCTYPE html>
<html>
<head>
    <title>My SSEXI App</title>
</head>
<body sx-connect="/sse">
    <script src="ssexi.js"></script>
</body>
</html>
```

2. Set up your SSE endpoint to return JSON messages:

```javascript
// Server endpoint should return messages like:
{
  "html": {"status": "<div id='status'>Connected</div>"},
  "js": {"userCount": 5}
}
```

### Complete Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Real-time Chat</title>
</head>
<body sx-connect="/chat-stream">
    <div id="messages">
        <!-- Messages will be updated here -->
    </div>
    
    <div id="user-count">
        <!-- User count will be updated here -->
    </div>
    
    <form sx-post="/send-message">
        <input type="text" name="message" placeholder="Type your message..." required>
        <input type="hidden" name="user_id" value="123">
        <button type="submit">Send</button>
    </form>
    
    <script src="ssexi.js"></script>
</body>
</html>
```

## Attributes Reference

### `sx-connect`

Establishes an SSE connection to the specified endpoint. Typically placed on the `<body>` element.

```html
<body sx-connect="/live-updates">
```

**Features:**
- Automatic reconnection on connection loss
- JSON message parsing
- Event dispatching for lifecycle events

### `sx-post`

Defines a POST endpoint for form submissions.

```html
<form sx-post="/api/submit">
    <input type="text" name="data">
    <button type="submit">Submit</button>
</form>
```

**Features:**
- Prevents default form submission
- Automatic FormData serialization
- Form reset after successful submission (configurable)

### `sx-swap`

Controls form behavior after submission:

```html
<form sx-post="/api/data" sx-swap="none">
    <!-- Form resets after successful submission -->
</form>
```

**Values:**
- `none` (default): Reset form after successful submission

### `sx-ignore`

Prevents SSEXI.js from processing an element and its children:

```html
<div sx-ignore>
    <!-- This section won't be processed by SSEXI -->
    <form sx-post="/test">This form won't work</form>
</div>
```

## SSE Message Format

SSEXI.js expects SSE messages to contain JSON data with the following structure:

### HTML Updates

```json
{
  "html": {
    "element-id": "<div id='element-id' class='updated'>New content</div>",
    "another-id": "<span id='another-id'>More content</span>"
  }
}
```

**Rules:**
- Keys are element IDs to target
- Values are complete HTML strings
- Target elements must exist in the DOM
- ID attributes are preserved during updates

### JavaScript Updates

```json
{
  "js": {
    "variableName": "value",
    "objectVar": {"key": "value"},
    "exec": "alert('Hello World!');"
  }
}
```

**Types:**
- **Variables**: Set `window[key] = value`
- **exec**: Execute JavaScript code using `eval()`

### Combined Updates

```json
{
  "html": {
    "status": "<div id='status' class='success'>Message sent!</div>"
  },
  "js": {
    "messageCount": 42,
    "exec": "scrollToBottom();"
  }
}
```

## Event System

SSEXI.js dispatches custom events throughout the lifecycle:

### SSE Connection Events

```javascript
// Listen for connection events
document.addEventListener('sx:connected', (e) => {
    console.log('Connected to:', e.detail.endpoint);
});

document.addEventListener('sx:error', (e) => {
    console.log('Connection error:', e.detail.error);
});

document.addEventListener('sx:message', (e) => {
    console.log('Received update:', e.detail.update);
});
```

### Form Events

```javascript
// Listen for form events
document.addEventListener('sx:form-success', (e) => {
    console.log('Form submitted successfully');
});

document.addEventListener('sx:form-error', (e) => {
    console.log('Form submission failed:', e.detail.error);
});
```

### Update Events

```javascript
// Listen for specific update types
document.addEventListener('sx:html-updated', (e) => {
    console.log('HTML updated for:', e.detail.elementId);
});

document.addEventListener('sx:js-var', (e) => {
    console.log('Variable set:', e.detail.key, '=', e.detail.value);
});

document.addEventListener('sx:js-exec', (e) => {
    console.log('JavaScript executed:', e.detail.code);
});
```

## Advanced Usage

### Manual Processing

Force SSEXI.js to process new elements:

```javascript
// Process a specific element
const newElement = document.createElement('div');
newElement.setAttribute('sx-post', '/api/endpoint');
document.dispatchEvent(new CustomEvent('sx:process', {
    detail: { target: newElement }
}));

// Or use the API
SSEXI.process(newElement);
```

### Connection Management

Access active connections:

```javascript
// View all active connections
console.log(SSEXI.connections);

// Close a specific connection
const endpoint = '/my-sse-endpoint';
if (SSEXI.connections.has(endpoint)) {
    SSEXI.connections.get(endpoint).close();
}
```

### Dynamic Form Creation

```javascript
// Create forms dynamically
const form = document.createElement('form');
form.setAttribute('sx-post', '/api/dynamic');
form.innerHTML = `
    <input type="text" name="dynamic_field" value="test">
    <button type="submit">Submit</button>
`;
document.body.appendChild(form);

// Process the new form
SSEXI.process(form);
```

## Server-Side Implementation

### SSE Endpoint Requirements

Your SSE endpoint should:

1. Set appropriate headers:
```http
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

2. Send JSON data:
```
data: {"html": {"status": "<div id='status'>Update</div>"}}

data: {"js": {"count": 10}}

```

### Example Server Implementation (Python/FastAPI)

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json
import asyncio

app = FastAPI()

@app.get("/sse")
async def sse_endpoint():
    async def event_publisher():
        while True:
            # Send HTML update
            data = {
                "html": {
                    "status": f"<div id='status'>Time: {time.time()}</div>"
                },
                "js": {
                    "lastUpdate": time.time()
                }
            }
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(1)
    
    return StreamingResponse(
        event_publisher(), 
        media_type="text/event-stream"
    )
```

## Best Practices

### Performance Optimization

1. **Minimize Message Size**: Send only changed data
2. **Batch Updates**: Combine multiple changes in one message
3. **Use Targeted Updates**: Update specific elements, not entire pages
4. **Debounce Rapid Changes**: Avoid overwhelming the client

### Security Considerations

1. **Validate JSON**: Always validate server-sent JSON
2. **Sanitize HTML**: Ensure HTML content is safe
3. **Limit exec Usage**: Use JavaScript execution sparingly
4. **Authentication**: Secure your SSE endpoints

### Error Handling

```javascript
// Handle connection errors gracefully
document.addEventListener('sx:error', (e) => {
    // Show user-friendly error message
    document.getElementById('status').innerHTML = 
        '<div class="error">Connection lost. Reconnecting...</div>';
});

// Handle form errors
document.addEventListener('sx:form-error', (e) => {
    alert('Failed to submit form: ' + e.detail.error);
});
```

## Troubleshooting

### Common Issues

**SSE Connection Not Establishing**
- Check endpoint URL and server CORS settings
- Verify server sends proper SSE headers
- Check browser dev tools Network tab

**HTML Updates Not Working**
- Ensure target element IDs exist
- Check JSON format in SSE messages
- Verify HTML structure is valid

**Form Submissions Failing**
- Check network requests in dev tools
- Verify server endpoint accepts POST requests
- Ensure form data is properly serialized

### Debug Mode

Enable verbose logging:

```javascript
// Log all SSEXI events
['connected', 'error', 'message', 'html-updated', 'js-var', 'js-exec'].forEach(eventType => {
    document.addEventListener('sx:' + eventType, (e) => {
        console.log('SSEXI Event:', eventType, e.detail);
    });
});
```

## Browser Support

SSEXI.js works in all modern browsers that support:
- Server-Sent Events (EventSource API)
- ES6 features (const, let, arrow functions)
- MutationObserver
- CustomEvent

**Supported Browsers:**
- Chrome 37+
- Firefox 38+
- Safari 10+
- Edge 79+

## Contributing

SSEXI.js is designed to be simple and focused. When contributing:

1. Maintain the declarative, attribute-based approach
2. Keep the library lightweight
3. Follow the hypermedia philosophy
4. Ensure backward compatibility
5. Add comprehensive tests for new features

## License

[Add your license information here]

## Version History

- **1.0.0**: Initial release with core SSE functionality, HTML updates, JavaScript variable setting, and code execution capabilities.