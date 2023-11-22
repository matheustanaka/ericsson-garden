import React, { useState } from 'react';
import './style.css'

function Dashboard() {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/uploader', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      console.log(data);

      if (response.ok) {
        alert('File uploaded successfully');
      } else {
        alert('File upload failed');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('There was an error when uploading the file');
    }
  };

  return (
    <form onSubmit={handleSubmit} className='form-uploader'>
      <div className="form-content">
        <h1 className='form-title'>Drop Files Here</h1>
        <input type="file" onChange={handleFileChange} />
        <button type="submit" className='upload'>Upload</button>
      </div>
    </form>
  );
}

export default Dashboard;

