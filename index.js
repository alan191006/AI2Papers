window.addEventListener('DOMContentLoaded', () => {
  fetchPapers();
});

async function fetchPapers() {
  try {
      // Assuming the JSON file is in the same directory as your HTML file
      const response = await fetch('papers.json');
      const data = await response.json();

      const paperContainer = document.getElementById('paper-container');
      paperContainer.innerHTML = '';

      data.paper.forEach(paper => {
          const paperDiv = document.createElement('div');
          paperDiv.className = 'paper';

          const titleDiv = document.createElement('div');
          titleDiv.className = 'title';
          titleDiv.textContent = paper.title;
          paperDiv.appendChild(titleDiv);

          const authorDiv = document.createElement('div');
          authorDiv.className = 'author';
          authorDiv.textContent = `Author: ${paper.author}`;
          paperDiv.appendChild(authorDiv);

          const abstractDiv = document.createElement('div');
          abstractDiv.className = 'abstract';
          abstractDiv.textContent = `Abstract: ${paper.abstract}`;
          paperDiv.appendChild(abstractDiv);

          const urlDiv = document.createElement('div');
          urlDiv.className = 'url';
          urlDiv.innerHTML = `<a href="${paper.url}" target="_blank">Original Paper</a>`;
          paperDiv.appendChild(urlDiv);

          paperContainer.appendChild(paperDiv);
      });
  } catch (error) {
      console.error('Error fetching papers:', error);
  }
}
