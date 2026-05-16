package com.jd.genie.util;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import okhttp3.*;
import okhttp3.sse.EventSource;
import okhttp3.sse.EventSourceListener;
import okhttp3.sse.EventSources;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import java.io.IOException;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

/**
 * Ollama API 测试类
 *
 * 测试 Ollama 本地大语言模型 API 的各种功能
 *
 * 前置条件:
 * 1. 本地需要安装并启动 Ollama 服务
 * 2. 默认地址: http://localhost:11434
 * 3. 需要拉取至少一个模型，如: ollama pull qwen2.5
 *
 * 参考文档: https://github.com/ollama/ollama/blob/main/docs/api.md
 */
@Slf4j
@SpringBootTest
public class OllamaApiTest {

    private static final String OLLAMA_BASE_URL = "http://localhost:11434";
    private static final String DEFAULT_MODEL = "qwen3:14b";
    private static final int TIMEOUT_SECONDS = 60;

    private OkHttpClient httpClient;
    private ObjectMapper objectMapper;
    private String ollamaBaseUrl;

    @BeforeEach
    public void setUp() {
        httpClient = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build();

        objectMapper = new ObjectMapper();

        // 可以通过环境变量配置 Ollama 地址
        ollamaBaseUrl = System.getenv().getOrDefault("OLLAMA_BASE_URL", OLLAMA_BASE_URL);
        log.info("Ollama API 地址: {}", ollamaBaseUrl);
    }

    /**
     * 测试健康检查 - 验证 Ollama 服务是否运行
     */
    @Test
    public void testHealthCheck() throws IOException {
        log.info("=== 测试健康检查 ===");

        Request request = new Request.Builder()
                .url(ollamaBaseUrl)
                .get()
                .build();

        try (Response response = httpClient.newCall(request).execute()) {
            if (response.isSuccessful()) {
                log.info("Ollama 服务运行正常");
                String body = response.body().string();
                log.info("响应: {}", body);
            } else {
                log.error("Ollama 服务未响应，状态码: {}", response.code());
            }
        }
    }

    /**
     * 测试列出所有已安装的模型
     */
    @Test
    public void testListModels() throws IOException {
        log.info("=== 测试列出模型 ===");

        Request request = new Request.Builder()
                .url(ollamaBaseUrl + "/api/tags")
                .get()
                .build();

        try (Response response = httpClient.newCall(request).execute()) {
            if (response.isSuccessful()) {
                String responseBody = response.body().string();
                log.info("已安装的模型列表: {}", responseBody);

                JsonNode jsonNode = objectMapper.readTree(responseBody);
                JsonNode models = jsonNode.get("models");
                if (models != null && models.isArray()) {
                    log.info("找到 {} 个模型:", models.size());
                    models.forEach(model -> {
                        String name = model.get("name").asText();
                        log.info("  - {}", name);
                    });
                }
            } else {
                log.error("获取模型列表失败，状态码: {}", response.code());
            }
        }
    }

    /**
     * 测试简单的文本生成 (非流式)
     */
    @Test
    public void testGenerate() throws IOException {
        log.info("=== 测试文本生成 ===");

        String prompt = "用一句话介绍什么是人工智能";

        String jsonBody = String.format(
                "{\"model\": \"%s\", \"prompt\": \"%s\", \"stream\": false}",
                DEFAULT_MODEL, prompt
        );

        Request request = new Request.Builder()
                .url(ollamaBaseUrl + "/api/generate")
                .post(RequestBody.create(jsonBody, MediaType.parse("application/json")))
                .build();

        try (Response response = httpClient.newCall(request).execute()) {
            if (response.isSuccessful()) {
                String responseBody = response.body().string();
                log.info("生成响应: {}", responseBody);

                JsonNode jsonNode = objectMapper.readTree(responseBody);
                String responseText = jsonNode.get("response").asText();
                log.info("模型回复: {}", responseText);
            } else {
                log.error("生成失败，状态码: {}", response.code());
            }
        }
    }

