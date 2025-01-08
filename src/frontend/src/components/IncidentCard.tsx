import { useState } from 'react';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';
import type { Incident } from '../api/client';

dayjs.extend(relativeTime);

interface IncidentCardProps {
  incident: Incident;
}

const getStatusBadgeClass = (status: string) => {
  switch (status.toLowerCase()) {
    case 'ok':
      return 'status-badge status-ok';
    case 'minor':
      return 'status-badge status-minor';
    case 'major':
      return 'status-badge status-major';
    default:
      return 'status-badge bg-gray-800/50 text-gray-300 border border-gray-600/30';
  }
};

export const IncidentCard = ({ incident }: IncidentCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="card">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold text-white">
              {incident.incident.title}
            </h3>
            <span className={getStatusBadgeClass(incident.current_state)}>
              {incident.current_state}
            </span>
          </div>
          <p className="text-gray-400 mb-2">
            {incident.incident.description}
          </p>
          <div className="flex flex-wrap gap-2 mb-3">
            {incident.incident.components.map((component) => (
              <span
                key={component}
                className="px-2 py-1 bg-gray-800/50 text-gray-300 text-xs rounded-full
                         border border-purple-500/20"
              >
                {component}
              </span>
            ))}
          </div>
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="ml-4 p-1 hover:bg-gray-700/50 rounded-full transition-colors duration-300"
          aria-label={isExpanded ? "Collapse details" : "Expand details"}
        >
          {isExpanded ? (
            <ChevronUpIcon className="h-5 w-5 text-gray-400 hover:text-purple-400" />
          ) : (
            <ChevronDownIcon className="h-5 w-5 text-gray-400 hover:text-purple-400" />
          )}
        </button>
      </div>
      
      <div className="flex justify-between items-center text-sm text-gray-400">
        <span>{dayjs(incident.created_at).fromNow()}</span>
        <a
          href={incident.incident.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-purple-400 hover:text-purple-300 transition-colors duration-300"
        >
          View Details →
        </a>
      </div>

      {isExpanded && incident.history.length > 0 && (
        <div className="mt-4 pt-4 border-t border-purple-500/10">
          <h4 className="text-sm font-medium text-white mb-2">History</h4>
          <div className="space-y-2">
            {incident.history.map((entry) => (
              <div
                key={entry.id}
                className="flex items-center justify-between text-sm"
              >
                <div className="flex items-center gap-2">
                  <span className="text-gray-400">
                    {dayjs(entry.recorded_at).format('MMM D, YYYY HH:mm')}
                  </span>
                  <span className="text-gray-600">→</span>
                  <span className={getStatusBadgeClass(entry.current_state)}>
                    {entry.current_state}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};