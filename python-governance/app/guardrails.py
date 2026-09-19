import json
from agents import GuardrailFunctionOutput,ToolGuardrailFunctionOutput
from agents import input_guardrail,output_guardrail
from agents.decorators import tool_input_guardrail,tool_output_guardrail
from .security import scan_text,redact

@input_guardrail(name="security-input",run_in_parallel=False)
async def security_input(ctx,agent,input):
    text=str(input);s=scan_text(text)
    blocked=s["secret"] or s["prompt_injection"]
    return GuardrailFunctionOutput(output_info=s,tripwire_triggered=blocked)

@output_guardrail(name="security-output")
async def security_output(ctx,agent,output):
    text=str(output);s=scan_text(text)
    return GuardrailFunctionOutput(output_info={"scan":s,"redacted":redact(text)},
      tripwire_triggered=s["secret"])

@tool_input_guardrail
def mcp_input_guard(data):
    args=data.context.tool_arguments or "{}"
    s=scan_text(args)
    if s["secret"] or s["prompt_injection"]:
        return ToolGuardrailFunctionOutput.reject_content("Tool call blocked by security policy.")
    return ToolGuardrailFunctionOutput.allow()

@tool_output_guardrail
def mcp_output_guard(data):
    text=str(data.output)
    s=scan_text(text)
    if s["secret"]:
        return ToolGuardrailFunctionOutput.reject_content("Tool output contained protected data.")
    return ToolGuardrailFunctionOutput.allow()
