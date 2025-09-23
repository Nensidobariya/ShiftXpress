// Confirm booking button functionality - UPDATED
document.getElementById("confirmBtn").addEventListener("click", function() {
  // Validate form
  const date = document.getElementById("date").value;
  const shift = document.getElementById("shift").value;
  const vehicle = document.getElementById("vehicle").value;
  
  if (!date || !shift || !vehicle) {
    alert("Please fill in all required fields");
    return;
  }
  
  // Store booking data in localStorage
  localStorage.setItem('pickupLocation', 
    document.getElementById('pickAddress').value + ', ' + 
    document.getElementById('pickCity').value + ' - ' + 
    document.getElementById('pickZip').value
  );
  
  localStorage.setItem('destination', 
    document.getElementById('dropAddress').value + ', ' + 
    document.getElementById('dropCity').value + ' - ' + 
    document.getElementById('dropZip').value
  );
  
  localStorage.setItem('bookingDateTime', 
    new Date(date).toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    }) + ' at ' + shift + ' Shift'
  );
  
  localStorage.setItem('bookingDistance', document.getElementById('distance').textContent);
  localStorage.setItem('distanceCharge', '₹' + document.getElementById('price').textContent);
  localStorage.setItem('totalAmount', '₹' + (parseInt(document.getElementById('price').textContent) + 50));
  localStorage.setItem('selectedVehicle', vehicle);
  localStorage.setItem('purpose', document.getElementById('purpose').value);
  
  // If validation passes, redirect to user dashboard
  window.location.href = "/HTML/userdash.html";
});