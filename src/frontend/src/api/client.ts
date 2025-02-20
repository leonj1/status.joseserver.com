import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'https://status-api.joseserver.com';

export interface Incident {
  id: number;
  service: string;
  previous_state: string;
  current_state: string;
  created_at: string;
  incident: {
    title: string;
    description: string;
    components: string[];
    url: string;
  };
  history: IncidentHistory[];
}

export interface IncidentHistory {
  id: number;
  incident_id: number;
  recorded_at: string;
  service: string;
  previous_state: string;
  current_state: string;
  incident: {
    title: string;
    description: string;
    components: string[];
    url: string;
  };
}

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getRecentIncidents = async (count = 10) => {
  const response = await api.get<Incident[]>(`/incidents/recent?count=${count}`);
  return response.data;
};

export const getIncidentHistory = async (incidentId: number) => {
  const response = await api.get<IncidentHistory[]>(`/incidents/${incidentId}/history`);
  return response.data;
};

export const getHealthStatus = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const generateRandomIncident = async (state?: string) => {
  const url = state ? `/incidents/generate?state=${state}` : '/incidents/generate';
  const response = await api.get<Incident>(url);
  return response.data;
};

export const resolveIncident = async (incident: Incident) => {
  const response = await api.post<Incident>('/incidents', {
    service: incident.service,
    previous_state: incident.current_state,
    current_state: 'operational',
    incident: {
      title: `${incident.service} Service Restored`,
      description: `The ${incident.service} service has been restored to normal operation.`,
      components: incident.incident.components,
      url: incident.incident.url
    }
  });
  return response.data;
};
