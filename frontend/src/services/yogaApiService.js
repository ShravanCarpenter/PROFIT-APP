import axios from 'axios';

const API_URL = 'http://localhost:5000'; 

const yogaApiService = {
    analyzeImage: (file) => {
        const formData = new FormData();
        formData.append('image', file);

        return axios.post(`${API_URL}/predict`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        }).then(res => res.data);
    }
};

export default yogaApiService;
