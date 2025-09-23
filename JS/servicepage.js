    // Add current year to footer
    document.getElementById('y').textContent = new Date().getFullYear();
    
    // Tab functionality
    document.addEventListener('DOMContentLoaded', function() {
      const tabs = document.querySelectorAll('.service-tab');
      const contents = document.querySelectorAll('.service-content');
      
      tabs.forEach(tab => {
        tab.addEventListener('click', function() {
          const tabId = this.getAttribute('data-tab');
          
          // Remove active class from all tabs and contents
          tabs.forEach(t => t.classList.remove('active'));
          contents.forEach(c => c.classList.remove('active'));
          
          // Add active class to clicked tab and corresponding content
          this.classList.add('active');
          document.getElementById(tabId).classList.add('active');
        });
      });
      
      // Add animation to service content when they become active
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting && entry.target.classList.contains('active')) {
            entry.target.style.opacity = 1;
            entry.target.style.transform = 'translateY(0)';
          }
        });
      }, { threshold: 0.1 });
      
      // Apply to all service contents
      contents.forEach(content => {
        content.style.opacity = 0;
        content.style.transform = 'translateY(20px)';
        content.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(content);
      });
    });