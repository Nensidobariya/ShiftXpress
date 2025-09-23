  // Toggle sidebar on mobile
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    menuToggle.addEventListener('click', function(e) {
      e.stopPropagation();
      sidebar.classList.toggle('open');
      mainContent.classList.toggle('shifted');
    });
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
      if (window.innerWidth <= 992 && 
          !sidebar.contains(event.target) && 
          !menuToggle.contains(event.target) &&
          sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
        mainContent.classList.remove('shifted');
      }
    });
    
    // Prevent closing when clicking inside sidebar
    sidebar.addEventListener('click', function(e) {
      e.stopPropagation();
    });
    
    // Add active class to nav items on click
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
      item.addEventListener('click', function() {
        navItems.forEach(i => i.classList.remove('active'));
        this.classList.add('active');
        
        // Close sidebar on mobile after selection
        if (window.innerWidth <= 992) {
          sidebar.classList.remove('open');
          mainContent.classList.remove('shifted');
        }
      });
    });

    // Update image paths to use relative paths
    document.addEventListener('DOMContentLoaded', function() {
      // Fix image paths to use relative paths
      const images = document.querySelectorAll('img');
      images.forEach(img => {
        if (img.src.includes('C:')) {
          // Replace absolute Windows paths with relative paths
          const filename = img.src.split('\\').pop();
          img.src = '/Photos/' + filename;
        }
      });
    });