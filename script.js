const toggle = document.querySelector(".toggle");
const body = document.body;
const typeTarget = document.querySelector(".type");
const cursor = document.querySelector(".cursor");
const viewProjectsBtn = document.getElementById("viewProjectsBtn");
const contactBtn = document.getElementById("contactBtn");
const contactForm = document.getElementById("contactForm");
const formStatus = document.getElementById("formStatus");

const words = [
  "Student",
  "Tech Explorer",
  "Data Analytics Learner",
  "Finance Enthusiast"
];

let wordIndex = 0;
let charIndex = 0;
let deleting = false;

function typeEffect() {
  const currentWord = words[wordIndex];
  if (!deleting) {
    typeTarget.textContent = currentWord.slice(0, charIndex + 1);
    charIndex += 1;
    if (charIndex === currentWord.length) {
      deleting = true;
      setTimeout(typeEffect, 1000);
      return;
    }
  } else {
    typeTarget.textContent = currentWord.slice(0, charIndex - 1);
    charIndex -= 1;
    if (charIndex === 0) {
      deleting = false;
      wordIndex = (wordIndex + 1) % words.length;
    }
  }
  setTimeout(typeEffect, deleting ? 60 : 100);
}

toggle.addEventListener("click", () => {
  body.classList.toggle("light");
  toggle.textContent = body.classList.contains("light") ? "☀️" : "🌙";
});

document.addEventListener("mousemove", (e) => {
  cursor.style.left = `${e.clientX}px`;
  cursor.style.top = `${e.clientY}px`;
});

viewProjectsBtn.addEventListener("click", () => {
  document.getElementById("projects").scrollIntoView({ behavior: "smooth" });
});

contactBtn.addEventListener("click", () => {
  document.getElementById("contact").scrollIntoView({ behavior: "smooth" });
});

const skillBars = document.querySelectorAll(".skills span i");
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      const width = entry.target.getAttribute("data-w");
      entry.target.style.width = width;
    }
  });
});
skillBars.forEach((bar) => observer.observe(bar));

contactForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  formStatus.textContent = "Sending...";
  formStatus.style.color = "var(--cyan)";

  const payload = {
    name: document.getElementById("name").value.trim(),
    email: document.getElementById("email").value.trim(),
    message: document.getElementById("message").value.trim()
  };

  try {
    const response = await fetch("/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Unable to send message");
    }

    formStatus.textContent = "Message sent successfully.";
    formStatus.style.color = "var(--pink)";
    contactForm.reset();
  } catch (error) {
    formStatus.textContent = error.message;
    formStatus.style.color = "#ff6b6b";
  }
});

// Animated matrix-like background.
const canvas = document.getElementById("matrix");
const ctx = canvas.getContext("2d");
const letters = "01ABCDEFGHIJKLMNOPQRSTUVWXYZ#$%&";
let cols = 0;
let drops = [];

function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  cols = Math.floor(canvas.width / 16);
  drops = Array(cols).fill(1);
}

function drawMatrix() {
  ctx.fillStyle = "rgba(10, 10, 10, 0.08)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#00cfff";
  ctx.font = "14px monospace";

  for (let i = 0; i < drops.length; i += 1) {
    const text = letters[Math.floor(Math.random() * letters.length)];
    ctx.fillText(text, i * 16, drops[i] * 16);
    if (drops[i] * 16 > canvas.height && Math.random() > 0.975) {
      drops[i] = 0;
    }
    drops[i] += 1;
  }
}

window.addEventListener("resize", resizeCanvas);
resizeCanvas();
setInterval(drawMatrix, 45);
typeEffect();
