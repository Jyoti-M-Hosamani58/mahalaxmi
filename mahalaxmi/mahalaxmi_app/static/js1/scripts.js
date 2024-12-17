// Optional JS for dropdown functionality (already handled by CSS hover)
document.querySelector('.dropbtn').addEventListener('click', function() {
  var dropdownContent = document.querySelector('.dropdown-content');
  dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
});
