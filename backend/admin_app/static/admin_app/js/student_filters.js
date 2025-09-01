const filterModal = document.getElementById('filterModal');
const closeFilterBtn = filterModal.querySelector('.close-btn');

function openFilterModal()
{
    filterModal.style.display = 'flex';
}

closeFilterBtn.onclick = () => filterModal.style.display = 'none';
window.onclick = (e) => {
  if (e.target === filterModal) filterModal.style.display = 'none';
};