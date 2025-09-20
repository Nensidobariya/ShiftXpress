
    function animateCounter(id, target) {
      let count = 0;
      let speed = target / 200; // adjust speed
      let counter = document.getElementById(id);
      let update = setInterval(() => {
        count += speed;
        if (count >= target) {
          count = target;
          clearInterval(update);
        }
        counter.innerText = Math.floor(count);
      }, 20);
    }

    window.onload = () => {
      animateCounter("count1", 500);
      animateCounter("count2", 200);
      animateCounter("count3", 150);
      animateCounter("count4", 50);
    }
