new Vue({
  el: '#app',
  data: {
    papers: [] // Initialize papers as an empty array
  },
  async mounted() {
    try {
      const response = await fetch('./output.json');
      this.papers = await response.json();
      this.papers = data.map(paper => ({ ...paper, isExpanded: false }));
    } catch (error) {
      console.error('Error fetching papers:', error);
    }
  },
  methods: {
    truncateAbstract(abstract) {
      const words = abstract.split(' ');
      if (words.length > 30) {
        return words.slice(0, 30).join(' ') + '...';
      }
      return abstract;
    },
    toggleExpand(paperId) {
      const paper = this.papers.find(paper => paper.id === paperId);
      paper.isExpanded = !paper.isExpanded;
    }
  },
  template: `
    <div id="paper-container">
      <div v-for="paper in papers" :key="paper.id" class="paper">
        <div class="title">{{ paper.title }}</div>
        <div class="author" style="font-size: smaller; margin-bottom: 0.5em;">{{ paper.authors }}</div>
        <div class="abstract" style="text-align: left;" @click="toggleExpand(paper.id)">
          {{ paper.isExpanded ? paper.abstract : truncateAbstract(paper.abstract) }}
          <span v-if="!paper.isExpanded" class="expand-indicator">...</span>
        </div>
        <div v-if="paper.isExpanded" class="url" style="margin-top: 0.5em;">
          <a :href="paper.link" target="_blank">Go to paper</a>
        </div>
      </div>
    </div>
  `
});
