# Changelog

## [1.0.5] - 2025-08-27

### Changed
- updated readme documentation

## [1.0.4] - 2025-06-11

### Changed
- removed static dead_letter_queue_name (dlq_name) value from failed_messages 
    to a passed parameter in the class constructor with a default value of ```failed_messages```

## [1.0.1] - 2025-06-11

### Changed
- Updated README with improved documentation
- Fixed typos in examples
- Enhanced Docker Compose examples
- Improved formatting and clarity

## [1.0.0] - 2025-06-10

### Added
- Initial release of RabbitMQ Easy
- Automatic connection management with retry logic
- Dead letter queue support
- Environment variable configuration
- Comprehensive logging with emoji indicators
- Context manager support
- Health check functionality
- Queue information retrieval
- Batch queue setup
- Custom exceptions for better error handling
- Complete test suite
- Documentation and examples

### Features
- Idempotent queue and exchange creation
- Automatic reconnection on connection loss
- Configurable retry logic
- Support for both file and console logging
- Production-ready error handling