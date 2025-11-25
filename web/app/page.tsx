import Link from 'next/link';
import { getRunsIndex } from '@/lib/dataLoader';
import { formatDate, formatDuration, formatScore } from '@/lib/utils';

export default async function Home() {
  let runsIndex;
  let error = null;

  try {
    runsIndex = await getRunsIndex();
  } catch (e) {
    error = e instanceof Error ? e.message : 'Failed to load runs';
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-yellow-800 mb-2">
            No Data Available
          </h2>
          <p className="text-yellow-700 mb-4">
            No evaluation runs found. Please run the ETL script to generate data:
          </p>
          <pre className="bg-yellow-100 text-yellow-900 p-4 rounded overflow-x-auto text-sm">
            python tools/etl/build_static_data.py \<br />
            {'  '}--framework evalscope \<br />
            {'  '}--raw-dir ./outputs \<br />
            {'  '}--out-dir ./web/public/data
          </pre>
        </div>
      </div>
    );
  }

  const runs = runsIndex?.runs || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Evaluation Runs
        </h1>
        <p className="text-gray-600">
          {runs.length} run{runs.length !== 1 ? 's' : ''} found
          {runsIndex?.last_updated && (
            <span className="ml-2 text-sm">
              (Updated: {formatDate(runsIndex.last_updated)})
            </span>
          )}
        </p>
      </div>

      {runs.length === 0 ? (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-12 text-center">
          <p className="text-gray-500">No evaluation runs available</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {runs.map((run) => (
            <Link
              key={run.run_id}
              href={`/runs/${run.run_id}`}
              className="block bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {run.model.name}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {run.run_id}
                  </p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                    run.status === 'completed'
                      ? 'bg-green-100 text-green-800'
                      : run.status === 'failed'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {run.status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-500">Framework</p>
                  <p className="text-sm font-medium text-gray-900">
                    {run.framework}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Model Type</p>
                  <p className="text-sm font-medium text-gray-900">
                    {run.model.type}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Overall Score</p>
                  <p className="text-sm font-medium text-gray-900">
                    {formatScore(run.overall_score)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Duration</p>
                  <p className="text-sm font-medium text-gray-900">
                    {formatDuration(run.duration_seconds)}
                  </p>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-4">
                <p className="text-sm text-gray-500 mb-2">Datasets</p>
                <div className="flex flex-wrap gap-2">
                  {run.datasets.map((dataset) => (
                    <span
                      key={dataset}
                      className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded"
                    >
                      {dataset}
                    </span>
                  ))}
                </div>
              </div>

              <div className="mt-4 text-xs text-gray-400">
                {formatDate(run.start_time)}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
