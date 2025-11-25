import Link from 'next/link';
import { getRunData, getRunsIndex } from '@/lib/dataLoader';
import { formatDate, formatDuration, formatScore } from '@/lib/utils';
import { BenchmarkResultsTable } from '@/components/BenchmarkResultsTable';

interface PageProps {
  params: Promise<{ runId: string }>;
}

// Generate static paths for all runs
export async function generateStaticParams() {
  try {
    const index = await getRunsIndex();
    return index.runs.map((run) => ({
      runId: run.run_id,
    }));
  } catch (error) {
    console.error('Failed to generate static params:', error);
    return [];
  }
}

export default async function RunDetailPage({ params }: PageProps) {
  const { runId } = await params;

  let data;
  let error = null;

  try {
    data = await getRunData(runId);
  } catch (e) {
    error = e instanceof Error ? e.message : 'Failed to load run data';
  }

  if (error || !data) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-red-800 mb-2">
            Error Loading Run
          </h2>
          <p className="text-red-700">{error}</p>
          <Link href="/" className="text-blue-600 hover:underline mt-4 inline-block">
            ← Back to runs
          </Link>
        </div>
      </div>
    );
  }

  const { meta, summary } = data;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-6">
        <Link href="/" className="text-blue-600 hover:underline text-sm">
          ← Back to runs
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {meta.model.name}
            </h1>
            <p className="text-gray-500">{runId}</p>
          </div>
          <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
            {meta.status}
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
          <div>
            <p className="text-sm text-gray-500 mb-1">Framework</p>
            <p className="text-lg font-semibold text-gray-900">
              {meta.framework} {meta.framework_version}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500 mb-1">Model Type</p>
            <p className="text-lg font-semibold text-gray-900">
              {meta.model.type}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500 mb-1">Overall Score</p>
            <p className="text-lg font-semibold text-gray-900">
              {formatScore(summary.overall.avg_score)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500 mb-1">Total Samples</p>
            <p className="text-lg font-semibold text-gray-900">
              {summary.overall.total_samples.toLocaleString()}
            </p>
          </div>
        </div>

        <div className="border-t border-gray-200 pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Run Information
          </h3>
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <dt className="text-sm text-gray-500">Start Time</dt>
              <dd className="text-sm font-medium text-gray-900">
                {formatDate(meta.start_time)}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">End Time</dt>
              <dd className="text-sm font-medium text-gray-900">
                {formatDate(meta.end_time)}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Duration</dt>
              <dd className="text-sm font-medium text-gray-900">
                {formatDuration(meta.duration_seconds)}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Model Revision</dt>
              <dd className="text-sm font-medium text-gray-900">
                {meta.model.revision || 'N/A'}
              </dd>
            </div>
          </dl>
        </div>

        {meta.config && Object.keys(meta.config).length > 0 && (
          <div className="border-t border-gray-200 pt-6 mt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Configuration
            </h3>
            <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {meta.config.eval_batch_size && (
                <div>
                  <dt className="text-sm text-gray-500">Batch Size</dt>
                  <dd className="text-sm font-medium text-gray-900">
                    {meta.config.eval_batch_size}
                  </dd>
                </div>
              )}
              {meta.config.seed !== null && meta.config.seed !== undefined && (
                <div>
                  <dt className="text-sm text-gray-500">Seed</dt>
                  <dd className="text-sm font-medium text-gray-900">
                    {meta.config.seed}
                  </dd>
                </div>
              )}
            </dl>
          </div>
        )}
      </div>

      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Evaluation Results
        </h2>
        <BenchmarkResultsTable results={summary.datasets} />
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Sample Predictions
        </h2>
        <p className="text-gray-600 mb-4">
          View detailed sample predictions for each dataset
        </p>
        <div className="flex flex-wrap gap-3">
          {meta.datasets.map((dataset) => (
            <Link
              key={dataset}
              href={`/runs/${runId}/samples?dataset=${dataset}`}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              View {dataset} samples
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
