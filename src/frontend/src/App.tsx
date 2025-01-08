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
    <div className="min-h-screen bg-gray-900 bg-blur-pattern">
      {/* Navigation */}
      <nav className="fixed w-full z-50 bg-gray-900/80 backdrop-blur-md border-b border-purple-500/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex-shrink-0">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-purple-600 bg-clip-text text-transparent">
                System Status
              </h1>
            </div>
            <div className="hidden md:flex space-x-8">
              <a href="#dashboard" className="nav-link">Dashboard</a>
              <a href="#history" className="nav-link">History</a>
              <a href="#services" className="nav-link">Services</a>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <h2 className="text-5xl font-bold mb-6 bg-gradient-to-r from-purple-400 via-purple-600 to-purple-800 bg-clip-text text-transparent">
            Real-Time System Status
          </h2>
          <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
            Monitor our service performance and incident updates in real-time with our beautiful status dashboard
          </p>
          <div className="flex gap-4 justify-center mb-12">
            <button className="btn-primary">View Dashboard</button>
            <button className="btn-secondary">Subscribe to Updates</button>
          </div>
        </div>
      </section>

      {/* Status Overview */}
      <section className="py-16 px-4 bg-gray-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <div className="glass-card text-center">
              <div className="text-purple-400 text-4xl font-bold mb-2">99.9%</div>
              <div className="text-gray-400">Uptime</div>
            </div>
            <div className="glass-card text-center">
              <div className="text-purple-400 text-4xl font-bold mb-2">
                {incidents.length}
              </div>
              <div className="text-gray-400">Active Incidents</div>
            </div>
            <div className="glass-card text-center">
              <div className="text-purple-400 text-4xl font-bold mb-2">24/7</div>
              <div className="text-gray-400">Monitoring</div>
            </div>
          </div>
        </div>
      </section>

      {/* Incidents Section */}
      <main className="max-w-7xl mx-auto px-4 py-16">
        <h3 className="text-3xl font-bold text-white mb-8">Recent Incidents</h3>
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

      {/* Footer */}
      <footer className="border-t border-purple-500/20 bg-gray-900/80 backdrop-blur-md mt-12">
        <div className="max-w-7xl mx-auto px-4 py-12">
          <div className="grid md:grid-cols-3 gap-8 text-center md:text-left">
            <div>
              <h4 className="text-lg font-semibold text-purple-400 mb-4">About</h4>
              <p className="text-gray-400">
                Status page powered by FastAPI and React with real-time monitoring
              </p>
            </div>
            <div>
              <h4 className="text-lg font-semibold text-purple-400 mb-4">Quick Links</h4>
              <div className="space-y-2">
                <a href="#" className="block text-gray-400 hover:text-purple-400 transition-colors">Documentation</a>
                <a href="#" className="block text-gray-400 hover:text-purple-400 transition-colors">API Status</a>
                <a href="#" className="block text-gray-400 hover:text-purple-400 transition-colors">Support</a>
              </div>
            </div>
            <div>
              <h4 className="text-lg font-semibold text-purple-400 mb-4">Connect</h4>
              <div className="space-y-2">
                <a href="#" className="block text-gray-400 hover:text-purple-400 transition-colors">Twitter</a>
                <a href="#" className="block text-gray-400 hover:text-purple-400 transition-colors">GitHub</a>
                <a href="#" className="block text-gray-400 hover:text-purple-400 transition-colors">Discord</a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
