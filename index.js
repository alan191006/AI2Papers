async function fetchPapers() {
  try {
    // Assuming the JSON file is in the same directory as your HTML file
    const response = await fetch('papers.json');
    const data = await response.json();

    const paperContainer = document.getElementById('paper-container');
    paperContainer.innerHTML = '';

    data.forEach(paper => {
      const paperDiv = document.createElement('div');
      paperDiv.className = 'paper';

      const titleDiv = document.createElement('div');
      titleDiv.className = 'title';
      titleDiv.textContent = paper.title;
      paperDiv.appendChild(titleDiv);

      const authorDiv = document.createElement('div');
      authorDiv.className = 'author';
      authorDiv.textContent = `Authors: ${paper.authors}`;
      paperDiv.appendChild(authorDiv);

      const abstractDiv = document.createElement('div');
      abstractDiv.className = 'abstract';
      abstractDiv.textContent = `Abstract: ${paper.abstract}`;
      paperDiv.appendChild(abstractDiv);

      const urlDiv = document.createElement('div');
      urlDiv.className = 'url';
      urlDiv.innerHTML = `<a href="${paper.link}" target="_blank">Original Paper</a>`;
      paperDiv.appendChild(urlDiv);

      paperContainer.appendChild(paperDiv);
    });
  } catch (error) {
    console.error('Error fetching papers:', error);
  }
}

// Call the function to fetch and display papers
fetchPapers();
