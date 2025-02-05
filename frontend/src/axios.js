// src/axios.js
import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8080', // Replace with your backend server URL
  headers: {
    'Content-Type': 'application/json',
  },
});

export default axiosInstance;
