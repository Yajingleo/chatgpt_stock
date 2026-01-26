# Bazel commands reference for stock analysis project
# Common commands for Google-style development workflow

## Build Commands

# Build everything
bazel build //...

# Build specific targets
bazel build //:simple_agent
bazel build //cpp:trading_algorithms
bazel build //go:data_ingestion_service

# Build with specific configs
bazel build --config=local //...
bazel build --config=ci //...

## Test Commands

# Run all tests
bazel test //...

# Run specific tests
bazel test //stock_selection/agent:all
bazel test //cpp:performance_test
bazel test //go:data_ingestion_test

# Run with coverage
bazel coverage //...

## Run Commands

# Run Python agents
bazel run //:simple_agent
bazel run //:voice_agent
bazel run //:web_server

# Run Go services
bazel run //go:data_ingestion_service
bazel run //go:news_processor_service

## Development Commands

# Query dependencies
bazel query 'deps(//:stock_agent_lib)'
bazel query 'rdeps(//..., //proto:stock_data_proto)'

# Build graph visualization
bazel query --output=graph //... | dot -Tpng > build_graph.png

# Clean builds
bazel clean
bazel clean --expunge

## Remote Execution (if configured)

# Build remotely
bazel build --config=remote //...

# Clean remote cache
bazel clean --expunge_async

## Useful Development Aliases

# Add to ~/.bashrc or ~/.zshrc:
# alias bb='bazel build'
# alias bt='bazel test'
# alias br='bazel run'
# alias bq='bazel query'

## IDE Integration

# Generate compile_commands.json for C++
bazel run @hedron_compile_commands//:refresh_all

# For VS Code: Install "Bazel" extension
# For IntelliJ: Install "Bazel for IntelliJ" plugin