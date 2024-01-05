async function fetchPapers() {
  try {
    const response = await fetch('output.json');
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
      authorDiv.style.fontSize = 'smaller';
      // Remove the "Authors: " prefix
      authorDiv.textContent = paper.authors;
      paperDiv.appendChild(authorDiv);
    
      // Add a margin between author and abstract
      authorDiv.style.marginBottom = '0.5em';
    
      const abstractDiv = document.createElement('div');
      abstractDiv.className = 'abstract';
      // Set text alignment to justify
      abstractDiv.style.textAlign = 'justify';
      // Remove the "Abstract: " prefix
      abstractDiv.textContent = paper.abstract;
      paperDiv.appendChild(abstractDiv);
    
      const urlDiv = document.createElement('div');
      urlDiv.className = 'url';
      // Display "URL: " and align to the left
      urlDiv.style.textAlign = 'left'; // Fix: Set text alignment for urlDiv
      urlDiv.innerHTML = `URL: <a href="${paper.link}" target="_blank">${paper.link}</a>`;
      urlDiv.style.marginTop = '0.5em';

      paperDiv.appendChild(urlDiv);
    
      paperContainer.appendChild(paperDiv);
    });
    
  } catch (error) {
    console.error('Error fetching papers:', error);
  }
}

// Call the function to fetch and display papers
fetchPapers();
