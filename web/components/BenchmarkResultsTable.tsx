'use client';

import { BenchmarkResult } from '@/lib/types';
import { formatScore } from '@/lib/utils';
import { useState } from 'react';

interface Props {
  results: BenchmarkResult[];
}

export function BenchmarkResultsTable({ results }: Props) {
  const [expandedDatasets, setExpandedDatasets] = useState<Set<string>>(
    new Set()
  );

  const toggleDataset = (dataset: string) => {
    const newExpanded = new Set(expandedDatasets);
    if (newExpanded.has(dataset)) {
      newExpanded.delete(dataset);
    } else {
      newExpanded.add(dataset);
    }
    setExpandedDatasets(newExpanded);
  };

  if (results.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
        No evaluation results available
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {results.map((result) => {
        const isExpanded = expandedDatasets.has(result.dataset);
        const primaryMetric = Object.keys(result.metrics)[0];

        return (
          <div key={result.dataset} className="bg-white rounded-lg shadow">
            <button
              onClick={() => toggleDataset(result.dataset)}
              className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center space-x-4">
                <div className="text-left">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {result.dataset_pretty_name || result.dataset}
                  </h3>
                  <p className="text-sm text-gray-500">{result.dataset}</p>
                </div>
              </div>
              <div className="flex items-center space-x-6">
                <div className="text-right">
                  <p className="text-sm text-gray-500">Overall Score</p>
                  <p className="text-xl font-bold text-gray-900">
                    {formatScore(result.overall_score)}
                  </p>
                </div>
                <svg
                  className={`w-5 h-5 text-gray-400 transition-transform ${
                    isExpanded ? 'transform rotate-180' : ''
                  }`}
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M19 9l-7 7-7-7"></path>
                </svg>
              </div>
            </button>

            {isExpanded && (
              <div className="px-6 pb-6 border-t border-gray-200">
                <div className="mt-4">
                  <h4 className="text-sm font-semibold text-gray-700 mb-3">
                    Metrics
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    {Object.entries(result.metrics).map(([name, metric]) => (
                      <div key={name} className="bg-gray-50 p-4 rounded">
                        <p className="text-sm text-gray-600 mb-1">{name}</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {formatScore(metric.score)}
                        </p>
                        {metric.macro_score !== undefined && (
                          <p className="text-xs text-gray-500 mt-1">
                            Macro: {formatScore(metric.macro_score)}
                          </p>
                        )}
                        <p className="text-xs text-gray-500 mt-1">
                          {metric.num_samples.toLocaleString()} samples
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {result.categories && result.categories.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-3">
                      Category Breakdown
                    </h4>
                    <div className="space-y-4">
                      {result.categories.map((category, idx) => (
                        <div key={idx} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-3">
                            <h5 className="font-medium text-gray-900">
                              {category.name.join(' > ')}
                            </h5>
                            <span className="text-sm font-semibold text-gray-900">
                              {formatScore(category.score)}
                            </span>
                          </div>
                          {category.subsets && category.subsets.length > 0 && (
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                              {category.subsets.map((subset) => (
                                <div
                                  key={subset.name}
                                  className="bg-gray-50 p-2 rounded text-sm"
                                >
                                  <p className="text-gray-700 truncate" title={subset.name}>
                                    {subset.name}
                                  </p>
                                  <p className="font-semibold text-gray-900">
                                    {formatScore(subset.score)}
                                  </p>
                                  <p className="text-xs text-gray-500">
                                    n={subset.num}
                                  </p>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
