<template>
  <div>


    <ul class="group-tabs" ref="groupTabs">
      <li
          v-for="(group, index) in dataGroups"
          :key="index"
          :class="{ active: selectedGroup === index }"
          @click="selectGroup(index)"
      >
        {{ group.name }}
      </li>
    </ul>
    <div class="operations-container">
      <button @click="saveData">保存</button>
      <button @click="toggleAdvancedOptions" class="advanced-button">高级选项</button>
    </div>

    <div v-if="showAdvancedOptions" class="group-edit">
      <div>
        <label>名称：</label>
        <input v-model="editedGroupName" @blur="updateGroupName" />
      </div>
      <div>
        <label>关键字覆盖：</label>
        <input v-model="editedKeywordOverride" @blur="updateKeywordOverride" />
      </div>
      <div>
        <label>RSS覆盖：</label>
        <input v-model="editedRssOverride" @blur="updateRssOverride" />
      </div>
    </div>
    <div ref="hotTable"></div>
  </div>
</template>

<script>
import Handsontable from "handsontable";
import "handsontable/dist/handsontable.full.css";
import 'handsontable/languages/zh-CN';

export default {
  data() {
    return {
      dataGroups: [],
      selectedGroup: 0,
      draggingIndex: null,
      hotInstance: null,
      editedGroupName: "",
      editedKeywordOverride: "",
      editedRssOverride: "",
      showAdvancedOptions: false,
    };
  },
  mounted() {
    this.loadData();
  },
  methods: {
    async loadData() {
      try {
        const response = await fetch("/api/config"); // Replace "/api/data" with your Flask API endpoint to fetch the data.
        const jsonData = await response.json();
        this.dataGroups = jsonData.data_dump.data_groups;
        this.loadTable();
        this.updateEditedGroupInfo();
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    },
    loadTable() {
      const selectedData = this.dataGroups[this.selectedGroup].data;
      this.hotInstance?.destroy(); // Destroy previous Handsontable instance, if exists
      this.hotInstance = new Handsontable(this.$refs.hotTable, {
        data: selectedData,
        columns: [
          { data: "release_date", type: "text", title: "添加时间" },
          { data: "series_name", type: "text", title: "剧集名称" },
          { data: "mustContain", type: "text", title: "包含关键字" },
          { data: "mustNotContain", type: "text", title: "排除关键字" },
          { data: "rename_offset", type: "text", title: "集数修正" },
          { data: "savePath", type: "text", title: "保存路径" },
          { data: "affectedFeeds", type: "text", title: "RSS订阅地址" },
          { data: "assignedCategory", type: "text", title: "种子类型" },
        ],
        colHeaders: true,
        rowHeaders: true,
        stretchH: "all",
        manualColumnResize: true, // 允许手动修改列宽
        height: 400,
        licenseKey: "non-commercial-and-evaluation",
        language: 'zh-CN', // 中文
        contextMenu: [ // 右键菜单
          "row_above",
          "row_below",
          "col_left",
          "col_right",
          "---------",
          "remove_row",
          "remove_col",
          "---------",
          "copy",
          "cut"
        ],

      });
    },
    selectGroup(index) {
      this.selectedGroup = index;
      this.updateEditedGroupInfo();
      this.loadTable();
    },
    async saveData() {
      try {
        const tableData = this.hotInstance.getData();
        const selectedDataGroup = this.dataGroups[this.selectedGroup];
        selectedDataGroup.data = tableData; // Update the data in the selected group

        // Create an array to hold the formatted data objects
        const formattedData = tableData.map((row) => {
          return {
            release_date: row[0],
            series_name: row[1],
            mustContain: row[2],
            mustNotContain: row[3],
            rename_offset: row[4],
            savePath: row[5],
            affectedFeeds: row[6],
            assignedCategory: row[7],
          };
        });

        // Update the data in the selected group
        selectedDataGroup.data = formattedData;

        const jsonData = { data_dump: { data_groups: this.dataGroups } };

        const response = await fetch("/api/save_data", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(jsonData),
        });

        if (response.ok) {
          console.log("Data saved successfully!");
        } else {
          console.error("Failed to save data:", response.statusText);
        }
      } catch (error) {
        console.error("Error saving data:", error);
      }
    },
    updateEditedGroupInfo() {
      const selectedGroup = this.dataGroups[this.selectedGroup];
      this.editedGroupName = selectedGroup.name;
      this.editedKeywordOverride = selectedGroup.keyword_override;
      this.editedRssOverride = selectedGroup.rss_override;
    },
    updateGroupName() {
      const selectedGroup = this.dataGroups[this.selectedGroup];
      selectedGroup.name = this.editedGroupName;
    },
    updateKeywordOverride() {
      const selectedGroup = this.dataGroups[this.selectedGroup];
      selectedGroup.keyword_override = this.editedKeywordOverride;
    },
    updateRssOverride() {
      const selectedGroup = this.dataGroups[this.selectedGroup];
      selectedGroup.rss_override = this.editedRssOverride;
    },
    toggleAdvancedOptions() {
      this.showAdvancedOptions = !this.showAdvancedOptions;
    },
  },
};
</script>

<style>
ul {
  display: flex;
  list-style: none;
  padding: 0;
}

.group-tabs {
  display: flex;
  list-style: none;
  padding: 0;
  margin-bottom: 20px;
}

.group-tabs li {
  cursor: pointer;
  padding: 8px 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: #f8f8f8;
  transition: background-color 0.2s ease;
  margin-right: 10px;
}

.group-tabs li.active {
  background-color: #007bff;
  color: white;
}

.group-tabs li:hover {
  background-color: #007bdd;
}

.operations-container {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.operations-container button{
  margin-right:10px;
}

.group-edit {
  display: flex;
  margin-bottom: 10px;
}

</style>
