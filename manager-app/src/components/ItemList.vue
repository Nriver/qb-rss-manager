<template>
  <div>
    <h2>Items List?</h2>
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
