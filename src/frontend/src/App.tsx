import { useEffect, useState } from 'react';
import { getRecentIncidents, type Incident } from './api/client';
import { IncidentCard } from './components/IncidentCard';

function App() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const data = await getRecentIncidents();
        setIncidents(data);
        setError(null);
      } catch (err) {
        setError('Failed to load incidents. Please try again later.');
        console.error('Error fetching incidents:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchIncidents();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-900">System Status</h1>
          <p className="mt-1 text-sm text-gray-500">
            Latest incidents and system updates
          </p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            {error}
          </div>
        ) : incidents.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-6 text-center">
            <p className="text-gray-500">No incidents reported</p>
          </div>
        ) : (
          <div className="space-y-6">
            {incidents.map((incident) => (
              <IncidentCard key={incident.id} incident={incident} />
            ))}
          </div>
        )}
      </main>

      <footer className="border-t border-gray-200 bg-white mt-12">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <p className="text-center text-sm text-gray-500">
            Status page powered by FastAPI and React
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
