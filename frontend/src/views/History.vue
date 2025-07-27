<template>
  <div class="container">
    <header>
      <h1>AI Diary</h1>
      <nav>
        <router-link to="/">Home</router-link> |
        <router-link to="/history">History</router-link>
      </nav>
    </header>

    <main>
      <h2>History</h2>
      <div class="date-picker">
        <input type="date" v-model="selectedDate" @change="fetchSummaryByDate">
      </div>

      <div v-if="selectedSummary" class="summary-display">
        <h3>Summary for {{ selectedSummary.summary_date }}</h3>
        <p>{{ selectedSummary.content }}</p>
      </div>

      <div class="summaries-list">
        <h3>All Summaries</h3>
        <ul>
          <li v-for="summary in summaries" :key="summary.id">
            <a href="#" @click.prevent="selectSummary(summary)">{{ summary.summary_date }}</a>
          </li>
        </ul>
        <button @click="loadMore" :disabled="!hasMore">Load More</button>
      </div>
    </main>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  data() {
    return {
      selectedDate: null,
      selectedSummary: null,
      summaries: [],
      page: 1,
      hasMore: true
    };
  },
  methods: {
    async fetchSummaries() {
      try {
        const response = await api.getSummaries(this.page);
        if (response.data.length > 0) {
          this.summaries = [...this.summaries, ...response.data];
        } else {
          this.hasMore = false;
        }
      } catch (error) {
        console.error('Failed to fetch summaries:', error);
      }
    },
    async fetchSummaryByDate() {
      if (!this.selectedDate) return;
      try {
        const response = await api.getSummaryByDate(this.selectedDate);
        this.selectedSummary = response.data;
      } catch (error) {
        this.selectedSummary = { summary_date: this.selectedDate, content: 'No summary found for this date.' };
        console.error('Failed to fetch summary by date:', error);
      }
    },
    selectSummary(summary) {
      this.selectedSummary = summary;
    },
    loadMore() {
      this.page++;
      this.fetchSummaries();
    }
  },
  created() {
    this.fetchSummaries();
  }
};
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.date-picker, .summary-display, .summaries-list {
  margin-bottom: 2rem;
}
</style>
