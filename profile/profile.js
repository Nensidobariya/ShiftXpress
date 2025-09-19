let currentStep = 1;
let interval;

function startUpdate() {
  document.getElementById("statusText").innerText = "In Progress...";
  interval = setInterval(updateStep, 2000);
}

function updateStep() {
  if (currentStep > 4) {
    clearInterval(interval);
    document.getElementById("statusText").innerText = "Completed ✅";
    return;
  }
  document.getElementById("step" + currentStep).classList.add("active");
  currentStep++;
}
