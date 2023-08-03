<template>
  <div class="config-editor">
    <h2 class="config-editor__title">直接编辑配置文件</h2>
    <p class="config-editor__note">请注意备份好配置，改错了可能会导致无法运行</p>
    <textarea
        class="config-editor__textarea"
        v-model="configContent"
        rows="10"
        cols="50"
        placeholder="配置内容..."
    ></textarea>
    <button class="config-editor__save-btn" @click="saveConfig">Save</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      configContent: '',
    };
  },
  mounted() {
    this.fetchConfig();
  },
  methods: {
    fetchConfig() {
      fetch('/api/config')
          .then((response) => response.json())
          .then((data) => {
            this.configContent = JSON.stringify(data, null, 2);
          });
    },
    saveConfig() {
      const newConfigData = JSON.parse(this.configContent);
      fetch('/api/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newConfigData),
      })
          .then((response) => response.json())
          .then((data) => {
            console.log('Config saved successfully!');
            console.log(data);
          });
    },
  },
};
</script>

<style>
.config-editor {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.config-editor__title {
  font-size: 24px;
  margin-bottom: 10px;
}

.config-editor__note {
  color: red; /* Set the color to red */
  font-size: 14px;
  margin-bottom: 10px;
}

.config-editor__textarea {
  width: 100%;
  height: 300px;
  resize: none;
  border: 1px solid #ccc;
  padding: 10px;
  font-family: 'Arial', sans-serif;
}

.config-editor__save-btn {
  margin-top: 10px;
  padding: 10px 20px;
  background-color: #007bff;
  color: #fff;
  border: none;
  cursor: pointer;
  font-size: 16px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.config-editor__save-btn:hover {
  background-color: #0056b3;
}
</style>
