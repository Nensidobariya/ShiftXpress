    // Multi-step form functionality
    const steps = document.querySelectorAll('.form-step');
    const progressSteps = document.querySelectorAll('.progress-step');
    let currentStep = 1;

    // Function to show a specific step
    function showStep(stepNumber) {
      steps.forEach(step => step.classList.remove('active'));
      document.getElementById(`step${stepNumber}`).classList.add('active');
      currentStep = stepNumber;
      
      // Update progress indicator
      progressSteps.forEach(step => step.classList.remove('active'));
      document.querySelector(`.progress-step[data-step="${stepNumber}"]`).classList.add('active');
      
      // Scroll to top of form when changing steps
      document.querySelector('.booking-form').scrollTop = 0;
    }

    // Next button functionality
    document.querySelectorAll('.next-btn').forEach(button => {
      button.addEventListener('click', function() {
        const nextStep = parseInt(this.getAttribute('data-next'));
        
        // Validate current step before proceeding
        if (validateStep(currentStep)) {
          // Update summary if moving to step 3
          if (nextStep === 3) {
            updateSummary();
            calculateEstimate();
          }
          
          showStep(nextStep);
        }
      });
    });

    // Previous button functionality
    document.querySelectorAll('.prev-btn').forEach(button => {
      button.addEventListener('click', function() {
        const prevStep = parseInt(this.getAttribute('data-prev'));
        showStep(prevStep);
      });
    });

    // Validate step function
    function validateStep(step) {
      const inputs = document.querySelectorAll(`#step${step} [required]`);
      let isValid = true;
      
      inputs.forEach(input => {
        if (!input.value) {
          input.style.borderColor = 'red';
          isValid = false;
        } else {
          input.style.borderColor = '#ddd';
        }
      });
      
      return isValid;
    }

    // Update summary in step 3
    function updateSummary() {
      document.getElementById('summaryPickCity').textContent = document.getElementById('pickCity').value;
      document.getElementById('summaryPickZip').textContent = document.getElementById('pickZip').value;
      document.getElementById('summaryPickAddress').textContent = document.getElementById('pickAddress').value;
      document.getElementById('summaryDropCity').textContent = document.getElementById('dropCity').value;
      document.getElementById('summaryDropZip').textContent = document.getElementById('dropZip').value;
      document.getElementById('summaryDropAddress').textContent = document.getElementById('dropAddress').value;
    }

    // Calculate estimate
    function calculateEstimate() {
      const pickupZip = parseInt(document.getElementById('pickZip').value);
      const dropZip = parseInt(document.getElementById('dropZip').value);
      
      const distance = Math.abs(pickupZip - dropZip) / 2;
      const baseCharge = 500;
      const perKmCharge = 15;
      const price = baseCharge + distance * perKmCharge;

      document.getElementById("distance").textContent = distance.toFixed(1);
      document.getElementById("price").textContent = price.toFixed(0);
    }

    // Vehicle availability logic
    const unavailableVehicle = "Tempo"; // Set unavailable vehicle
    const vehicleSelect = document.getElementById("vehicle");
    const messageBox = document.getElementById("vehicleMessage");

    vehicleSelect.addEventListener("change", function () {
      const selected = vehicleSelect.value;

      if (selected === unavailableVehicle) {
        // Remove the unavailable option
        for (let i = 0; i < vehicleSelect.options.length; i++) {
          if (vehicleSelect.options[i].value === unavailableVehicle) {
            vehicleSelect.remove(i);
            break;
          }
        }

        // Reset selection
        vehicleSelect.value = "";

        // Show message
        const availableVehicles = Array.from(vehicleSelect.options)
          .filter(opt => opt.value !== "")
          .map(opt => opt.value)
          .join(", ");

        messageBox.innerText = `${unavailableVehicle} is currently unavailable. Please choose from: ${availableVehicles}.`;
      } else {
        messageBox.innerText = "";
      }
    });

    // Confirm booking button functionality
    document.getElementById("confirmBtn").addEventListener("click", function() {
      // Validate form
      const date = document.getElementById("date").value;
      const shift = document.getElementById("shift").value;
      const vehicle = document.getElementById("vehicle").value;
      
      if (!date || !shift || !vehicle) {
        alert("Please fill in all required fields");
        return;
      }
      
      // If validation passes, redirect to user dashboard
      window.location.href = "/HTML/confirmation.html";
    });

    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById("date").setAttribute('min', today);
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
  window.location.href = "/HTML/confirmation.html";
});