"""
Main A2A endpoint for handling JSON-RPC requests from Telex.
"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from app.models import JSONRPCRequest, JSONRPCResponse, JSONRPCError, MessageParams, ExecuteParams
from .workflow_handlers import handle_message_send, handle_execute

router = APIRouter()

# Map method names to their handler functions and Pydantic models
METHOD_HANDLERS = {
    "message/send": (handle_message_send, MessageParams),
    "execute": (handle_execute, ExecuteParams),
}

@router.post("/a2a/agent/DecisionNote")
async def handle_a2a_request(request: Request):
    """
    Main A2A endpoint - handles all JSON-RPC requests from Telex.
    """
    body = await request.json()
    request_id = body.get("id")

    try:
        # Basic validation
        if body.get("jsonrpc") != "2.0" or "id" not in body or "method" not in body:
            raise ValidationError("Invalid JSON-RPC request structure.", [])
        
        rpc_request = JSONRPCRequest(**body)
        
        if rpc_request.method in METHOD_HANDLERS:
            handler, params_model = METHOD_HANDLERS[rpc_request.method]
            
            # Validate params based on the method
            try:
                params = params_model(**rpc_request.params)
            except ValidationError as e:
                return JSONResponse(
                    status_code=400,
                    content=JSONRPCResponse(
                        id=request_id,
                        error=JSONRPCError(
                            code=-32602,
                            message="Invalid params",
                            data={"details": e.errors()}
                        )
                    ).model_dump(exclude_none=True)
                )

            result = await handler(params)
            response = JSONRPCResponse(id=rpc_request.id, result=result)
        else:
            response = JSONRPCResponse(
                id=rpc_request.id,
                error=JSONRPCError(code=-32601, message="Method not found")
            )
            
        return JSONResponse(content=response.model_dump(exclude_none=True))

    except ValidationError as e:
        return JSONResponse(
            status_code=400,
            content=JSONRPCResponse(
                id=request_id,
                error=JSONRPCError(
                    code=-32600,
                    message="Invalid Request",
                    data={"details": e.errors()}
                )
            ).model_dump(exclude_none=True)
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=JSONRPCResponse(
                id=request_id,
                error=JSONRPCError(
                    code=-32603,
                    message="Internal error",
                    data={"details": str(e)}
                )
            ).model_dump(exclude_none=True)
        )