    /**
     * 测试流式文本生成
     */
    @Test
    public void testGenerateStream() throws InterruptedException {
        log.info("=== 测试流式文本生成 ===");

        String prompt = "写一首关于春天的短诗";

        String jsonBody = String.format(
                "{\"model\": \"%s\", \"prompt\": \"%s\", \"stream\": true}",
                DEFAULT_MODEL, prompt
        );

        CountDownLatch latch = new CountDownLatch(1);
        AtomicReference<StringBuilder> fullResponse = new AtomicReference<>(new StringBuilder());

        Request request = new Request.Builder()
                .url(ollamaBaseUrl + "/api/generate")
                .post(RequestBody.create(jsonBody, MediaType.parse("application/json")))
                .build();

        EventSource.Factory factory = EventSources.createFactory(httpClient);
        factory.newEventSource(request, new EventSourceListener() {
            @Override
            public void onOpen(@NotNull EventSource eventSource, @NotNull Response response) {
                log.info("流式连接已建立");
            }

            @Override
            public void onEvent(@NotNull EventSource eventSource, @Nullable String id,
                                @Nullable String type, @NotNull String data) {
                try {
                    JsonNode jsonNode = objectMapper.readTree(data);
                    if (jsonNode.has("response")) {
                        String responseText = jsonNode.get("response").asText();
                        fullResponse.get().append(responseText);
                        System.out.print(responseText); // 实时输出
                    }

                    if (jsonNode.has("done") && jsonNode.get("done").asBoolean()) {
                        log.info("\n流式生成完成");
                        latch.countDown();
                    }
                } catch (Exception e) {
                    log.error("处理事件数据失败", e);
                }
            }

            @Override
            public void onClosed(@NotNull EventSource eventSource) {
                log.info("流式连接已关闭");
            }

            @Override
            public void onFailure(@NotNull EventSource eventSource, @Nullable Throwable t,
                                  @Nullable Response response) {
                log.error("流式连接失败", t);
                latch.countDown();
            }
        });

        boolean completed = latch.await(TIMEOUT_SECONDS, TimeUnit.SECONDS);
        if (completed) {
            log.info("\n完整回复: {}", fullResponse.get());
        } else {
            log.error("流式生成超时");
        }
    }

    /**
     * 测试聊天接口
     */
    @Test
    public void testChat() throws IOException {
        log.info("=== 测试聊天接口 ===");

        String jsonBody = String.format(
                "{\"model\": \"%s\", \"messages\": [{\"role\": \"user\", \"content\": \"你好，请介绍一下你自己\"}], \"stream\": false}",
                DEFAULT_MODEL
        );

        Request request = new Request.Builder()
                .url(ollamaBaseUrl + "/api/chat")
                .post(RequestBody.create(jsonBody, MediaType.parse("application/json")))
                .build();

        try (Response response = httpClient.newCall(request).execute()) {
            if (response.isSuccessful()) {
                String responseBody = response.body().string();
                log.info("聊天响应: {}", responseBody);

                JsonNode jsonNode = objectMapper.readTree(responseBody);
                JsonNode message = jsonNode.get("message");
                if (message != null) {
                    String content = message.get("content").asText();
                    log.info("模型回复: {}", content);
                }
            } else {
                log.error("聊天失败，状态码: {}", response.code());
            }
        }
    }

    /**
     * 测试流式聊天
     */
    @Test
    public void testChatStream() throws InterruptedException {
        log.info("=== 测试流式聊天 ===");

        String jsonBody = String.format(
                "{\"model\": \"%s\", \"messages\": [{\"role\": \"user\", \"content\": \"讲一个简短的笑话\"}], \"stream\": true}",
                DEFAULT_MODEL
        );

        CountDownLatch latch = new CountDownLatch(1);
        AtomicReference<StringBuilder> fullResponse = new AtomicReference<>(new StringBuilder());

        Request request = new Request.Builder()
                .url(ollamaBaseUrl + "/api/chat")
                .post(RequestBody.create(jsonBody, MediaType.parse("application/json")))
                .build();

        EventSource.Factory factory = EventSources.createFactory(httpClient);
        factory.newEventSource(request, new EventSourceListener() {
            @Override
            public void onOpen(@NotNull EventSource eventSource, @NotNull Response response) {
                log.info("聊天流式连接已建立");
            }

            @Override
            public void onEvent(@NotNull EventSource eventSource, @Nullable String id,
                                @Nullable String type, @NotNull String data) {
                try {
                    JsonNode jsonNode = objectMapper.readTree(data);
                    if (jsonNode.has("message")) {
                        JsonNode messageNode = jsonNode.get("message");
                        if (messageNode.has("content")) {
                            String content = messageNode.get("content").asText();
                            fullResponse.get().append(content);
                            System.out.print(content);
                        }
                    }

                    if (jsonNode.has("done") && jsonNode.get("done").asBoolean()) {
                        log.info("\n流式聊天完成");
                        latch.countDown();
                    }
                } catch (Exception e) {
                    log.error("处理聊天事件数据失败", e);
                }
            }

            @Override
            public void onFailure(@NotNull EventSource eventSource, @Nullable Throwable t,
                                  @Nullable Response response) {
                log.error("流式聊天失败", t);
                latch.countDown();
            }
        });

        boolean completed = latch.await(TIMEOUT_SECONDS, TimeUnit.SECONDS);
        if (completed) {
            log.info("\n完整回复: {}", fullResponse.get());
        }
    }

