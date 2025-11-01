"""
Main A2A endpoint for handling JSON-RPC requests from Telex.
"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.models import JSONRPCRequest, JSONRPCResponse, JSONRPCError
from routes.workflow_handlers import (
    handle_add_decision_node,
    handle_list_decisions_node,
)
from utils.formatters import ResponseFormatter

router = APIRouter()

from .workflow_handlers import handle_message_send

# Map method names to their handler functions
METHOD_HANDLERS = {
    "message/send": handle_message_send,
    # Add other method handlers here if needed
}


@router.post("/a2a")
async def handle_a2a_request(request: Request):
    """
    Main A2A endpoint - handles all JSON-RPC requests from Telex.
    """
    try:
        body = await request.json()
        
        # Basic validation
        if body.get("jsonrpc") != "2.0" or "id" not in body or "method" not in body:
            return JSONResponse(
                status_code=400,
                content=JSONRPCResponse(
                    id=body.get("id"),
                    error=JSONRPCError(code=-32600, message="Invalid Request")
                ).model_dump(exclude_none=True)
            )
        
        rpc_request = JSONRPCRequest(**body)
        
        if rpc_request.method in METHOD_HANDLERS:
            handler = METHOD_HANDLERS[rpc_request.method]
            result = await handler(rpc_request.params)
            response = JSONRPCResponse(id=rpc_request.id, result=result)
        else:
            response = JSONRPCResponse(
                id=rpc_request.id,
                error=JSONRPCError(code=-32601, message="Method not found")
            )
            
        return JSONResponse(content=response.model_dump(exclude_none=True))

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=JSONRPCResponse(
                id=body.get("id") if "body" in locals() else None,
                error=JSONRPCError(
                    code=-32603,
                    message="Internal error",
                    data={"details": str(e)}
                )
            ).model_dump(exclude_none=True)
        )
