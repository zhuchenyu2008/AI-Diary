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
      <div class="countdown">
        <h2>Time until next summary: {{ countdown }}</h2>
      </div>

      <div class="event-form">
        <h3>Record a new event</h3>
        <form @submit.prevent="submitEvent">
          <textarea v-model="eventText" placeholder="What's on your mind?"></textarea>
          <input type="file" @change="handleFileUpload" accept="image/*" ref="fileInput">
          <button type="submit">Record Event</button>
        </form>
      </div>

      <div class="timeline">
        <h3>Today's Events</h3>
        <ul>
          <li v-for="event in events" :key="event.id">
            <p>{{ event.created_at }}: {{ event.content }}</p>
            <img v-if="event.event_type === 'image'" :src="getStrapiUrl(event.file_path)" alt="Event image" style="max-width: 200px;">
          </li>
        </ul>
      </div>
    </main>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  data() {
    return {
      countdown: '',
      eventText: '',
      eventFile: null,
      events: []
    };
  },
  methods: {
    getStrapiUrl(path) {
      if (!path) return '';
      const baseUrl = 'http://localhost:5000/';
      return `${baseUrl}${path}`;
    },
    updateCountdown() {
      const now = new Date();
      const tomorrow = new Date(now);
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(0, 0, 0, 0);

      const diff = tomorrow - now;
      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      this.countdown = `${hours}h ${minutes}m ${seconds}s`;
    },
    handleFileUpload(event) {
      this.eventFile = event.target.files[0];
    },
    async submitEvent() {
      const formData = new FormData();
      if (this.eventFile) {
        formData.append('event_type', 'image');
        formData.append('file', this.eventFile);
        if (this.eventText) {
          formData.append('content', this.eventText);
        }
      } else {
        formData.append('event_type', 'text');
        formData.append('content', this.eventText);
      }

      try {
        await api.createEvent(formData);
        this.eventText = '';
        this.eventFile = null;
        this.$refs.fileInput.value = null;
        this.fetchEvents();
      } catch (error) {
        console.error('Failed to create event:', error);
      }
    },
    async fetchEvents() {
      try {
        const response = await api.getEventsTimeline();
        this.events = response.data;
      } catch (error) {
        console.error('Failed to fetch events:', error);
      }
    }
  },
  created() {
    this.updateCountdown();
    setInterval(this.updateCountdown, 1000);
    this.fetchEvents();
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
.countdown {
  text-align: center;
  margin-bottom: 2rem;
}
.event-form, .timeline {
  background: #f9f9f9;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}
textarea {
  width: 100%;
  height: 100px;
  margin-bottom: 1rem;
}
</style>
