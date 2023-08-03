<template>
  <div>
    <ul>
      <li v-for="item in items" :key="item.id">{{ item.name }}</li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      items: [],
    };
  },
  mounted() {
    this.fetchItems();
  },
  methods: {
    fetchItems() {
      fetch('/api/items')
          .then((response) => response.json())
          .then((data) => {
            this.items = data;
          });
    },
  },
};
</script>