    /**
     * 测试多轮对话
     */
    @Test
    public void testMultiTurnChat() throws IOException {
        log.info("=== 测试多轮对话 ===");

        // 构建对话历史
        String messagesJson = """
                [
                    {"role": "user", "content": "我叫小明"},
                    {"role": "assistant", "content": "你好小明，很高兴认识你"},
                    {"role": "user", "content": "我叫什么名字"}
                ]
                """;

        String jsonBody = String.format(
                "{\"model\": \"%s\", \"messages\": %s, \"stream\": false}",
                DEFAULT_MODEL, messagesJson
        );

        Request request = new Request.Builder()
                .url(ollamaBaseUrl + "/api/chat")
                .post(RequestBody.create(jsonBody, MediaType.parse("application/json")))
                .build();

        try (Response response = httpClient.newCall(request).execute()) {
            if (response.isSuccessful()) {
                String responseBody = response.body().string();
                JsonNode jsonNode = objectMapper.readTree(responseBody);
                JsonNode message = jsonNode.get("message");
                if (message != null) {
                    String content = message.get("content").asText();
                    log.info("模型回复: {}", content);
                }
            }
        }
    }

    /**
     * 测试设置生成参数
     */
    @Test
    public void testGenerateWithParameters() throws IOException {
        log.info("=== 测试生成参数设置 ===");

        String jsonBody = String.format(
                "{\"model\": \"%s\", \"prompt\": \"写一首关于科技的诗\", \"stream\": false, \"options\": {\"temperature\": 0.8, \"top_p\": 0.9, \"max_tokens\": 100}}",
                DEFAULT_MODEL
        );

        Request request = new Request.Builder()
                .url(ollamaBaseUrl + "/api/generate")
                .post(RequestBody.create(jsonBody, MediaType.parse("application/json")))
                .build();

        try (Response response = httpClient.newCall(request).execute()) {
            if (response.isSuccessful()) {
                String responseBody = response.body().string();
                JsonNode jsonNode = objectMapper.readTree(responseBody);
                String responseText = jsonNode.get("response").asText();
                log.info("模型回复 (temperature=0.8): {}", responseText);

                // 显示生成统计信息
                if (jsonNode.has("prompt_eval_count")) {
                    log.info("提示词评估次数: {}", jsonNode.get("prompt_eval_count"));
                }
                if (jsonNode.has("eval_count")) {
                    log.info("生成次数: {}", jsonNode.get("eval_count"));
                }
            }
        }
    }

    /**
     * 测试获取模型信息
     */
    @Test
    public void testShowModelInfo() throws IOException {
        log.info("=== 测试获取模型信息 ===");

        String jsonBody = String.format("{\"name\": \"%s\"}", DEFAULT_MODEL);

        Request request = new Request.Builder()
                .url(ollamaBaseUrl + "/api/show")
                .post(RequestBody.create(jsonBody, MediaType.parse("application/json")))
                .build();

        try (Response response = httpClient.newCall(request).execute()) {
            if (response.isSuccessful()) {
                String responseBody = response.body().string();
                log.info("模型详细信息: {}", responseBody);

                JsonNode jsonNode = objectMapper.readTree(responseBody);
                if (jsonNode.has("license")) {
                    log.info("许可证: {}", jsonNode.get("license").asText());
                }
                if (jsonNode.has("modelfile")) {
                    log.info("Modelfile: {}", jsonNode.get("modelfile").asText());
                }
            }
        }
    }

    /**
     * 综合测试：完整对话流程
     */
    @Test
    public void testCompleteConversationFlow() throws IOException {
        log.info("=== 综合测试：完整对话流程 ===");

        // 第一步：检查服务健康状态
        log.info("步骤1: 检查服务状态");
        testHealthCheck();

        // 第二步：列出可用模型
        log.info("\n步骤2: 列出可用模型");
        testListModels();

        // 第三步：进行对话
        log.info("\n步骤3: 进行对话");
        String prompt = "请用3句话解释机器学习的基本概念";

        String jsonBody = String.format(
                "{\"model\": \"%s\", \"prompt\": \"%s\", \"stream\": false}",
                DEFAULT_MODEL, prompt
        );

        Request request = new Request.Builder()
                .url(ollamaBaseUrl + "/api/generate")
                .post(RequestBody.create(jsonBody, MediaType.parse("application/json")))
                .build();

        try (Response response = httpClient.newCall(request).execute()) {
            if (response.isSuccessful()) {
                String responseBody = response.body().string();
                JsonNode jsonNode = objectMapper.readTree(responseBody);
                String responseText = jsonNode.get("response").asText();
                log.info("最终回复: {}", responseText);
                log.info("\n综合测试完成！");
            }
        }
    }
}
