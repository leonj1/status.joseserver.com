import { useEffect, useState } from 'react';
import { getRecentIncidents, generateRandomIncident, type Incident } from './api/client';
import { IncidentCard } from './components/IncidentCard';
import { RandomIncidentModal } from './components/RandomIncidentModal';
import { Toaster } from 'react-hot-toast';

function App() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [incidentMap, setIncidentMap] = useState<Map<string, number>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [generating, setGenerating] = useState(false);

  const handleGenerateIncident = async (state: string) => {
    try {
      setGenerating(true);
      const newIncident = await generateRandomIncident(state);
      setIncidents(prev => [newIncident, ...prev]);
      setIsModalOpen(false);
    } catch (err) {
      console.error('Error generating incident:', err);
      setError('Failed to generate incident. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const handleIncidentUpdate = (updatedIncident: Incident) => {
    const index = incidentMap.get(updatedIncident.id);
    if (index !== undefined) {
      setIncidents(prev => {
        const newIncidents = [...prev];
        newIncidents[index] = updatedIncident;
        return newIncidents;
      });
    }
  };

  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const data = await getRecentIncidents();
        setIncidents(data);
        // Update the index map
        const newMap = new Map();
        data.forEach((incident, index) => {
          newMap.set(incident.id, index);
        });
        setIncidentMap(newMap);
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
    <>
      <Toaster position="top-right" toastOptions={{
        duration: 4000,
        style: {
          background: '#2D3748',
          color: '#fff',
        },
        success: {
          iconTheme: {
            primary: '#68D391',
            secondary: '#2D3748',
          },
        },
        error: {
          iconTheme: {
            primary: '#F56565',
            secondary: '#2D3748',
          },
        },
      }} />
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
              <div>
                <button
                  onClick={() => setIsModalOpen(true)}
                  disabled={generating}
                  className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {generating ? 'Generating...' : 'Random Incident'}
                </button>
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
                <IncidentCard 
                  key={incident.id} 
                  incident={incident}
                  onUpdate={handleIncidentUpdate}
                  onResolve={(resolvedIncident) => {
                    setIncidents(prev => {
                      // Check if incident already exists in the list
                      const exists = prev.some(inc => inc.id === resolvedIncident.id);
                      if (exists) {
                        return prev; // Don't add if already exists
                      }
                      return [resolvedIncident, ...prev];
                    });
                  }}
                />
              ))}
            </div>
          )}
        </main>

        <RandomIncidentModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSubmit={handleGenerateIncident}
        />
      </div>
    </>
  );
}

export default App;
