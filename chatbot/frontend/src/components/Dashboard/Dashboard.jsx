import { useState } from 'react';
import axios from 'axios';
import './style.css';

export default function Dashboard () {
  const [inputText, setInputText] = useState("");
  const [questions, setQuestions] = useState([]);   
  const [summaries, setSummaries] = useState([]); 


  const fetchSummary = async (event) => {
    event.preventDefault();
    try {
      const { data } = await axios.post('http://localhost:5000/chatbot', { text: inputText });
      console.log("Data received from API:", data);

      if (data.answer) {
        setQuestions(prevQuestions => [...prevQuestions, inputText]); 
        setSummaries(prevSummaries => [...prevSummaries, data.answer]); 
      } else {
        console.log("No answer in the response");
      }
    } catch (error) {
      console.error("Error fetching summary:", error);
    }
  };

  const handleInputChange = (event) => {
    setInputText(event.target.value);
  };

  return (
    <div className='dashboard'>
      <h1>Summary Word (.docx)</h1>
      <div className="analyze-content">
        {questions.length > 0 ? (
          questions.map((question, index) => (
            <div key={index}>
              <p><strong>Question:</strong> {question}</p>
              <p><strong>Answer:</strong> {summaries[index]}</p>
            </div>
          ))
        ) : (
          <p>No content to display</p>
        )}
      </div>
      <form className='form-data' onSubmit={fetchSummary}>
        <input 
          type='text' 
          className='input-data' 
          placeholder='Enter text' 
          value={inputText} 
          onChange={handleInputChange}
        />
        <button className='btn-analyzer' type='submit'>Send</button>
      </form>
    </div>
  );
}

