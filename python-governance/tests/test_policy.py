from app.policy import evaluate
from app.security import TOKENS
def test_reader_cannot_restart():
    d=evaluate(TOKENS["demo-reader-token"],"restart_service",{"service":"api","environment":"dev"})
    assert d.effect=="deny"
def test_prod_restart_needs_approval():
    d=evaluate(TOKENS["demo-operator-token"],"restart_service",{"service":"api","environment":"production"})
    assert d.effect=="approval"
def test_cross_tenant_denied():
    d=evaluate(TOKENS["demo-admin-token"],"delete_customer",{"tenant_id":"globex","customer_id":"C1"})
    assert d.effect=="deny"
