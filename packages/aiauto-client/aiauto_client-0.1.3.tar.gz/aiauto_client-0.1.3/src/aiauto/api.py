from typing import Optional, List, Union
from .serializer import object_to_json
from .core import StudyWrapper, AIAutoController


def create_study(
    study_name: str,
    token: str,
    direction: Optional[str] = None,
    directions: Optional[List[str]] = None,
    sampler: Union[object, dict, None] = None,
    pruner: Union[object, dict, None] = None
) -> StudyWrapper:
    if not direction and not directions:
        raise ValueError("Either 'direction' or 'directions' must be specified")

    if direction and directions:
        raise ValueError("Cannot specify both 'direction' and 'directions'")

    try:
        # Initialize controller (which ensures workspace)
        controller = AIAutoController(token)
        
        # Prepare request data for CreateStudy
        request_data = {
            "spec": {
                "studyName": study_name,
                "direction": direction or "",
                "directions": directions or [],
                "samplerJson": object_to_json(sampler),
                "prunerJson": object_to_json(pruner)
            }
        }
        
        # Call CreateStudy RPC
        response = controller.client.call_rpc("CreateStudy", request_data)
        
        # Return StudyWrapper
        return StudyWrapper(
            study_name=response.get("studyName", study_name),
            storage=controller.storage,
            controller=controller
        )

    except Exception as e:
        raise RuntimeError(f"Failed to create study: {e}") from e