/**
 * SSEXI.js - SSE + Fixi: Declarative Server-Sent Events for Hypermedia
 * Inspired by fixi.js but focused on SSE-driven DOM updates
 */
(() => {
    if (document.__ssexi_mo) return;
    
    // Mutation observer to watch for new elements
    document.__ssexi_mo = new MutationObserver((recs) => 
        recs.forEach((r) => 
            r.type === "childList" && 
            r.addedNodes.forEach((n) => process(n))
        )
    );
    
    // Event dispatcher
    let send = (elt, type, detail, bub) => 
        elt.dispatchEvent(new CustomEvent("sx:" + type, {
            detail, 
            cancelable: true, 
            bubbles: bub !== false, 
            composed: true
        }));
    
    // Attribute getter with default
    let attr = (elt, name, defaultVal) => elt.getAttribute(name) || defaultVal;
    
    // Check if element should be ignored
    let ignore = (elt) => elt.closest("[sx-ignore]") != null;
    
    // SSE connection management
    let connections = new Map();
    
    // Initialize form handling for element
    let initForm = (elt) => {
        if (elt.__ssexi_form || ignore(elt) || !send(elt, "form-init", {})) return;
        
        let postEndpoint = attr(elt, "sx-post");
        if (!postEndpoint) return;
        
        // Mark as initialized
        elt.__ssexi_form = true;
        
        // Add form submit handler
        elt.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (!send(elt, "form-submit", { endpoint: postEndpoint })) return;
            
            try {
                const formData = new FormData(elt);
                
                const response = await fetch(postEndpoint, {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    send(elt, "form-success", { endpoint: postEndpoint, response });
                    
                    // Reset form if sx-swap is "none" or not specified
                    const swapMode = attr(elt, "sx-swap", "none");
                    if (swapMode === "none") {
                        elt.reset();
                    }
                } else {
                    send(elt, "form-error", { endpoint: postEndpoint, error: response.statusText });
                }
                
            } catch (error) {
                send(elt, "form-error", { endpoint: postEndpoint, error });
            }
        });
        
        send(elt, "form-initialized", { endpoint: postEndpoint });
    };

    // Initialize SSE connection for element
    let initSSE = (elt) => {
        if (elt.__ssexi || ignore(elt) || !send(elt, "init", {})) return;
        
        let endpoint = attr(elt, "sx-connect");
        if (!endpoint) return;
        
        // Mark as initialized
        elt.__ssexi = true;
        
        // Close existing connection if any
        if (connections.has(endpoint)) {
            connections.get(endpoint).close();
        }
        
        // Create new EventSource
        let eventSource = new EventSource(endpoint);
        connections.set(endpoint, eventSource);
        
        // Message handler - supports your SSE message format
        eventSource.onmessage = (event) => {
            try {
                const update = JSON.parse(event.data);
                
                if (!send(elt, "message", { update, endpoint })) return;
                
                // Handle JS updates
                if (update.js) {
                    Object.entries(update.js).forEach(([key, value]) => {
                        if (key === 'exec') {
                            // Execute JavaScript code
                            eval(value);
                            send(elt, "js-exec", { code: value });
                        } else {
                            // Set window variables
                            window[key] = value;
                            send(elt, "js-var", { key, value });
                        }
                    });
                }
                
                // Handle HTML updates
                if (update.html) {
                    Object.entries(update.html).forEach(([elementId, htmlContent]) => {
                        const targetElement = document.getElementById(elementId);
                        if (targetElement) {
                            const doUpdate = () => {
                                const temp = document.createElement('div');
                                temp.innerHTML = htmlContent;
                                const newElement = temp.querySelector(targetElement.tagName);
                                
                                if (newElement) {
                                    // Clear existing content
                                    while (targetElement.firstChild) {
                                        targetElement.removeChild(targetElement.firstChild);
                                    }
                                    
                                    // Move new content
                                    while (newElement.firstChild) {
                                        targetElement.appendChild(newElement.firstChild);
                                    }
                                    
                                    // Preserve ID and update other attributes
                                    const originalId = targetElement.id;
                                    while (targetElement.attributes.length > 0) {
                                        targetElement.removeAttribute(targetElement.attributes[0].name);
                                    }
                                    targetElement.id = originalId;
                                    
                                    Array.from(newElement.attributes).forEach(attr => {
                                        if (attr.name !== 'id') {
                                            targetElement.setAttribute(attr.name, attr.value);
                                        }
                                    });
                                    
                                    send(elt, "html-updated", { elementId, targetElement });
                                }
                            };
                            
                            // Simple update without view transitions
                            doUpdate();
                        } else {
                            send(elt, "html-error", { elementId, error: "Element not found" });
                        }
                    });
                }
                
                send(elt, "processed", { update });
                
            } catch (error) {
                send(elt, "parse-error", { error, data: event.data });
            }
        };
        
        // Error handler with auto-reconnect
        eventSource.onerror = (error) => {
            send(elt, "error", { error, endpoint });
            eventSource.close();
            connections.delete(endpoint);
            
            // Auto-reconnect after 5 seconds
            setTimeout(() => {
                if (document.contains(elt) && !ignore(elt)) {
                    initSSE(elt);
                }
            }, 5000);
        };
        
        // Connection established
        eventSource.onopen = () => {
            send(elt, "connected", { endpoint });
        };
        
        send(elt, "initialized", { endpoint });
    };
    
    // Process element and its children
    let process = (n) => {
        if (n.matches) {
            if (ignore(n)) return;
            if (n.matches("[sx-connect]")) initSSE(n);
            if (n.matches("[sx-post]")) initForm(n);
        }
        if (n.querySelectorAll) {
            n.querySelectorAll("[sx-connect]").forEach(initSSE);
            n.querySelectorAll("[sx-post]").forEach(initForm);
        }
    };
    
    // Manual processing trigger
    document.addEventListener("sx:process", (evt) => process(evt.target));
    
    // Cleanup on page unload
    window.addEventListener("beforeunload", () => {
        connections.forEach(conn => conn.close());
        connections.clear();
    });
    
    // Initialize when DOM is ready
    document.addEventListener("DOMContentLoaded", () => {
        document.__ssexi_mo.observe(document.documentElement, {
            childList: true, 
            subtree: true
        });
        process(document.body);
    });
    
    // Export API for manual control
    window.SSEXI = {
        process,
        connections,
        version: "1.0.0"
    };
})();