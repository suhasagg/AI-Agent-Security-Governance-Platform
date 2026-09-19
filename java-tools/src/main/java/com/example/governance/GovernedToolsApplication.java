package com.example.governance;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;
@SpringBootApplication
public class GovernedToolsApplication {
 public static void main(String[] args){SpringApplication.run(GovernedToolsApplication.class,args);}
 @Bean ToolCallbackProvider tools(EnterpriseTools tools){
  return MethodToolCallbackProvider.builder().toolObjects(tools).build();
 }
}