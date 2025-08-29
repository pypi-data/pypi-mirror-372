# Utils Package

This package provides utility functions and classes for common operations in the application, including logging and Azure Service Bus integration.

## Installation

The package is managed using Poetry. To install dependencies:

```bash
poetry install
```

## Features

### Logger

A simple logging utility that provides a standardized way to set up logging across the application.

#### Usage

```python
from abs_utils.logger import setup_logger

# Create a logger instance
logger = setup_logger("my_module")

# Use the logger
logger.info("This is an info message")
logger.error("This is an error message")
```

### Azure Service Bus Integration

Provides functionality to interact with Azure Service Bus for message queuing and event handling.

#### AzureServiceBus Class

A wrapper class for Azure Service Bus operations.

```python
from abs_utils.azure_service_bus import AzureServiceBus

# Initialize the service bus client
service_bus = AzureServiceBus(
    connection_string="your_connection_string",
    queue_name="your_queue_name"
)

# Send a message
await service_bus.send({"key": "value"})
```

#### Event Decorator

A decorator that automatically sends events to Azure Service Bus after function execution. This is particularly useful for tracking entity operations in your application.

```python
from fastapi import APIRouter, Depends, Request
from dependency_injector.wiring import inject, Provide
from abs_utils.azure_service_bus import azure_event_decorator, AzureServiceBus

router = APIRouter()

@router.post("/{entity_name}/records")
@inject
@azure_event_decorator(event_type="record_created")
async def create_record(
    entity_name: str,
    data: dict,
    request: Request,
    azure_service_bus: AzureServiceBus = Depends(Provide[Container.azure_service_bus]),
    service: YourService = Depends(Provide[Container.yourService])
):
    # Your function logic here
    return await service.create(data, entity_name)
```

The decorator automatically creates and sends an event payload with the following structure:
```json
{
    "event_id": "uuid",
    "event_type": "record_created",
    "entity_name": "your_entity_name",
    "entity_id": "record_id",
    "payload": {
        // Your data payload
    },
    "user": {
        "id": "user_id",
        "uuid": "user_uuid",
        "email": "user_email",
        "name": "user_name"
    }
}
```

Key features of the decorator:
1. Automatically captures the entity name from the route parameters
2. Extracts user information from the request state
3. Generates a unique event ID for each event
4. Handles errors gracefully with logging
5. Works seamlessly with FastAPI dependency injection

## Dependencies

- Python 3.x
- azure-servicebus
- fastapi
- logging
- dependency-injector

## Contributing

When adding new utilities to this package:
1. Place new modules in the appropriate subdirectory under `abs_utils/`
2. Add proper documentation and type hints
3. Update this README with usage examples
4. Add tests for new functionality
