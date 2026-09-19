from .contracts import Decision,Identity
TOOL_POLICY={
 "get_customer":{"roles":{"reader","operator","admin"},"risk":"low"},
 "get_deployment":{"roles":{"reader","operator","admin"},"risk":"low"},
 "create_ticket":{"roles":{"operator","admin"},"risk":"medium"},
 "restart_service":{"roles":{"operator","admin"},"risk":"high"},
 "delete_customer":{"roles":{"admin"},"risk":"critical"},
}
def evaluate(identity:Identity,tool:str,args:dict)->Decision:
    p=TOOL_POLICY.get(tool)
    if not p:return Decision(effect="deny",reason="tool not registered",risk="critical")
    if not set(identity.roles).intersection(p["roles"]):
        return Decision(effect="deny",reason="role not authorized",risk=p["risk"])
    if args.get("tenant_id") and args["tenant_id"]!=identity.tenant_id:
        return Decision(effect="deny",reason="cross-tenant argument denied",risk="critical")
    env=str(args.get("environment","")).lower()
    if tool=="restart_service" and env=="production":
        return Decision(effect="approval",reason="production restart requires human approval",risk="high")
    if tool=="delete_customer":
        return Decision(effect="approval",reason="destructive customer operation requires approval",risk="critical")
    return Decision(effect="allow",reason="policy satisfied",risk=p["risk"])
