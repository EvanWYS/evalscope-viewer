'use client';

import { Sample } from '@/lib/types';
import { formatScore } from '@/lib/utils';
import { useState, Fragment } from 'react';

interface Props {
  samples: Sample[];
}

export function SamplesTable({ samples }: Props) {
  const [expandedSamples, setExpandedSamples] = useState<Set<string | number>>(
    new Set()
  );

  const toggleSample = (id: string | number) => {
    const newExpanded = new Set(expandedSamples);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedSamples(newExpanded);
  };

  const renderValue = (value: any): string => {
    if (typeof value === 'string') return value;
    if (Array.isArray(value)) return value.join(', ');
    if (typeof value === 'object' && value !== null) {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  };

  const truncateText = (text: string, maxLength: number = 100): string => {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
  };

  if (samples.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
        No samples available
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Input
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Target
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Prediction
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Scores
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {samples.map((sample) => {
              const isExpanded = expandedSamples.has(sample.id);
              const inputText = renderValue(sample.input);
              const targetText = renderValue(sample.target);
              const predictionText = renderValue(sample.prediction);

              return (
                <Fragment key={sample.id}>
                  <tr className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {sample.id}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="max-w-xs">
                        {isExpanded ? inputText : truncateText(inputText)}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="max-w-xs">
                        {isExpanded ? targetText : truncateText(targetText)}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="max-w-xs">
                        {isExpanded
                          ? predictionText
                          : truncateText(predictionText)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {Object.entries(sample.scores).map(([key, value]) => (
                        <div key={key} className="mb-1">
                          <span className="text-gray-500">{key}:</span>{' '}
                          <span className="font-medium text-gray-900">
                            {formatScore(value)}
                          </span>
                        </div>
                      ))}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => toggleSample(sample.id)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        {isExpanded ? 'Collapse' : 'Expand'}
                      </button>
                    </td>
                  </tr>
                  {isExpanded && (
                    <tr key={`${sample.id}-details`}>
                      <td colSpan={6} className="px-6 py-4 bg-gray-50">
                        <div className="space-y-4">
                          {sample.choices && sample.choices.length > 0 && (
                            <div>
                              <h4 className="text-sm font-semibold text-gray-700 mb-2">
                                Choices
                              </h4>
                              <ul className="list-disc list-inside text-sm text-gray-900">
                                {sample.choices.map((choice, idx) => (
                                  <li key={idx}>{choice}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {sample.metadata &&
                            Object.keys(sample.metadata).length > 0 && (
                              <div>
                                <h4 className="text-sm font-semibold text-gray-700 mb-2">
                                  Metadata
                                </h4>
                                <pre className="text-xs text-gray-900 bg-white p-3 rounded border border-gray-200 overflow-x-auto">
                                  {JSON.stringify(sample.metadata, null, 2)}
                                </pre>
                              </div>
                            )}
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
