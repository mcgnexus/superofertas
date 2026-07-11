import axios, { type AxiosInstance } from 'axios';
import type { OfertaFilters } from '../types';

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const ofertasApi = {
  getOfertas: async (filters?: OfertaFilters) => {
    const params = new URLSearchParams();
    if (filters?.supermercado) params.append('supermercado', filters.supermercado);
    if (filters?.categoria) params.append('categoria', filters.categoria);
    if (filters?.precio_max) params.append('precio_max', filters.precio_max.toString());
    
    const response = await apiClient.get(`/api/ofertas?${params.toString()}`);
    return response.data;
  },

  generarMenu: async (data: {
    presupuesto: number;
    num_personas: number;
    supermercados: string[];
    restricciones: string[];
  }) => {
    const response = await apiClient.post('/api/menu/generar', data);
    return response.data;
  },

  getHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  scrapeMercadona: async () => {
    const response = await apiClient.post('/api/scrape/mercadona');
    return response.data;
  },

  scrapeCarrefour: async () => {
    const response = await apiClient.post('/api/scrape/carrefour');
    return response.data;
  },

  scrapeDia: async () => {
    const response = await apiClient.post('/api/scrape/dia');
    return response.data;
  },

  scrapeAll: async () => {
    const response = await apiClient.post('/api/scrape/all');
    return response.data;
  }
};