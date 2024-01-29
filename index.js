new Vue({
  el: '#paper-container',
  data: {
    papers: [] // Initialize papers as an empty array
  },
  async mounted() {
    try {
      const response = await fetch('./output.json');
      const data = await response.json();

      // Initialize isExpanded property for each paper using array index
      this.papers = data.map((paper, index) => ({ ...paper, isExpanded: false, index }));
    } catch (error) {
      console.error('Error fetching papers:', error);
    }
  },
  methods: {
    toggleExpand(paperIndex) {
      // Toggle the isExpanded property for the clicked paper
      const clickedPaper = this.papers[paperIndex];
      clickedPaper.isExpanded = !clickedPaper.isExpanded;

      // Close other expanded papers
      this.papers.forEach((paper, index) => {
        if (index !== paperIndex) {
          paper.isExpanded = false;
        }
      });
    }
  },
  template: `
    <div id="paper-container">
      <div v-for="(paper, index) in papers" :key="index" class="paper" @click="toggleExpand(index)">
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
