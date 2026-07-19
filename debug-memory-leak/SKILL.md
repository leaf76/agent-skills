---
name: debug-memory-leak
description: Debug memory leaks in the application
---

# Debug Memory Leak Workflow

This workflow helps identify and debug memory leaks in the Cloudflare Workers application.

## Steps

1. **Enable Memory Debugging**
   - Add memory tracking to the worker
   - Enable detailed logging for memory usage
   - Set up memory profiling hooks

2. **Collect Memory Metrics**
   ```bash
   # Check current memory usage patterns
   wrangler tail --format=json | jq '.event' | grep -i memory
   ```

3. **Analyze Heap Usage**
   - Review object allocation patterns
   - Check for unclosed connections or uncached data
   - Identify long-lived objects that should be garbage collected

4. **Common Memory Leak Sources**
   - **Durable Objects**: Check for unclosed WebSocket connections
   - **KV Storage**: Verify proper cleanup of large values
   - **Caches**: Ensure cache size limits are enforced
   - **Async Operations**: Confirm all futures are properly awaited

5. **Debugging Commands**
   ```bash
   # Monitor memory usage over time
   wrangler tail --format=pretty | grep "Memory usage"

   # Check for hanging promises
   wrangler tail --format=json | jq '.log[] | select(.message | contains("promise"))'
   ```

6. **Fix Common Issues**
   - Add explicit cleanup in Durable Object `close()` methods
   - Implement cache eviction policies
   - Use weak references where appropriate
   - Ensure proper error handling to prevent resource leaks

7. **Validate Fixes**
   - Run load tests with memory monitoring
   - Verify memory usage stabilizes after garbage collection
   - Check for memory growth under sustained load

## Tips

- Use `console.log` with memory usage timestamps
- Monitor Durable Object lifecycle closely
- Check for event listener leaks
- Review async/await patterns for unresolved promises
- Use `WeakMap` or `WeakSet` for temporary object storage

## Related Files

- `src/lib.rs` - Main worker entry point
- `src/durable_objects/` - Durable Object implementations
- `src/services/cache.rs` - Cache management
- `src/middleware/` - Request/response handling
