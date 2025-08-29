from functools import wraps
from fastapi import Request
from typing import Any, Callable
from .azure_service_bus import AzureServiceBus
from uuid import uuid4
import json
from ..constants import ON_RECORD_UPDATION
def azure_event_decorator(event_type: str):
    """
    A decorator that sends a message to Azure Service Bus after the function execution.
    
    Args:
        event_name (str): The name of the event to be sent
    
    Returns:
        Callable: The decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Extract required parameters from kwargs
            request:Request = kwargs.get('request')
            data:Any = kwargs.get('data') or None
            azure_service_bus:AzureServiceBus = kwargs.get('azure_service_bus')
            entity_id:str = kwargs.get('entity_id') or None
            app_id:str = kwargs.get('app_id') or None
            record_id:str = kwargs.get('record_id') or None
            form_id:str = kwargs.get('form_id') or None

            if request.state and hasattr(request.state, 'user'):
                user = {
                    "id": request.state.user.id,
                    "uuid": request.state.user.uuid,
                    "email": request.state.user.email,
                    "name": request.state.user.name,
                }
            else:
                user = {
                    "id": None,
                    "uuid": None,
                    "email": None,
                    "name": None,
                }
            
            # Execute the original function
            result = await func(*args, **kwargs)

            if event_type != ON_RECORD_UPDATION:
                data = result
            
            event_payload = {
                "event_id": str(uuid4()),
                "event_key": event_type,
                "collection_name": f"entity_{entity_id}",
                "record_id": record_id,
                "form_id": form_id,
                "payload": data,
                "result": result,
                "user": user,
            }
            # Send message to Azure Service Bus
            # event_payload = json.dumps(event_payload)
            await azure_service_bus.send(event_payload)
            return result
        return wrapper
    return decorator
