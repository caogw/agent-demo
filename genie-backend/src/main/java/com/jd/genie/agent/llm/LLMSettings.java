package com.jd.genie.agent.llm;

import com.alibaba.fastjson.annotation.JSONField;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * LLM 配置类
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LLMSettings {
    /**
     * 模型名称
     */
    @JSONField(name = "model")
    private String model;

    /**
     * 最大生成 token 数量
     */
    @JSONField(name = "maxTokens")
    private int maxTokens;

    /**
     * 温度参数
     */
    @JSONField(name = "temperature")
    private double temperature;

    /**
     * API 类型（openai 或 azure）
     */
    @JSONField(name = "apiType")
    private String apiType;

    /**
     * API 密钥
     */
    @JSONField(name = "apiKey")
    private String apiKey;

    /**
     * API 版本（仅适用于 Azure）
     */
    @JSONField(name = "apiVersion")
    private String apiVersion;

    /**
     * 基础 URL
     */
    @JSONField(name = "baseUrl")
    private String baseUrl;

    /**
     * 接口 URL
     */
    @JSONField(name = "interfaceUrl")
    private String interfaceUrl;

    /**
     * FunctionCall类型
     */
    @JSONField(name = "functionCallType")
    private String functionCallType;

    /**
     * 最大输入 token 数量
     */
    @JSONField(name = "maxInputTokens")
    private int maxInputTokens;

    /**
     * 额外参数
     */
    @JSONField(name = "extParams")
    private Map<String, Object> extParams;

}