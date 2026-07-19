# Performance Optimization Checklist

## Targets

| Metric | Target | Critical |
|--------|--------|----------|
| API P95 | < 200ms | < 500ms |
| API P99 | < 500ms | < 1s |
| DB Query | < 100ms | < 500ms |
| Frontend LCP | < 2.5s | < 4s |
| Frontend FID | < 100ms | < 300ms |
| Frontend CLS | < 0.1 | < 0.25 |

## Database

### Query Optimization

- [ ] Check for N+1 queries
- [ ] Add missing indexes (check `EXPLAIN ANALYZE`)
- [ ] Use `SELECT` only needed columns
- [ ] Add pagination for large result sets
- [ ] Use connection pooling
- [ ] Consider query caching (Redis)

### Common Index Patterns

```sql
-- Foreign keys
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Frequently filtered columns
CREATE INDEX idx_orders_status ON orders(status);

-- Composite for common queries
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Partial index for specific conditions
CREATE INDEX idx_active_users ON users(email) WHERE active = true;
```

## API/Backend

### Response Time

- [ ] Add caching (Redis/Memcached)
- [ ] Use async/await properly
- [ ] Avoid blocking operations
- [ ] Implement request batching
- [ ] Use CDN for static assets

### Memory

- [ ] Check for memory leaks
- [ ] Use streaming for large data
- [ ] Implement pagination
- [ ] Release resources properly

### Concurrency

- [ ] Use connection pools
- [ ] Implement rate limiting
- [ ] Add request queuing
- [ ] Use background jobs for heavy tasks

## Frontend

### Loading Performance

- [ ] Code splitting / lazy loading
- [ ] Image optimization (WebP, lazy load)
- [ ] Minify JS/CSS
- [ ] Enable gzip/brotli
- [ ] Use CDN
- [ ] Preload critical resources

### Runtime Performance

- [ ] Debounce/throttle events
- [ ] Virtual scrolling for lists
- [ ] Memoize expensive computations
- [ ] Avoid layout thrashing
- [ ] Use Web Workers for heavy computation

## Monitoring

### Key Metrics to Track

- Request latency (P50, P95, P99)
- Error rate
- Database query time
- Memory usage
- CPU usage
- Active connections

### Tools

- APM: Datadog, New Relic, Sentry
- Profiling: py-spy, node --prof, Chrome DevTools
- Load testing: k6, wrk, Apache Bench
