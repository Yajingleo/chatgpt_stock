# Claude AI Agent Collaboration Rules (Stock Selection Project)

## Project Overview
This is a stock selection and analysis project with the following main features:
- S&P 500 stock energy analysis (`sp_500_energy.py`)
- Stock news crawler (`stock_news_crawler.py`)
- Data support for investment decision-making

## Agent Role Definitions

### 🔍 Data Analyst Agent
**Responsibilities:**
- Handle code optimization and feature extensions for `sp_500_energy.py`
- Stock data processing, calculation, and statistical analysis
- Performance optimization and parallel processing improvements

**Collaboration Rules:**
- Must maintain backward compatibility when modifying stock analysis logic
- Add detailed docstrings when creating new indicator calculation functions
- Exercise special caution with financial calculation code modifications to ensure accuracy

### 📰 Information Collector Agent
**Responsibilities:**
- Handle web crawling and data acquisition for `stock_news_crawler.py`
- News source expansion and data parsing optimization
- API integration and data format standardization

**Collaboration Rules:**
- Implement error handling and retry mechanisms when adding new data sources
- Crawler code must comply with websites' robots.txt and terms of service
- Maintain reasonable data acquisition frequency to avoid excessive requests

### 🏗️ System Architect Agent
**Responsibilities:**
- Overall project architecture design and code refactoring
- Dependency management and environment configuration
- Code quality and best practices enforcement

**Collaboration Rules:**
- Consider impact on existing functionality for major architectural changes
- Update installation instructions in README.md when adding new dependencies
- Maintain functionality integrity during code refactoring

## General Collaboration Principles

### 📝 Code Standards
1. **Python Code Style:** Follow PEP 8 standards
2. **Documentation Requirements:** All functions must have detailed docstrings
3. **Variable Naming:** Use descriptive variable names, especially for financial terms
4. **Error Handling:** All external API calls must have appropriate exception handling

### 🔄 Version Control Collaboration
1. **Branching Strategy:** Use separate feature branches for each new functionality
2. **Commit Messages:** Use meaningful commit messages including change types
3. **Code Review:** Core algorithm modifications require additional validation

### 📊 Data Processing Collaboration
1. **Data Validation:** All externally acquired data needs integrity validation
2. **Caching Strategy:** Implement reasonable caching mechanisms for frequently accessed data
3. **Performance Monitoring:** Record execution time for key operations

### 🛡️ Security and Reliability
1. **API Key Management:** Sensitive information must not be hardcoded; use environment variables
2. **Rate Limiting:** Implement request frequency limits to avoid API service bans
3. **Data Backup:** Important analysis results need to be saved to files

## Specific Feature Collaboration Rules

### SP500 Energy Analysis Collaboration
- **Data Acquisition Agent** ensures yfinance data availability
- **Analysis Agent** handles energy calculation and indicator optimization
- **System Agent** manages parallel processing performance optimization

### News Crawler Collaboration
- **Information Collector Agent** handles news source expansion and parsing
- **Data Analysis Agent** handles news sentiment analysis (if needed)
- **System Agent** manages crawler stability and error recovery

## Output Format Standards

### Analysis Results Output
```python
# Standard output format example
{
    "timestamp": "2025-09-07T10:00:00Z",
    "analysis_type": "energy_analysis",
    "parameters": {
        "lookback_days": 10,
        "num_processes": 10
    },
    "results": {
        "top_energy": [...],
        "bottom_energy": [...],
        "top_return": [...],
        "bottom_return": [...]
    }
    "news": {
        "stock_ticker": [...],
    }
}
```

### Error Reporting Format
```python
# Standard error format
{
    "error_type": "API_ERROR",
    "timestamp": "2025-09-07T10:00:00Z",
    "component": "stock_data_fetcher",
    "details": "Detailed error information",
    "suggested_action": "Recommended solution"
}
```

## Documentation Update Collaboration
1. **README.md Updates:** Synchronously update usage instructions when adding new features
2. **API Documentation:** All public functions must have clear parameter and return value descriptions
3. **Example Code:** Provide code examples for actual use cases

## Performance and Monitoring
1. **Execution Time Recording:** Statistics for key operation durations
2. **Memory Usage Monitoring:** Memory optimization for big data processing
3. **Network Request Monitoring:** API call success rate and response time tracking

## Best Practices

### Code Quality
- Write clean, readable, and maintainable code
- Use type hints where appropriate
- Implement comprehensive unit tests for critical functions
- Follow DRY (Don't Repeat Yourself) principles

### Data Handling
- Validate all input data before processing
- Handle edge cases gracefully
- Implement proper logging for debugging purposes
- Use consistent data formats across the project

### Security Considerations
- Never expose sensitive credentials in code
- Validate and sanitize user inputs
- Implement proper authentication for external APIs
- Use secure communication protocols (HTTPS)

### Testing Strategy
- Write unit tests for all core functions
- Implement integration tests for API interactions
- Test error handling scenarios
- Maintain test coverage above 80%

## Communication Protocols

### Inter-Agent Communication
- Use standardized message formats for agent-to-agent communication
- Implement clear interfaces between different agent responsibilities
- Establish error propagation mechanisms across agent boundaries
- Maintain audit logs for all inter-agent transactions

### Human-Agent Interaction
- Provide clear progress indicators for long-running operations
- Implement user-friendly error messages with actionable suggestions
- Support incremental result delivery for better user experience
- Maintain context awareness across conversation sessions

---

*This file defines the collaboration relationships and rules among AI agents in this project, ensuring code quality and project maintainability.*