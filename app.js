// Aesthetic Picture Generator - Combined Frontend + Backend
// Run: node app.js
// Install: npm install express jimp body-parser multer

const express = require("express");
const bodyParser = require("body-parser");
const multer = require("multer");
const Jimp = require("jimp");
const app = express();
const port = 3000;

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static("public"));

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// ---------- FRONTEND (HTML + CSS + JS) ----------
const htmlPage = `
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Aesthetic Picture Generator</title>
<style>
  body {
    font-family: "Poppins", sans-serif;
    background: linear-gradient(120deg, #a6c0fe, #f68084);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 0;
  }
  h1 {
    color: white;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
  }
  .container {
    background: white;
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    text-align: center;
  }
  input, select, button {
    margin: 10px;
    padding: 10px;
    border-radius: 8px;
    border: none;
    font-size: 16px;
  }
  button {
    background-color: #6a11cb;
    color: white;
    cursor: pointer;
    transition: 0.3s;
  }
  button:hover {
    background-color: #2575fc;
  }
  img {
    margin-top: 20px;
    max-width: 90%;
    border-radius: 10px;
  }
</style>
</head>
<body>
  <h1>✨ Aesthetic Picture Generator ✨</h1>
  <div class="container">
    <form id="uploadForm" enctype="multipart/form-data">
      <input type="file" name="image" id="imageInput" accept="image/*" required>
      <select name="filter" id="filter">
        <option value="vintage">Vintage</option>
        <option value="warm">Warm Tone</option>
        <option value="cool">Cool Tone</option>
        <option value="grayscale">Grayscale</option>
        <option value="bright">Brighten</option>
        <option value="blur">Soft Blur</option>
      </select>
      <button type="submit">Generate Aesthetic Image 🎨</button>
    </form>
    <img id="outputImage" src="" alt="">
  </div>

  <script>
    const form = document.getElementById('uploadForm');
    const outputImage = document.getElementById('outputImage');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(form);
      const response = await fetch('/process', { method: 'POST', body: formData });
      const blob = await response.blob();
      outputImage.src = URL.createObjectURL(blob);
    });
  </script>
</body>
</html>
`;

// Serve HTML Page
app.get("/", (req, res) => {
  res.send(htmlPage);
});

// ---------- BACKEND (JIMP Image Processing) ----------
app.post("/process", upload.single("image"), async (req, res) => {
  try {
    const filter = req.body.filter;
    const image = await Jimp.read(req.file.buffer);

    // Apply filter
    switch (filter) {
      case "vintage":
        image.color([{ apply: "desaturate", params: [20] }, { apply: "darken", params: [10] }]);
        image.contrast(0.3);
        break;
      case "warm":
        image.color([{ apply: "red", params: [20] }, { apply: "green", params: [10] }]);
        break;
      case "cool":
        image.color([{ apply: "blue", params: [30] }, { apply: "green", params: [-10] }]);
        break;
      case "grayscale":
        image.grayscale();
        break;
      case "bright":
        image.brightness(0.2).contrast(0.2);
        break;
      case "blur":
        image.blur(5);
        break;
      default:
        break;
    }

    const buffer = await image.getBufferAsync(Jimp.MIME_JPEG);
    res.set("Content-Type", "image/jpeg");
    res.send(buffer);

  } catch (err) {
    console.error(err);
    res.status(500).send("Error processing image.");
  }
});

// Start server
app.listen(port, () => console.log(\`🌸 Aesthetic Picture Generator running at http://localhost:\${port}\`));
