const filterModal = document.getElementById('filterModal');
const closeFilterBtn = filterModal.querySelector('.close-btn');
const filterForm = document.getElementById('studentFilterForm');
const ajaxUrl = document.querySelector('.scroll-container').dataset.ajaxUrl;

function openFilterModal()
{
    filterModal.style.display = 'flex';
}

closeFilterBtn.onclick = () => filterModal.style.display = 'none';
window.onclick = (e) => {
    if (e.target === filterModal) filterModal.style.display = 'none';
};

//Add Event listeners for AJAX responses when submit or reset are clicked
filterForm.addEventListener('submit', function(e) 
{
    e.preventDefault();
    const formData = new FormData(this);
    const query = new URLSearchParams(formData).toString();

    // JSON
    fetch(`${ajaxUrl}?${query}`, 
      { headers: { 'X-Requested-With': 'XMLHttpRequest' }})
      .then(response => response.json())
      .then(data => 
      {
          document.querySelector('.scroll-container').innerHTML = data.table_html;
          filterModal.style.display = 'none';
      });
});

document.getElementById('reset-btn').addEventListener('click', function(e) 
{
    console.log("Reset clicked, location before:", window.location.href);
    setTimeout(() => {
        console.log("Reset clicked, location after 1s:", window.location.href);
    }, 1000);

    e.preventDefault(); // Cancel form submit 
    e.stopPropagation();

    filterForm.reset(); //Visual form reset

    fetch(ajaxUrl, { 
        headers: { 'X-Requested-With': 'XMLHttpRequest' }})
        .then(response => response.json())
        .then(data => 
        {
            document.querySelector('.scroll-container').innerHTML = data.table_html;
            filterModal.style.display = 'none';
        });
});