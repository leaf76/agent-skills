#!/bin/bash
# Performance profiling helper
set -e

TARGET="${1:-}"
TYPE="${2:-auto}"

profile_python() {
    echo "🐍 Profiling Python..."
    
    if [ -n "$TARGET" ]; then
        # cProfile
        python -m cProfile -s cumulative "$TARGET" 2>/dev/null | head -50
        
        # memory_profiler (if installed)
        if python -c "import memory_profiler" 2>/dev/null; then
            echo ""
            echo "Memory Profile:"
            python -m memory_profiler "$TARGET" 2>/dev/null || true
        fi
    else
        echo "Usage: $0 <script.py>"
    fi
}

profile_node() {
    echo "📘 Profiling Node.js..."
    
    if [ -n "$TARGET" ]; then
        # V8 profiler
        node --prof "$TARGET"
        node --prof-process isolate-*.log > profile.txt
        head -100 profile.txt
        rm -f isolate-*.log
    else
        echo "Usage: $0 <script.js>"
    fi
}

analyze_db() {
    echo "🗄️  Analyzing database queries..."
    
    # PostgreSQL EXPLAIN
    if [ -n "$TARGET" ]; then
        echo "Running EXPLAIN ANALYZE..."
        psql -c "EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) $TARGET"
    else
        echo "Usage: $0 '<SQL query>' db"
    fi
}

benchmark_api() {
    echo "🌐 Benchmarking API endpoint..."
    
    if [ -n "$TARGET" ]; then
        # Using wrk if available, otherwise curl
        if command -v wrk &> /dev/null; then
            wrk -t4 -c100 -d10s "$TARGET"
        elif command -v ab &> /dev/null; then
            ab -n 1000 -c 10 "$TARGET"
        else
            echo "Timing single request..."
            time curl -s -o /dev/null -w "Total: %{time_total}s\nConnect: %{time_connect}s\nTTFB: %{time_starttransfer}s\n" "$TARGET"
        fi
    else
        echo "Usage: $0 <url> api"
    fi
}

# Auto-detect or use specified type
case "$TYPE" in
    python|py)
        profile_python
        ;;
    node|js)
        profile_node
        ;;
    db|sql)
        analyze_db
        ;;
    api|http)
        benchmark_api
        ;;
    auto)
        if [[ "$TARGET" == *.py ]]; then
            profile_python
        elif [[ "$TARGET" == *.js ]] || [[ "$TARGET" == *.ts ]]; then
            profile_node
        elif [[ "$TARGET" == http* ]]; then
            benchmark_api
        else
            echo "Usage: $0 <target> {python|node|db|api}"
        fi
        ;;
    *)
        echo "Usage: $0 <target> {python|node|db|api|auto}"
        exit 1
        ;;
esac
