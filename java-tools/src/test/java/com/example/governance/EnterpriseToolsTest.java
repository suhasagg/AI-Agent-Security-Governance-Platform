package com.example.governance;
import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
class EnterpriseToolsTest {
 @Test void deploymentRead(){
  var x=new EnterpriseTools().get_deployment("api","dev");
  assertEquals("healthy",x.get("status"));
 }
}