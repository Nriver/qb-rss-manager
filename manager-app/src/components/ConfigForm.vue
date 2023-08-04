<template>
  <div class="edit-config-container">
    <form @submit.prevent="saveConfig" class="config-form">
      <div class="config-section">
        <h3>qBitrrent API 相关配置</h3>
        <div class="form-row">
          <label class="form-label" for="useQbApi">使用 qBitrrent API:</label>
          <input type="checkbox" v-model="config.use_qb_api" id="useQbApi" />
        </div>

        <div class="form-row">
          <label class="form-label" for="qbApiIp">qBitrrent API IP:</label>
          <input type="text" v-model="config.qb_api_ip" id="qbApiIp" />
        </div>

        <div class="form-row">
          <label class="form-label" for="qbApiPort">qBitrrent API 端口:</label>
          <input type="number" v-model="config.qb_api_port" id="qbApiPort" />
        </div>

        <div class="form-row">
          <label class="form-label" for="qbApiUsername">qBitrrent API 用户名:</label>
          <input type="text" v-model="config.qb_api_username" id="qbApiUsername" />
        </div>

        <div class="form-row">
          <label class="form-label" for="qbApiPassword">qBitrrent API 密码:</label>
          <input type="password" v-model="config.qb_api_password" id="qbApiPassword" />
        </div>

        <div class="form-row">
          <label class="form-label" for="qbExecutable">qBitrrent 可执行程序:</label>
          <input type="text" v-model="config.qb_executable" id="qbExecutable" />
        </div>
      </div>

      <div class="config-section">
        <h3>RSS 相关配置 (如使用api则无需配置)</h3>
        <div class="form-row">
          <label class="form-label" for="feedsJsonPath">Feeds JSON 路径:</label>
          <input type="text" v-model="config.feeds_json_path" id="feedsJsonPath" />
        </div>

        <div class="form-row">
          <label class="form-label" for="rssArticleFolder">RSS Article 目录:</label>
          <input type="text" v-model="config.rss_article_folder" id="rssArticleFolder" />
        </div>

        <div class="form-row">
          <label class="form-label" for="rulesPath">规则路径:</label>
          <input type="text" v-model="config.rules_path" id="rulesPath" />
        </div>
      </div>

      <button type="submit" class="save-button">保存</button>
    </form>
  </div>
</template>

<style>
.edit-config-container {
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 10px;
  background-color: #f9f9f9;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.edit-config-title {
  text-align: center;
  font-size: 24px;
  margin-bottom: 20px;
}

.config-form {
  display: flex;
  flex-direction: column;
}

.form-row {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.form-label {
  font-size: 18px;
  margin-bottom: 5px;
  text-align: left;
}

.form-row input {
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.save-button {
  padding: 10px 20px;
  font-size: 18px;
  border: none;
  border-radius: 5px;
  background-color: #007bff;
  color: #fff;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.save-button:hover {
  background-color: #0056b3;
}

.config-section {
  margin-top: 20px;
}

.config-section h3 {
  font-size: 20px;
  margin-bottom: 10px;
}

.password-input-wrapper input[type="password"] {
  padding-right: 40px;
}

</style>

<script>
export default {
  data() {
    return {
      config: {},
    };
  },
  created() {
    // 从后端获取原始配置数据
    this.fetchConfig();
  },
  methods: {
    fetchConfig() {
      // 从后端获取原始配置数据
      fetch("/api/config")
          .then((response) => response.json())
          .then((data) => {
            this.config = data; // 更新组件中的配置数据
          })
          .catch((error) => {
            console.error("获取配置时出错:", error);
          });
    },
    saveConfig() {
      // 将更新后的配置发送到后端保存
      fetch("/api/update_config", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(this.config),
      })
          .then((response) => response.json())
          .then((data) => {
            console.log("配置保存成功:", data);
          })
          .catch((error) => {
            console.error("保存配置时出错:", error);
          });
    },
  },
};
</script>
