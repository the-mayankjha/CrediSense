import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const api = {
  uploadDocument: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await axios.post(`${API_BASE_URL}/ingest/document`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error("Error uploading document:", error);
      throw error;
    }
  },

  researchCompany: async (companyName: string) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/research/company/${encodeURIComponent(companyName)}`);
      return response.data;
    } catch (error) {
      console.error("Error researching company:", error);
      throw error;
    }
  },

  generateCAM: async (payload: {
    application_id: string;
    company_data: any;
    research_data: any;
    primary_insights: string;
  }) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/engine/generate-cam`, payload);
      return response.data;
    } catch (error) {
      console.error("Error generating CAM:", error);
      throw error;
    }
  }
};
