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
    <div className="min-h-screen bg-gray-900">
      {/* Navigation */}
      <nav className="fixed w-full z-50 bg-gray-900/80 backdrop-blur-md border-b border-purple-500/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex-shrink-0">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-purple-600 bg-clip-text text-transparent">
                System Status
              </h1>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 pt-24 pb-12">
        <h2 className="text-3xl font-bold text-white mb-8">Recent Incidents</h2>
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div>
          </div>
        ) : error ? (
          <div className="glass-card border-red-500/30 text-red-400">
            {error}
          </div>
        ) : incidents.length === 0 ? (
          <div className="glass-card text-center">
            <p className="text-gray-400">No incidents reported</p>
          </div>
        ) : (
          <div className="space-y-6">
            {incidents.map((incident) => (
              <IncidentCard key={incident.id} incident={incident} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
