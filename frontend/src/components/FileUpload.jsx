// to be deleted.


import React, { useState } from "react";
import axios from "axios";

const FileUpload = () => {
  const [files, setFiles] = useState([]);
  const [uploadMessage, setUploadMessage] = useState("");

  const handleFileChange = (event) => {
    setFiles(event.target.files);
  };

  const handleFileUpload = async () => {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i]);
    }

    try {
      const response = await axios.post("http://localhost:8080/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setUploadMessage(response.data.message);
    } catch (error) {
      console.error("Error uploading files:", error.response?.data || error.message);
      setUploadMessage("Error uploading files.");
    }
  };

  return (
    <div>
      <h2>Upload PDFs</h2>
      <input type="file" multiple onChange={handleFileChange} />
      <button onClick={handleFileUpload}>Upload</button>
      {uploadMessage && <p>{uploadMessage}</p>}
    </div>
  );
};

export default FileUpload;
