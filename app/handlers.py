from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

async def custom_pydantic_validation_handler(request: Request, exc: ValidationError):
    """
    Catch Pydantic ValidationError globally and return custom JSON format.
    """
    custom_errors = []
    
    for err in exc.errors():
        # แปลง loc tuple -> dot notation string
        # เช่น ('images', 0, 'dataUrl') -> "images.0.dataUrl"
        field_name = ".".join([str(x) for x in err['loc']])
        
        custom_errors.append({
            "field": field_name,
            "message": err['msg']
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation Failed",
            "errors": custom_errors
        }
    )