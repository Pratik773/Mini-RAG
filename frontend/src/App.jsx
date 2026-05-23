import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  // Upload PDF
  const uploadFile = async () => {
    if (!file) {
      alert("Please select a PDF file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/upload",
        formData,
      );

      alert("PDF uploaded successfully");

      console.log(response.data);
    } catch (error) {
      console.log(error);

      alert("Upload failed");
    }
  };

  // Ask Question
  const askQuestion = async () => {
    if (!question) {
      alert("Please enter question");
      return;
    }

    try {
      const response = await axios.post("http://127.0.0.1:8000/ask", {
        question: question,
      });

      setAnswer(response.data.answer);
    } catch (error) {
      console.log(error);

      alert("Question request failed");
    }
  };

  return (
    <div class="a">
      <div className="container">
        <h1>Mini RAG AI</h1>

        {/* Upload Section */}
        <div className="card">
          <h2>Upload PDF</h2>

          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files[0])}
          />

          <button onClick={uploadFile}>Upload</button>
        </div>

        {/* Question Section */}
        <div className="card">
          <h2>Ask Question</h2>

          <input
            type="text"
            placeholder="Ask something from PDF..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />

          <button onClick={askQuestion}>Ask</button>
        </div>

        {/* Answer Section */}
        <div className="card">
          <h2>AI Answer</h2>

          <p>{answer}</p>
        </div>
      </div>
    </div>
  );
}

export default App;
