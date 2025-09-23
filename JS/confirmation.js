 // Function to fetch data from localStorage
  function getBookingData() {
    // Get customer data from signup
    const customerData = {
      name: localStorage.getItem('customerName') || 'Customer Name',
      phone: localStorage.getItem('customerPhone') || 'Phone Number',
      email: localStorage.getItem('customerEmail') || 'Email Address'
    };
    
    // Get booking data from booking page
    const bookingData = {
      pickupLocation: localStorage.getItem('pickupLocation') || 'Pickup location not specified',
      destination: localStorage.getItem('destination') || 'Destination not specified',
      dateTime: localStorage.getItem('bookingDateTime') || 'Date and time not specified',
      distance: localStorage.getItem('bookingDistance') || 'Distance not calculated',
      distanceCharge: localStorage.getItem('distanceCharge') || '₹0',
      totalAmount: localStorage.getItem('totalAmount') || '₹0',
      vehicle: localStorage.getItem('selectedVehicle') || 'Vehicle not selected',
      purpose: localStorage.getItem('purpose') || 'Not specified'
    };
    
    // Get driver data (simulated - would normally come from admin assignment)
    const driverData = {
      name: localStorage.getItem('assignedDriver') || 'Driver to be assigned by admin',
      rating: localStorage.getItem('driverRating') || '',
      vehicle: localStorage.getItem('assignedVehicle') || bookingData.vehicle,
      contact: localStorage.getItem('driverContact') || 'Will be provided after assignment'
    };
    
    return { customerData, bookingData, driverData };
  }
  
  // Function to update the page with fetched data
  function updatePageWithData() {
    const { customerData, bookingData, driverData } = getBookingData();
    
    // Update customer details
    document.getElementById('customerName').textContent = customerData.name;
    document.getElementById('customerPhone').textContent = customerData.phone;
    document.getElementById('customerEmail').textContent = customerData.email;
    
    // Update trip details
    document.getElementById('pickupLocation').textContent = bookingData.pickupLocation;
    document.getElementById('destination').textContent = bookingData.destination;
    document.getElementById('dateTime').textContent = bookingData.dateTime;
    document.getElementById('distance').textContent = bookingData.distance;
    
    // Update price details
    document.getElementById('distanceCharge').textContent = bookingData.distanceCharge;
    document.getElementById('totalAmount').textContent = bookingData.totalAmount;
    
    // Update driver details
    document.getElementById('driverName').textContent = driverData.name;
    document.getElementById('driverRating').textContent = driverData.rating;
    document.getElementById('vehicleInfo').textContent = driverData.vehicle;
    document.getElementById('driverContact').textContent = driverData.contact;
    
    // Update progress bar based on driver assignment
    const progressFill = document.getElementById('progressFill');
    if (driverData.name !== 'Driver to be assigned by admin') {
      progressFill.style.width = '75%';
      document.querySelectorAll('.step')[1].classList.add('active');
    }
  }
  
  // Function to simulate admin assigning a driver (for demonstration)
  function simulateDriverAssignment() {
    // In a real application, this would be done by the admin
    const assignedDriver = {
      name: 'Michael Johnson',
      rating: '★ 4.9 (128 ratings)',
      vehicle: localStorage.getItem('selectedVehicle') + ' • White • GJ-01-AB-1234',
      contact: '+1 (555) 987-6543'
    };
    
    // Save to localStorage (simulating database update)
    localStorage.setItem('assignedDriver', assignedDriver.name);
    localStorage.setItem('driverRating', assignedDriver.rating);
    localStorage.setItem('assignedVehicle', assignedDriver.vehicle);
    localStorage.setItem('driverContact', assignedDriver.contact);
    
    // Update the page
    updatePageWithData();
  }
  
  // Initialize the page when it loads
  document.addEventListener('DOMContentLoaded', function() {
    // Check if we have booking data
    const hasBookingData = localStorage.getItem('pickupLocation') && 
                          localStorage.getItem('destination');
    
    if (!hasBookingData) {
      // If no booking data exists, set some default values for demo
      if (!localStorage.getItem('customerName')) {
        localStorage.setItem('customerName', 'Please complete signup first');
        localStorage.setItem('customerPhone', 'N/A');
        localStorage.setItem('customerEmail', 'N/A');
      }
      
      if (!localStorage.getItem('pickupLocation')) {
        localStorage.setItem('pickupLocation', 'Please complete booking first');
        localStorage.setItem('destination', 'Please complete booking first');
        localStorage.setItem('bookingDateTime', 'N/A');
        localStorage.setItem('bookingDistance', 'N/A');
        localStorage.setItem('distanceCharge', '₹0');
        localStorage.setItem('totalAmount', '₹0');
      }
    }
    
    // Update the page with the data
    updatePageWithData();
    
    // Only simulate driver assignment if we have real booking data
    if (hasBookingData) {
      setTimeout(simulateDriverAssignment, 3000);
    }
  });