new Vue({
  el: '#app',
  data: {
    papers: [] // Initialize papers as an empty array
  },
  async mounted() {
    try {
      const response = await fetch('./output.json');
      const data = await response.json();

      // Initialize isExpanded property for each paper
      this.papers = data.map(paper => ({ ...paper, isExpanded: false }));
    } catch (error) {
      console.error('Error fetching papers:', error);
    }
  },
  methods: {
    toggleExpand(paperId) {
      // Toggle the isExpanded property for the clicked paper
      const clickedPaper = this.papers.find(paper => paper.id === paperId);
      clickedPaper.isExpanded = !clickedPaper.isExpanded;

      // Close other expanded papers
      this.papers.forEach(paper => {
        if (paper.id !== paperId) {
          paper.isExpanded = false;
        }
      });
    }
  },
  template: `
    <div id="paper-container">
      <div v-for="paper in papers" :key="paper.id" class="paper" @click="toggleExpand(paper.id)">
        <div class="title">{{ paper.title }}</div>
        <div v-if="paper.isExpanded" class="expanded-content">
          <div class="author">{{ paper.authors }}</div>
          <div class="abstract">{{ paper.abstract }}</div>
          <div class="url">
            <a :href="paper.link" target="_blank">Go to paper</a>
          </div>
        </div>
      </div>
    </div>
  `
});
