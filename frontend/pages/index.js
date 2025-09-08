import { useState } from "react";
import axios from "axios";
import { Container, Typography, Button, TextField, Box } from "@mui/material";

export default function Home() {
  const [file, setFile] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [summary, setSummary] = useState("");

  const handleSubmit = async () => {
    if (!file) return alert("Upload a file first!");
    const formData = new FormData();
    formData.append("file", file);
    formData.append("prompt", prompt);
    try {
      const res = await axios.post("http://localhost:8000/summarize", formData);
      setSummary(res.data.summary);
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  return (
    <Container>
      <Typography variant="h4" gutterBottom>Multi-Modal Summarizer</Typography>
      <Box my={2}>
        <input type="file" onChange={e => setFile(e.target.files[0])} />
      </Box>
      <TextField
        fullWidth
        label="Custom Prompt"
        value={prompt}
        onChange={e => setPrompt(e.target.value)}
        margin="normal"
      />
      <Button variant="contained" color="primary" onClick={handleSubmit}>
        Summarize
      </Button>
      {summary && (
        <Box mt={4}>
          <Typography variant="h6">Summary:</Typography>
          <Typography>{summary}</Typography>
        </Box>
      )}
    </Container>
  );
}
