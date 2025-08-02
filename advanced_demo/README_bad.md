# 🌊 SSEXI.js - *Server-Sent Events + Declarative Forms*

**SSEXI** (SSE + Fixi) is an experimental, minimalist implementation of [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) driven hypermedia controls for building reactive web applications with maximum simplicity.

While inspired by [fixi.js](https://github.com/bigskysoftware/fixi), SSEXI takes a fundamentally different approach: instead of request-response cycles, SSEXI maintains a persistent SSE connection and uses simple form submissions to trigger server updates that flow back through the SSE stream.

Here is an example:

```html
<div sx-connect="/stream/user123">
    <form sx-post="/add_item" sx-swap="none">
        <input type="text" name="item" placeholder="Add item...">
        <button type="submit">Add</button>
    </form>
    <ul id="item-list">
        <!-- Updates automatically via SSE -->
    </ul>
</div>
```

When this form is submitted, SSEXI will POST to `/add_item` and then receive real-time updates via the SSE connection at `/stream/user123` to update the DOM reactively.

## Philosophy: Simplicity Through Persistence

SSEXI is built on a core philosophical principle: **one persistent connection beats many request-response cycles** for interactive web applications. This approach offers several advantages:

### Superior Reactivity
Unlike traditional AJAX patterns where each action requires a round-trip request, SSEXI maintains an open SSE connection that can push updates instantly. This enables:
- **Multi-user synchronization**: Changes from other users appear immediately
- **Server-initiated updates**: The server can push updates without client requests  
- **Real-time feedback**: Form submissions trigger immediate UI updates
- **Live data streaming**: Continuous updates for dashboards, chat, notifications

### Hypermedia Compliance
SSEXI embraces the [hypermedia philosophy](https://dl.acm.org/doi/fullHtml/10.1145/3648188.3675127) by:
- Using declarative HTML attributes instead of imperative JavaScript
- Keeping all interaction logic in markup, not script files
- Following the principle of [Locality of Behavior](https://htmx.org/essays/locality-of-behaviour)
- Maintaining server authority over UI state changes

### Architectural Simplicity
The SSEXI pattern is elegantly simple:
1. **One Connection**: A single `sx-connect` attribute establishes the SSE stream
2. **Standard Forms**: Regular HTML forms with `sx-post` handle user input
3. **Server Control**: The server manages all state and pushes updates via SSE
4. **Declarative Updates**: HTML attributes describe behavior, not JavaScript

## How SSEXI Works

### Connection Model
SSEXI establishes a **single persistent SSE connection** per page using the `sx-connect` attribute:

```html
<div sx-connect="/stream/session123">
    <!-- All SSE updates flow through this connection -->
</div>
```

This connection remains open for the entire page session, receiving updates from the server in real-time.

### Form Interaction
User interactions happen through **standard HTML forms** enhanced with `sx-post`:

```html
<form sx-post="/api/action" sx-swap="none">
    <input type="text" name="data" />
    <button type="submit">Submit</button>
</form>
```

When submitted:
1. SSEXI prevents the default form submission
2. POSTs the form data to the specified endpoint
3. The server processes the request and sends updates via the SSE stream
4. The DOM updates automatically based on received SSE messages

### Server-Sent Updates
The server sends updates in a structured JSON format over the SSE connection:

```javascript
// HTML updates target elements by ID
{
    "html": {
        "todo-list": "<ul id='todo-list'><li>Updated content</li></ul>"
    }
}

// JavaScript variable updates
{
    "js": {
        "itemCount": 42,
        "userName": "alice"
    }
}

// JavaScript execution
{
    "js": {
        "exec": "console.log('Update complete'); showNotification();"
    }
}
```

## Core Features

SSEXI supports three fundamental types of real-time updates:

### 1. HTML Updates
Target any element by ID and replace its content:

```html
<div id="status">Loading...</div>
```

Server sends:
```json
{
    "html": {
        "status": "<div id='status' class='success'>Complete!</div>"
    }
}
```

The element's content is updated while preserving its ID, enabling seamless real-time UI updates.

### 2. JavaScript Variables  
Set global JavaScript variables from the server:

```json
{
    "js": {
        "userCount": 45,
        "lastUpdate": "2025-01-15T10:30:00Z"
    }
}
```

These variables become available as `window.userCount`, `window.lastUpdate`, etc.

### 3. JavaScript Execution
Execute arbitrary JavaScript code:

```json
{
    "js": {
        "exec": "updateChart(newData); playNotificationSound();"
    }
}
```

This enables complex client-side behaviors triggered by server events.

## Key Differences from Fixi.js

| Aspect | Fixi.js | SSEXI.js |
|--------|---------|----------|
| **Communication** | Request-response AJAX | Persistent SSE connection |
| **Server Expectation** | HTML responses | JSON SSE messages |
| **Reactivity** | Action-triggered | Continuous real-time |
| **Multi-user** | Manual coordination | Automatic synchronization |  
| **Connection** | Per-request | Single persistent |
| **Complexity** | Simple but limited | Simple with superior capabilities |

### Why SSEXI is Simpler (Despite Longer Code)

While SSEXI's source code is longer than fixi.js, it is conceptually simpler because:

1. **No Request Management**: No need to handle request queuing, timing, or coordination
2. **Unified Update Model**: All updates flow through one SSE channel
3. **Stateless Forms**: Forms just POST data; the server handles all state management
4. **Automatic Synchronization**: Multi-user sync works automatically without special handling
5. **Fewer Attributes**: Only `sx-connect` and `sx-post` needed for most applications

The additional code provides powerful capabilities (real-time updates, JS execution, error handling) that would require extensive custom JavaScript in traditional approaches.

## API Reference

### HTML Attributes

<table>
<thead>
<tr>
  <th>Attribute</th>
  <th>Description</th>
  <th>Example</th>
</tr>
</thead>
<tbody>
<tr>
  <td><code>sx-connect</code></td>
  <td>Establishes SSE connection to the specified endpoint</td>
  <td><code>sx-connect="/stream/user123"</code></td>
</tr>
<tr>
  <td><code>sx-post</code></td>
  <td>POST form data to the specified endpoint on submit</td>
  <td><code>sx-post="/api/add-item"</code></td>
</tr>
<tr>
  <td><code>sx-swap</code></td>
  <td>Controls form reset behavior, defaults to <code>none</code> (auto-reset)</td>
  <td><code>sx-swap="none"</code></td>
</tr>
<tr>
  <td><code>sx-ignore</code></td>
  <td>Elements with this attribute are ignored by SSEXI processing</td>
  <td><code>sx-ignore</code></td>
</tr>
</tbody>
</table>

### Events

SSEXI fires events to provide visibility into its operation:

<table>
<thead>
<tr>
  <th>Event</th>
  <th>Description</th>
  <th>Element</th>
</tr>
</thead>
<tbody>
<tr>
  <td><code>sx:connected</code></td>
  <td>SSE connection established</td>
  <td>Element with <code>sx-connect</code></td>
</tr>
<tr>
  <td><code>sx:error</code></td>
  <td>SSE connection error (auto-reconnects after 5s)</td>
  <td>Element with <code>sx-connect</code></td>
</tr>
<tr>
  <td><code>sx:message</code></td>
  <td>SSE message received</td>
  <td>Element with <code>sx-connect</code></td>
</tr>
<tr>
  <td><code>sx:form-success</code></td>
  <td>Form submission succeeded</td>
  <td>Form with <code>sx-post</code></td>
</tr>
<tr>
  <td><code>sx:form-error</code></td>
  <td>Form submission failed</td>
  <td>Form with <code>sx-post</code></td>
</tr>
<tr>
  <td><code>sx:html-updated</code></td>
  <td>HTML content updated via SSE</td>
  <td>Element with <code>sx-connect</code></td>
</tr>
<tr>
  <td><code>sx:js-exec</code></td>
  <td>JavaScript code executed</td>
  <td>Element with <code>sx-connect</code></td>
</tr>
<tr>
  <td><code>sx:js-var</code></td>
  <td>JavaScript variable set</td>
  <td>Element with <code>sx-connect</code></td>
</tr>
</tbody>
</table>

## Complete Example

Here's a full example of a collaborative todo application:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Collaborative Todos</title>
    <script src="ssexi.js"></script>
</head>
<body>
    <!-- SSE connection for real-time updates -->
    <div sx-connect="/stream/todos">
        <h1>Collaborative Todo List</h1>
        
        <!-- Add new todo -->
        <form sx-post="/todos" sx-swap="none">
            <input type="text" name="text" placeholder="Add a todo..." required>
            <button type="submit">Add Todo</button>
        </form>
        
        <!-- Live todo list (updated via SSE) -->
        <ul id="todo-list">
            <li>Loading todos...</li>
        </ul>
        
        <!-- Live stats (updated via SSE) -->
        <div id="stats">
            <span id="todo-count">0</span> todos, 
            <span id="user-count">0</span> users online
        </div>
    </div>
    
    <script>
        // Listen for SSEXI events
        document.addEventListener('sx:connected', () => {
            console.log('Connected to todo stream');
        });
        
        document.addEventListener('sx:form-success', () => {
            console.log('Todo added successfully');
        });
        
        document.addEventListener('sx:js-var', (e) => {
            console.log(`Variable updated: ${e.detail.key} = ${e.detail.value}`);
        });
    </script>
</body>
</html>
```

## Server-Side Integration

SSEXI expects servers to:

1. **Handle SSE connections** at the `sx-connect` endpoint
2. **Process form POSTs** at `sx-post` endpoints  
3. **Send structured JSON** over SSE for updates

Example SSE message formats:

```javascript
// Update multiple elements
data: {"html": {"todo-list": "<ul>...</ul>", "stats": "<div>5 todos</div>"}}

// Set variables and execute code
data: {"js": {"todoCount": 5, "exec": "updateChart(5)"}}

// Combined update
data: {
    "html": {"notification": "<div class='success'>Todo added!</div>"},
    "js": {"exec": "setTimeout(() => hideNotification(), 3000)"}
}
```

## Auto-Reconnection

SSEXI automatically handles connection failures:
- **Auto-reconnect**: Reconnects after 5 seconds if connection drops
- **Error events**: Fires `sx:error` events for connection issues
- **Graceful degradation**: Forms still work during connection outages
- **Cleanup**: Properly closes connections on page unload

## Error Handling

SSEXI provides comprehensive error handling:

```javascript
document.addEventListener('sx:error', (e) => {
    console.log('SSE connection error:', e.detail.error);
    // Show user-friendly error message
});

document.addEventListener('sx:form-error', (e) => {
    console.log('Form submission failed:', e.detail.error);
    // Handle form submission errors
});

document.addEventListener('sx:parse-error', (e) => {
    console.log('Invalid SSE message:', e.detail.data);
    // Handle malformed server messages
});
```

## Installation

SSEXI is designed to be [vendored](https://htmx.org/essays/vendoring/) - simply copy the source into your project:

```bash
curl https://raw.githubusercontent.com/your-repo/ssexi/main/ssexi.js > ssexi-1.0.0.js
```

Or include it via script tag:

```html
<script src="ssexi.js"></script>
```

No build process, no dependencies, no package managers required.

## Use Cases

SSEXI excels for applications requiring real-time interactivity:

- **Collaborative tools**: Documents, whiteboards, planning tools
- **Live dashboards**: Analytics, monitoring, status boards  
- **Chat applications**: Messaging, comments, notifications
- **Gaming**: Turn-based games, leaderboards, live scores
- **E-commerce**: Inventory updates, bidding, flash sales
- **IoT interfaces**: Sensor data, device control, automation

## Browser Support

SSEXI uses modern web APIs:
- [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) (IE/Edge 12+, Chrome 6+, Firefox 6+, Safari 5+)
- [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API) (IE/Edge 14+, Chrome 42+, Firefox 39+, Safari 10.1+)
- [MutationObserver](https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver) (IE 11+, Chrome 18+, Firefox 14+, Safari 6+)

For older browsers, polyfills can be used.

## Global API

SSEXI exposes a minimal global API:

```javascript
// Manual processing
SSEXI.process(document.getElementById('new-content'));

// Connection management  
SSEXI.connections; // Map of active connections

// Version
SSEXI.version; // "1.0.0"
```

## Debugging

Enable verbose logging to debug SSEXI behavior:

```javascript
// Log all SSEXI events
['connected', 'error', 'message', 'form-success', 'form-error', 
 'html-updated', 'js-exec', 'js-var'].forEach(event => {
    document.addEventListener(`sx:${event}`, (e) => {
        console.log(`SSEXI ${event}:`, e.detail);
    });
});
```

## Security Considerations

- **Input validation**: Always validate form inputs on the server
- **Authentication**: Protect SSE endpoints with proper authentication  
- **Authorization**: Ensure users only receive updates they're authorized to see
- **Rate limiting**: Protect form endpoints from abuse
- **Content filtering**: Sanitize HTML content sent via SSE updates
- **JavaScript execution**: Be cautious with `js.exec` - only execute trusted code

## Performance Notes

- **Connection pooling**: SSEXI reuses connections for the same endpoint
- **Memory management**: Automatically cleans up connections on page unload  
- **Efficient updates**: Only processes changed elements, preserves existing DOM where possible
- **Minimal overhead**: Small runtime footprint, no unnecessary abstractions

## Philosophy: Less is More

SSEXI embodies the principle that **fewer moving parts lead to more reliable systems**. By maintaining a single persistent connection instead of managing multiple request-response cycles, SSEXI eliminates entire classes of complexity:

- No request queuing or synchronization logic
- No loading states or request coordination  
- No manual cache invalidation or state synchronization
- No complex error recovery for failed requests

The result is applications that are not only more responsive but also easier to reason about, debug, and maintain.

## License

```
Zero-Clause BSD
===============

Permission to use, copy, modify, and/or distribute this software for
any purpose with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE
FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY
DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
```

---

*"The best software is software that doesn't need to exist, and the second best is software so simple it obviously has no deficiencies."* - The SSEXI Philosophy