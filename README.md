# 💡 ssexi.js

https://github.com/user-attachments/assets/0fd717ab-010a-4d29-a036-735042c9fb1d

**Server-Sent Events + Forms for Hypermedia Apps**

`ssexi.js` is a lightweight JavaScript library inspired by `fixi.js` for declarative **live updates** and **form submissions** via **Server-Sent Events (SSE)**.
It’s intentionally simple, limited in scope, and designed for small web apps with minimal JavaScript.
No frameworks. No build tools. Just drop it in and go.

---

## 🚀 Getting Started

### Include the script

```html
<script src="ssexi.js"></script>
```

---

## 🧬 Mark Your HTML

Apply declarative attributes **directly on `<body>`**:

```html
<body sx-connect="/events/news">
  <div id="news-feed"></div>
</body>
```

---

## ✉️ Forms via `[sx-post]`

```html
<form sx-post="/api/submit" sx-swap="none">
  <input name="email" />
  <button type="submit">Submit</button>
</form>
```

* Form data is POSTed to the given endpoint.
* Handled via `FormData` with fetch.

---

## 📡 Server Sends Updates Like

Send newline-delimited JSON SSE messages like this:

```
data: {"html": {"news-feed": "<div id='news-feed'><p>Latest News!</p></div>"}}
data: {"js": {"exec": "console.log('News updated!')"}}
data { "js": { "counterValue": 5 } }
```

Each `data:` line should contain **one JSON object**. Supported keys:

* `"html"`: DOM updates keyed by `id`
* `"js.exec"`: JavaScript to eval
* `"js.someVar"`: Sets `window.someVar`(window scope and hydrate web components)

## ✅ Features

* Auto-connects to SSE endpoints with `[sx-connect]`
* Auto-submits forms with `[sx-post]`
* Updates parts of the DOM based on simple JSON from the server
* Handles JavaScript execution and variable injection
* Reconnects SSE automatically if disconnected
* Observes new DOM nodes and initializes them automatically

---

## 🔁 Reconnection Logic

If the connection drops, `ssexi.js` will attempt to reconnect after 5 seconds, as long as the element is still present in the DOM.

---

## 🔧 Manual API

```js
ssexi.process(element);     // Manually process new elements
ssexi.connections;          // Map of open EventSource connections
ssexi.version;              // "1.0.0"
```

---

## 📦 Compatibility

* Works in all modern browsers that support EventSource
* No external dependencies
